#!/bin/bash

# Make logger.py executable
chmod 700 logger.py

# Make script.sh executable
chmod 700 script.sh

echo "Permissions set to 700 for logger.py and script.sh."

echo "Running ./script.sh file to check Error logs"

./script.sh