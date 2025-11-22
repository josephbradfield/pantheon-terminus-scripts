# Pantheon Site Scripts

This directory contains scripts for fetching and processing information about Pantheon sites.

## Scripts
 
### `fetch_pantheon_sites.sh`

This script fetches a list of all Pantheon sites associated with the authenticated user and saves the output to a file named `pantheon-sites.json` in the same directory.

**Dependencies:**
- [Terminus](https://pantheon.io/docs/terminus)

**Usage:**
```bash
./fetch_pantheon_sites.sh
```

### `process_pantheon_sites.py`

This script processes a JSON file containing a list of Pantheon sites, filters for sites on the "Basic" plan, and fetches the domains for each of those sites.

**Features:**
- Removes hard-coded paths for portability.
- Accepts a command-line argument for the input file path.
- If no input file is provided, it defaults to looking for `pantheon-domains.json` in the script's directory.
- If the default file is not found, it will run the `fetch_pantheon_sites.sh` script to generate it.

**Dependencies:**
- Python 3
- [Terminus](https://pantheon.io/docs/terminus)

**Usage:**

To run the script with the default behavior (using `pantheon-domains.json` or generating it):
```bash
python process_pantheon_sites.py
```

To specify an input file:
```bash
python process_pantheon_sites.py /path/to/your/sites.json
```

**Note:** your file needs to be formatted like so  
```json
"055ac97f-ec08-4457-be93-9feae1eb45aa": {
        "name": "ucr-pantheonsitename",
        "id": "055ac97f-ec08-4457-be93-9feae1eb45aa",
        "plan_name": "Basic",
        "framework": "drupal8",
        "region": "United States",
        "owner": "d5bc99d7-58d8-4de2-96bf-d29681afc848",
        "created": 1652824950,
        "memberships": "043b424f-9618-4043-bfd6-f666755df151: Team",
        "frozen": false
    },
```
