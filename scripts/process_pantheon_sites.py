
import json
import subprocess
import os
import ast
import re
import time
from math import ceil
import sys

def get_script_dir():
    """Gets the directory where the script is running."""
    return os.path.dirname(os.path.abspath(__file__))

def process_pantheon_sites(input_file=None):
    """
    Reads pantheon-sites.json, filters for "Basic" plans,
    and fetches domain information for each site.
    """
    script_dir = get_script_dir()

    if input_file is None:
        # If no input file is provided, default to 'pantheon-domains.json' in the script's directory
        input_file = os.path.join(script_dir, 'pantheon-domains.json')
        # Check if the default file exists
        if not os.path.exists(input_file):
            print(f"Default file {input_file} not found. Running script to generate it...")
            try:
                # Assumes the generation script is in the same directory
                generation_script = os.path.join(script_dir, 'fetch_pantheon_sites.sh')
                subprocess.run(['bash', generation_script], check=True)
                print("File generation script executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error running generation script: {e}")
                return
            except FileNotFoundError:
                print(f"Generation script not found at {generation_script}")
                return

    output_dir = os.path.join(script_dir, '..', 'output')
    output_file = os.path.join(output_dir, 'pantheon-domains.json')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_domains = {}

    sites = None

    if os.path.exists(input_file):
        try:
            with open(input_file, 'r') as f:
                sites = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing {input_file}: {e}")
            sites = None
    else:
        # If the input file doesn't exist, fall back to `terminus site:list`
        try:
            result = subprocess.run(
                ['terminus', 'site:list', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            sites = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error running terminus site:list: {e}")
            print(f"Stderr: {e.stderr}")
            return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from terminus site:list: {e}")
            return

    if sites is None:
        print("No site data available from file or terminus.")
        return

    # Normalize a list of site objects into a dict keyed by site id/name
    if isinstance(sites, list):
        sites_dict = {}
        for s in sites:
            if not isinstance(s, dict):
                continue
            key = s.get('id') or s.get('uuid') or s.get('name') or s.get('site')
            if not key:
                # try to find any unique-ish value
                for candidate in ('id', 'uuid', 'name', 'site'):
                    if candidate in s:
                        key = s[candidate]
                        break
            if not key:
                continue
            sites_dict[key] = s
        sites = sites_dict

    # Only process Basic plan sites (also allow 'plan' key from terminus)
    def is_basic(si):
        if not isinstance(si, dict):
            return False
        pn = si.get('plan_name') or si.get('plan') or ''
        return str(pn).lower() == 'basic'

    # Parameters for batching and timeouts
    BATCH_SIZE = 10
    CALL_TIMEOUT = 20  # seconds per terminus call
    SLEEP_BETWEEN_BATCHES = 0.5

    # Filter sites first into a list to batch over
    site_items = [(sid, sinfo) for sid, sinfo in sites.items() if is_basic(sinfo)]
    total = len(site_items)
    if total == 0:
        print("No Basic-plan sites to process.")
    batches = ceil(total / BATCH_SIZE) if total else 0

    for batch_idx in range(batches):
        start = batch_idx * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = site_items[start:end]
        print(f"Processing batch {batch_idx+1}/{batches} ({len(batch)} sites)")

        for i, (site_id, site_info) in enumerate(batch, start=start+1):
            print(f"[{i}/{total}] Processing site {site_id} ({site_info.get('name')})")
            command = [
                'terminus',
                'domain:list',
                f'{site_id}.live',
                '--format',
                'json',
                "--filter=type!=platform"
            ]
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=CALL_TIMEOUT,
                )
                domains_raw = json.loads(result.stdout)
                domains_raw = json.loads(result.stdout)

                # Normalize domains into a list of domain strings
                def extract_hostname_from_string(s):
                    # Try JSON first (handles double-quoted JSON strings)
                    try:
                        parsed = json.loads(s)
                        if isinstance(parsed, dict):
                            return parsed.get('id') or parsed.get('name') or parsed.get('domain') or parsed.get('hostname')
                        if isinstance(parsed, list) and parsed:
                            first = parsed[0]
                            if isinstance(first, dict):
                                return first.get('id') or first.get('name') or first.get('domain') or first.get('hostname')
                    except Exception:
                        pass

                    # Try Python literal eval (handles single-quoted dicts like "{'id': 'example.com', ...}")
                    try:
                        parsed = ast.literal_eval(s)
                        if isinstance(parsed, dict):
                            return parsed.get('id') or parsed.get('name') or parsed.get('domain') or parsed.get('hostname')
                        if isinstance(parsed, (list, tuple)) and parsed:
                            first = parsed[0]
                            if isinstance(first, dict):
                                return first.get('id') or first.get('name') or first.get('domain') or first.get('hostname')
                    except Exception:
                        pass

                    # Regex fallback: look for an 'id' key then a hostname pattern
                    m = re.search(r"['\"]?id['\"]?\s*:\s*['\"]([^'\"]+)['\"]", s)
                    if m:
                        return m.group(1)

                    # Generic hostname fallback (grab first domain-like token)
                    m2 = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", s)
                    if m2:
                        return m2.group(1)

                    return None

                normalized_domains = []
                if isinstance(domains_raw, dict):
                    for v in domains_raw.values():
                        if isinstance(v, str):
                            host = extract_hostname_from_string(v)
                            normalized_domains.append(host or v)
                        elif isinstance(v, dict):
                            normalized_domains.append(
                                v.get('id') or v.get('name') or v.get('domain') or v.get('hostname') or str(v)
                            )
                elif isinstance(domains_raw, list):
                    for item in domains_raw:
                        if isinstance(item, str):
                            host = extract_hostname_from_string(item)
                            normalized_domains.append(host or item)
                        elif isinstance(item, dict):
                            normalized_domains.append(
                                item.get('id') or item.get('name') or item.get('domain') or item.get('hostname') or str(item)
                            )
                elif domains_raw is not None:
                    if isinstance(domains_raw, str):
                        host = extract_hostname_from_string(domains_raw)
                        normalized_domains.append(host or domains_raw)
                    else:
                        normalized_domains.append(str(domains_raw))

                # Deduplicate and remove None/empty values while preserving order
                seen = set()
                deduped = []
                for d in normalized_domains:
                    if not d:
                        continue
                    if d in seen:
                        continue
                    seen.add(d)
                    deduped.append(d)

                site_entry = {
                    'name': site_info.get('name'),
                    'domains': deduped,
                }

                all_domains[site_id] = site_entry

            except subprocess.TimeoutExpired as e:
                print(f"Timeout ({CALL_TIMEOUT}s) while running terminus for site {site_id}")
                all_domains[site_id] = {
                    'name': site_info.get('name'),
                    'domains': [],
                    'error': f'timeout_after_{CALL_TIMEOUT}s'
                }
            except subprocess.CalledProcessError as e:
                print(f"Error running terminus for site {site_id}: {e}")
                print(f"Stderr: {e.stderr}")
                all_domains[site_id] = {
                    'name': site_info.get('name'),
                    'domains': [],
                    'error': 'terminus_failed'
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from terminus for site {site_id}: {e}")
                all_domains[site_id] = {
                    'name': site_info.get('name'),
                    'domains': [],
                    'error': 'json_parse_error'
                }

            # Incrementally write output to file so progress is saved
            try:
                with open(output_file, 'w') as f:
                    json.dump(all_domains, f, indent=4)
            except IOError as e:
                print(f"Error writing to {output_file}: {e}")

        # End of batch
        if batch_idx < batches - 1:
            time.sleep(SLEEP_BETWEEN_BATCHES)


    try:
        with open(output_file, 'w') as f:
            json.dump(all_domains, f, indent=4)
        print(f"Successfully wrote domains to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == '__main__':
    # Check if a command-line argument is provided
    if len(sys.argv) > 1:
        process_pantheon_sites(sys.argv[1])
    else:
        process_pantheon_sites()
