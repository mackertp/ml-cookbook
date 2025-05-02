#!/bin/bash

# Get the directory where the shell script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the 'sip' directory inside the script's folder
cd "$SCRIPT_DIR/"

# run something, like an application, in your directory
# ...