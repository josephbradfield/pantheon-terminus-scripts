#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
terminus site:list --format json > "$SCRIPT_DIR/../output/pantheon-sites.json"
