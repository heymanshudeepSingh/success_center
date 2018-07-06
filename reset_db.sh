
# Abort on error
set -e

# Remove migrations
rm -f apps/cae_home/migrations/0*.py
rm -f apps/CAE_Web/cae_web_core/migrations/0*.py
rm -f apps/CAE_Web/cae_web_autio_visual/migrations/0*.py

# Remove db
rm -f db.sqlite3

# Activate venv
. .venv/bin/activate

# Recreate migrations
python ./manage.py makemigrations

# Migrate
python ./manage.py migrate

# Load example data
python ./manage.py loaddata users
python ./manage.py loaddata calendars
