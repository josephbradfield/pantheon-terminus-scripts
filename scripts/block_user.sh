#!/bin/bash

# Default sites file path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SITES_FILE="$SCRIPT_DIR/../output/pantheon-sites.json"
USERNAMES=()

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    key="$1"
    case $key in
        --source)
        SITES_FILE="$2"
        shift # past argument
        shift # past value
        ;;
        *)    # unknown option
        USERNAMES+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done

# Check if at least one username is provided
if [ "${#USERNAMES[@]}" -eq 0 ]; then
  echo "Usage: $0 [--source <sites_file>] <username1> [username2] ..."
  exit 1
fi

# Check if the sites file exists
if [ ! -f "$SITES_FILE" ]; then
  echo "Error: Sites file not found at $SITES_FILE"
  exit 1
fi

# Read site names into an array to avoid parsing the JSON file multiple times
mapfile -t SITES < <(jq -r '.[].name' "$SITES_FILE")

# Loop over each username provided as a command-line argument
for USERNAME in "${USERNAMES[@]}"; do
  echo "--- Processing user: $USERNAME ---"
  # Loop over each site from the array
  for sitename in "${SITES[@]}"; do
    if [ -n "$sitename" ]; then
      echo "Blocking user '$USERNAME' on site '$sitename'..."
      terminus drush "$sitename.live" -- user:block "$USERNAME"
    fi
  done
done

echo "All users and sites processed."