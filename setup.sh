#!/bin/bash

# ======= Configuration Section =======
# Change these values to suit your application
# ====================================

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your virtual environment before running setup.sh"
    exit 1
fi

# Directory where the script resides
BASE_DIR=$(dirname "$0")

echo "Initializing the database..."
psql  -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
psql  -U "$DB_USER" -d "$DB_NAME" -f "$BASE_DIR/db/create.sql"


echo "Setup complete!"
