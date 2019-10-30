"""
Extra (universal) settings for Django project.

These are generally custom or optional settings (as in not necessarily mandatory to Django or installed Libraries).
Settings here will generally stay the same, regardless of Project installation.

For settings that are likely to change based on Project installation, see "settings/local_env/env.py".
"""

# System Imports.
from django.utils.crypto import get_random_string
import logging.config, string

# User Class Imports.
from settings.reusable_settings import *


# Check for local environment setup.
try:
    from settings.local_env.env import *
except Exception:
    debug_print('Missing or Invalid local env file. Copy the env_example.py file to env.py in settings/local_env/')
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


#region Logging Settings

# Set up logging directories.
debug_log_dir = os.path.join(LOGGING_DIRECTORY, 'debug/')
sql_log_dir = os.path.join(LOGGING_DIRECTORY, 'sql/')
# Make sure logging directories exist.
try:
    os.makedirs(LOGGING_DIRECTORY)
    os.makedirs(debug_log_dir)
    os.makedirs(sql_log_dir)
except FileExistsError:
    # Root logging directory exists. Attempt sub directories.
    try:
        # Debug directory.
        os.makedirs(debug_log_dir)
    except FileExistsError:
        pass    # Debug log dir already exists. This is fine.
    try:
        # SQL directory.
        os.makedirs(sql_log_dir)
    except FileExistsError:
        pass    # SQL log dir already exists. This is fine.
debug_print('{0}Logging folder{1}: {2}'.format(ConsoleColors.bold_blue, ConsoleColors.reset, LOGGING_DIRECTORY))


# Logic to filter logs based on logging level.
class _ExcludeWarningsFilter(logging.Filter):
    """
    Class to filter out any messages higher than log level 30.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """Filters out log messages with log level WARNING (numeric value: 30) or higher."""
        return record.levelno < 30


class _ExcludeChannelsFilter(logging.Filter):
    """
    Class to filter out any messages equal to level 25.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """Filters out log messages with log level CHANNELS (numeric value: 25)."""
        return record.levelno != 25


# Logic to add new, custom logging levels.
def add_logging_level(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the currently configured logging class.
    See https://stackoverflow.com/a/35804945 for details.
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

# Add new logging level.
add_logging_level('CHANNELS', 25)


# Logging variables.
handler_class = 'logging.handlers.RotatingFileHandler'
handler_file_max_bytes = 1024*1024*10
handler_file_backup_count = 10

# Set up logging configuration.
LOGGING = {
    'version': 1,
    'filters': {
        'exclude_channels': {
            '()': _ExcludeChannelsFilter,
        },
        'exclude_warnings': {
            '()': _ExcludeWarningsFilter,
        },
    },
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
            'formatter': 'standard',
        },
        # Debug level - To file.
        'file_debug': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'debug.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
            'filters': ['exclude_channels'],
        },
        'file_debug_connections': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'debug/connections.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
        },
        'file_debug_selenium': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'debug/selenium.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
        },
        'file_debug_sql_queries': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'sql/queries.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
        },
        'file_debug_sql_schema': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'sql/schema.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
        },
        'file_debug_templates': {
            'level': 'DEBUG',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'debug/templates.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
        },
        # Info level - To file.
        'file_info': {
            'level': 'INFO',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'info.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
            'filters': ['exclude_channels'],
        },
        # Channels level - To file.
        'file_channels': {
            'level': 'CHANNELS',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'channels.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'standard',
            'filters': ['exclude_warnings'],
        },
        # Warn level - To file.
        'file_warn': {
            'level': 'WARNING',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'warn.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
            'formatter': 'verbose',
        },
        # Error level - To file.
        'file_error': {
            'level': 'ERROR',
            'class': handler_class,
            'filename': os.path.join(LOGGING_DIRECTORY, 'error.log'),
            'maxBytes': handler_file_max_bytes,
            'backupCount': handler_file_backup_count,
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
        # Catch all for all other log types not found below (hopefully).
        '': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_channels', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
        'main': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_channels', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },

        # Various debug logging, mostly associated with Daphne (Channels) or Redis.
        'asyncio': {
            'handlers': ['file_debug_connections'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'aioredis': {
            'handlers': ['file_debug_connections'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'daphne.http_protocol': {
            'handlers': ['file_debug_connections'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'daphne.ws_protocol': {
            'handlers': ['file_debug_connections'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_debug_sql_queries'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.db.backends.schema': {
            'handlers': ['file_debug_sql_schema'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['file_debug_templates'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'selenium': {
            'handlers': ['file_debug_selenium'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'urllib3.connectionpool': {
            'handlers': ['file_debug_connections'],
            'level': 'NOTSET',
            'propagate': False,
        },

        # Standard logging for Django.
        'django': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },

        # Standard logging for Django Channels.
        'django.channels': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.channels.request': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.channels.server': {
            'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error',],
            'level': 'NOTSET',
            'propagate': False,
        },
    },
}


# Initialize logging.
LOGGING_CONFIG = None # Prevent django from initializing logging again
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

#endregion Logging Settings


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


# Set custom "development mode url" variable, based on DEBUG.
# Necessary for unit testing, or else tests referring to development urls will automatically fail.
if DEBUG:
    DEV_URLS = True
else:
    DEV_URLS = False

#endregion Environment Values


#region Third Party Library Settings

# django-phonenumber-field settings
PHONENUMBER_DEFAULT_REGION = "US" # Don't require users to prefix with +1

#endregion Third Party Library Settings
