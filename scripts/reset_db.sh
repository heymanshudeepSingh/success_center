#!/bin/bash
# Script to reset database, including fresh migrations.
# Currently only works with sqlite databases.


# Abort on error
set -e


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")"


function main () {
    # Remove migrations.
    ./reset_migrations.sh force

    # Remove sqlite database if present.
    rm -f ../db.sqlite3

    # Activate venv if present.
    if [[ -d "../.venv" ]]
    then
        . ../.venv/bin/activate
    fi

    # Recreate migrations.
    echo ""
    echo "Creating migrations..."
    python ../manage.py makemigrations
    echo ""
    echo ""

    # Migrate.
    echo "Migrating to database..."
    python ../manage.py migrate
    echo ""
    echo ""

    # Create seeded data.
    echo "Seeding data..."
    python ../manage.py seed --traceback
    echo ""

    echo ""
    echo "Database reset and reseeded. Terminating script."
}


# Warn user with prompt. Skips if arg of "force" was provided.
if [[ $1 != "force" ]]
then
    echo ""
    echo "Note: This will remove all migrations in CAE_Workspace, including ones in the apps subfolders."
    echo "      This script probably shouldn't be run in production environments."
    echo "      Only proceed if you know what you are doing."
    echo ""
    read -p "Are you sure you want to DELETE AND RESET? (y/N) " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then # Only run if y is pressed.
        echo "" # Move to newline
        main
    fi
    exit
fi
