"""
Extra settings for project, including logging and importing of local environment.
"""

# System Imports.
from django.utils.crypto import get_random_string
import logging.config, string

# User Class Imports.
from settings.reusable_settings import *


# Set up logging directories.
log_dir = os.path.join(BASE_DIR, 'settings/local_env/logs/')
try:
    os.makedirs(log_dir)
    debug_print('Logging folder created.')
except FileExistsError:
    debug_print('Logging folder found.')

# Set up logging configuration.
LOGGING = {
    'version': 1,
    'formatters': {
        # Simple logging. Includes message type and actual message.
        'simple': {
            'format': '[%(levelname)s]: %(message)s',
        },
        # Basic logging. Includes date, message type, file originated, and actual message.
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        # Verbose logging. Includes standard plus the process number and thread id.
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s || %(process)d %(thread)d || %(message)s',
        },
    },
    'handlers': {
        # Sends log message to the void. May be useful for debugging.
        'null': {
            'class': 'logging.NullHandler',
        },
        # To console.
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # Debug level - To file.
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'debug.log'),
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
            'formatter': 'standard',
        },
        # Info level - To file.
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'info.log'),
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
            'formatter': 'standard',
        },
        # Warn level - To file.
        'file_warn': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'warn.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        # Error level - To file.
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'error.log'),
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        # Error level - To admin email.
        'mail_error': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        # All basic logging to console/log files.
        '': {
            'handlers': ['console', 'file_info', 'file_warn', 'file_error'],
            'level': 'INFO',
            'propagate': True,
        },
        # Request logging.
        'django.request': {
            'handlers': ['console', 'file_warn', 'file_error'],
            'level': 'WARNING',
            'propagate': True,
        },
        # Logging to admin email.
        # TODO: Set up error emailing.
    },
}


# Initialize logging.
LOGGING_CONFIG = None # Prevent django from initializing logging again
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


# Check for secret key.
path_to_key = os.path.join(BASE_DIR, './settings/local_env/secret_key.txt')

try:
    # Attempt to read key.
    SECRET_KEY = open(path_to_key, 'r').read().strip()
    debug_print('Secret Key Found.')
except:
    try:
        # Generate new key.
        debug_print('Creating Secret Key...')
        allowed_chars = string.ascii_letters + string.digits
        SECRET_KEY = get_random_string(50, allowed_chars)
        debug_print('Secret Key created.')

        # Save key to file.
        secret_file = open(path_to_key, 'w+')
        secret_file.write(SECRET_KEY)
        secret_file.close()
        debug_print('Secret Key saved.')
    except:
        debug_print('Error generating secret key.')
        exit(1)


# Login url.
LOGIN_REDIRECT_URL = '/'


# from settings.local_env.env import *

# Local environment setup.
try:
    from settings.local_env.env import *
    if DEBUG:
        debug_print('Successfully imported {0}development{1} environment settings.'
                    .format(ConsoleColors.bold_blue, ConsoleColors.reset))
    else:
        debug_print('Successfully imported {0}production{1} environment settings.'
                    .format(ConsoleColors.bold_blue, ConsoleColors.reset))
except Exception:
    debug_print('Missing or Invalid local env file. Copy the env_example.py file to env.py in settings/local_env/')
    debug_print(sys.exc_info())
    sys.exit(1)
