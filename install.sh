#!/bin/bash

# Set the base directory and change to it
mybase=`dirname "$mypath"`
cd $mybase

# Load environment variables from .flaskenv file if it exists
if [ -f ".flaskenv" ]; then
    echo "Loading environment variables from .flaskenv file..."
    source .flaskenv
else
    echo ".flaskenv file not found. Exiting."
    exit 1
fi

# Ensure all the necessary environment variables are set
if [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_NAME" ] ; then
    echo "One or more required environment variables are missing in .flaskenv."
    exit 1
fi

# Generate secret key if not provided
if ! grep -q "^SECRET_KEY=" .flaskenv; then
    echo "SECRET_KEY not found in .flaskenv. Generating a new one..."
    SECRET=$(LC_CTYPE=C tr -dc 'a-z0-9' < /dev/urandom | head -c50)
    echo "" >> .flaskenv  # Ensure there is a newline
    echo "SECRET_KEY=\"$SECRET\"" >> .flaskenv
    echo "SECRET_KEY=$SECRET written to .flaskenv"
else
    echo "SECRET_KEY already exists in .flaskenv."
fi


# Export other environment variables
export FLASK_APP="main.py"
export FLASK_DEBUG="True"
export FLASK_RUN_HOST="0.0.0.0"
export FLASK_RUN_PORT="8080"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install PostgreSQL if it's not already installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found. Installing PostgreSQL..."
    brew install postgresql
    brew services start postgresql
else
    echo "PostgreSQL is already installed."
fi

# Create PostgreSQL user and database
echo "Creating PostgreSQL user and database..."
psql -U $DB_USER -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
psql -U $DB_USER -d postgres -c "ALTER USER $DB_USER WITH SUPERUSER;"
psql -U $DB_USER -d postgres -c "SELECT 1 FROM pg_catalog.pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || psql -U noah -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Reset pg_hba.conf to require password authentication if needed
if [ -f "$POSTGRES_CONF" ]; then
    echo "Reverting pg_hba.conf to require password authentication..."
    mv "$POSTGRES_CONF.bak" "$POSTGRES_CONF"
    brew services restart postgresql
fi

# Run setup script
source ./setup.sh

# Configure poetry and install dependencies
poetry config virtualenvs.in-project true
poetry install

echo "Installation and setup complete!"
