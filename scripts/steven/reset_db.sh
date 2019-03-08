#!/bin/bash
# Script to reset database, including fresh migrations.
# Specifically does not seed database. Only loads in Steven's migrations.


# Abort on error
set -e


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")"

# Remove migrations
rm -f ../../cae_home/migrations/0*.py
rm -f ../../apps/CAE_Web/cae_web_core/migrations/0*.py
rm -f ../../apps/CAE_Web/cae_web_autio_visual/migrations/0*.py

# Remove db
rm -f ../../db.sqlite3

# Activate venv
#. ../../.venv/bin/activate

# Recreate migrations
python ../../manage.py makemigrations

# Migrate
python ../../manage.py migrate

# Load example data
python ../../manage.py loaddata full_models/site_themes.json
python ../../manage.py loaddata users
python ../../manage.py loaddata room_types
python ../../manage.py loaddata rooms

# Load CAE_Web data if installed
if [ -d ../../apps/CAE_Web ]; then
    echo "Loading CAE_Web Fixtures..."
    python ../../manage.py loaddata calendars
    python ../../manage.py loaddata room_events
else
    echo "CAE_Web not found. Not loading its fixtures."
fi
