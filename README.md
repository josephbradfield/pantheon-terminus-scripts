# Pantheon Site Scripts

This directory contains scripts for fetching and processing information about Pantheon sites.

## Scripts

### `scripts/fetch_pantheon_sites.sh`

This script fetches a list of all Pantheon sites associated with the authenticated user and saves the output to `output/pantheon-sites.json`.

**Dependencies:**
- [Terminus](https://pantheon.io/docs/terminus)

**Usage:**
```bash
./scripts/fetch_pantheon_sites.sh
```

### `scripts/process_pantheon_sites.py`

This script processes `output/pantheon-sites.json`, filters for sites on the "Basic" plan, and fetches the domains for each of those sites, saving the result to `output/pantheon-domains.json`.

**Features:**
- If `output/pantheon-sites.json` is not found, it will run the `fetch_pantheon_sites.sh` script to generate it.
- You can also provide a path to a different site list file as a command-line argument.

**Dependencies:**
- Python 3
- [Terminus](https://pantheon.io/docs/terminus)

**Usage:**

To run the script with the default behavior:
```bash
python scripts/process_pantheon_sites.py
```

To specify an input file:
```bash
python scripts/process_pantheon_sites.py /path/to/your/sites.json
```

### `scripts/parse_domains.py`

This script reads `output/pantheon-domains.json`, extracts all domains, and writes them to `output/drupal_domains.csv` with `name` and `domain` columns.

**Dependencies:**
- Python 3

**Usage:**
```bash
python scripts/parse_domains.py
```

### `scripts/block_user.sh`

This script blocks one or more user accounts on a list of Pantheon sites.

**Features:**
- By default, it reads the site list from `output/pantheon-sites.json`.
- You can specify a different site list file using the `--source` flag.

**Dependencies:**
- [Terminus](https://pantheon.io/docs/terminus)
- [jq](https://stedolan.github.io/jq/)

**Usage:**

To block one user:
```bash
./scripts/block_user.sh <username>
```

To block multiple users:
```bash
./scripts/block_user.sh <username1> <username2>
```

To use a custom site list:
```bash
./scripts/block_user.sh --source /path/to/sites.json <username>
```