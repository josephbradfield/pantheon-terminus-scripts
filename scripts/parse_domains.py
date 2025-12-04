
import json
import os
import csv

def get_script_dir():
    """Gets the directory where the script is running."""
    return os.path.dirname(os.path.abspath(__file__))

def parse_domains():
    """
    Reads pantheon-domains.json, extracts all domains,
    and writes them to a new CSV file with site name and domain.
    """
    script_dir = get_script_dir()
    input_file = os.path.join(script_dir, '..', 'output', 'pantheon-domains.json')
    output_file = os.path.join(script_dir, '..', 'output', 'drupal_domains.csv')

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {input_file}: {e}")
        return

    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'domain'])  # Write header
            for site_id, site_info in data.items():
                if 'domains' in site_info and isinstance(site_info['domains'], list):
                    site_name = site_info.get('name', '')
                    for domain in site_info['domains']:
                        writer.writerow([site_name, domain])
        print(f"Successfully wrote domains to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == '__main__':
    parse_domains()
