"""
Extra (universal) settings for Django project.

These are generally custom or optional settings (as in not necessarily mandatory to Django or installed Libraries).
Settings here will generally stay the same, regardless of Project installation.

For settings that are likely to change based on Project installation, see "settings/local_env/env.py".
"""

# System Imports.
import string
from django.utils.crypto import get_random_string

# User Class Imports.
from settings import logging as init_logging
from settings.reusable_settings import *


# Check for local environment setup.
try:
    from env import *
except Exception:
    debug_print('Missing or Invalid local env file. Please Copy the env_example.py file from settings/local_env/')
    debug_print(sys.exc_info())
    sys.exit(1)


#region Secret Key Settings

# Check for secret key.
path_to_key = os.path.join(BASE_DIR, './settings/local_env/secret_key.txt')

try:
    # Attempt to read key.
    secret_key_file = open(path_to_key, 'r')
    SECRET_KEY = secret_key_file.read().strip()
    secret_key_file.close()
    debug_print('Secret Key Found.')
except FileNotFoundError:
    try:
        # Generate new key.
        debug_print('Creating Secret Key...')
        allowed_chars = string.ascii_letters + string.digits
        SECRET_KEY = get_random_string(50, allowed_chars)
        debug_print('Secret Key created.')

        # Save key to file.
        secret_key_file = open(path_to_key, 'w+')
        secret_key_file.write(SECRET_KEY)
        secret_key_file.close()

        debug_print('Secret Key saved.')
    except:
        debug_print('Error generating secret key.')
        exit(1)

#endregion Secret Key Settings


# Setup logging.
init_logging.get_logger(__name__, LOGGING_DIRECTORY)


#region Url Redirection Settings

LOGIN_URL = '/user/login/'
LOGIN_REDIRECT_URL = '/user/login_redirect/'
LOGOUT_REDIRECT_URL = LOGIN_URL

#endregion Url Redirection Settings


#region Environment Values

# Local environment setup.
if DEBUG:
    debug_print('Successfully imported {0}development{1} environment settings.'
                .format(ConsoleColors.bold_blue, ConsoleColors.reset))
else:
    debug_print('Successfully imported {0}production{1} environment settings.'
                .format(ConsoleColors.bold_blue, ConsoleColors.reset))


# Set custom debug variable aliases, based on DEBUG.
# Necessary for unit testing, or else tests referring to development urls will automatically fail.
# DEBUG may potentially have other unexpected logic set by Django, in the future.
# Thus setting a custom equivalent here saves potential future headache.
# This value is effectively a custom variable that's equivalent to DEBUG, but minus the extra logic Django provides.
if DEBUG:
    DEV_URLS = True
    DEV_MODE = True
    DEBUG_MODE = True
    PROD_MODE = False
else:
    DEV_URLS = False
    DEV_MODE = False
    DEBUG_MODE = False
    PROD_MODE = True

#endregion Environment Values


#region Third Party Library Settings

# django-phonenumber-field settings
PHONENUMBER_DEFAULT_REGION = 'US'   # Don't require users to prefix with +1

#endregion Third Party Library Settings
