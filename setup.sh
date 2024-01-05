#!/bin/bash

# Get working dirs
WORKING_DIR="$(dirname "$(readlink -f "$0")")"
SQLITE_DIR="$(which sqlite3)"

# Check if sqlite is installed otherwise exit
if [[ -z "$SQLITE_DIR" ]]
then
    echo "Please install sqlite3 on this device."
    exit
fi

# Remove any old database files
if [[ -e "$WORKING_DIR/database/website_database.db" ]]
then
    echo "Clearing old database file."
    rm "$WORKING_DIR/database/website_database.db"
fi

# Setup and populate data
echo "Creating random data."
eval "$WORKING_DIR/venv/bin/python3.10 ./database/setup/populate_data.py"

echo "Setting up Sqlite database."
sqlite3 ./database/website_database.db < ./database/setup/setup_database.sql

echo "Importing data."
sqlite3 ./database/website_database.db < ./database/setup/import_data_p1.sql
eval "$WORKING_DIR/venv/bin/python3.10 ./database/setup/import_data_p2.py"
sqlite3 ./database/website_database.db < ./database/setup/import_data_p3.sql

echo "Setup complete."

# TODO
# 1. Check sqlite version (min 3.44)