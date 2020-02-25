"""
Logging initialization.
Returns an instance of the project logger.
If first time call, then also sets up logging values for project.

Note: Standard log priority is "NOTSET" > "DEBUG" > "INFO" > "WARNING" > "ERROR" > "CRITICAL".
    See wiki for full list of non-standard values.
"""

# System Imports.
import logging.config

# User Class Imports.
from settings.reusable_settings import *


# Variables to help run logging.
LOG_VERSION = 2.1
first_logging_call = True
log_handler_class = 'logging.handlers.RotatingFileHandler'
log_handler_file_max_bytes = 1024 * 1024  # Roughly 1 MB.
log_handler_file_backup_count = 20


def get_logger(caller, log_dir=None):
    """
    Returns an instance of the logger. Always pass the __name__ attribute.
    By calling through here, guarantees that logger will always have proper settings loaded.
    :param caller: __name__ attribute of caller.
    :param log_dir: Directory to initialize logging at. Defined in "settings/local_env/env.py".
    :return: Instance of logger, associated with caller's __name__.
    """
    # Initialize logger.
    if first_logging_call:
        _initialize_logger_settings(log_dir)

    # Return logger instance, using passed name.
    return logging.getLogger(caller)


def _initialize_logger_settings(log_dir, debug=False):
    """
    Creates log directories (if not found) and initializes logging settings.
    :param debug: Boolean to indicate if test log messages should also be displayed after initialization.
    """
    if log_dir is None:
        raise ValueError('Logging dir is none. Cannot setup logging.')

    # Set up logging directories.
    auth_log_dir = os.path.join(log_dir, 'auth/')
    debug_log_dir = os.path.join(log_dir, 'debug/')
    sql_log_dir = os.path.join(log_dir, 'sql/')

    # Check if logging path exists.
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Check if auth logging path exists.
    if not os.path.exists(auth_log_dir):
        os.makedirs(auth_log_dir)

    # Check if debug logging path exists.
    if not os.path.exists(debug_log_dir):
        os.makedirs(debug_log_dir)

    # Check if sql logging path exists.
    if not os.path.exists(sql_log_dir):
        os.makedirs(sql_log_dir)

    # Add new logging levels. See wiki for currently defined levels in all projects.
    add_logging_level('CHANNELS', 21)
    add_logging_level('AUTH_INFO', 25)
    add_logging_level('AUTH_WARNING', 35)
    add_logging_level('AUTH_ERROR', 45)

    # Load dictionary of settings into logger.
    logging.config.dictConfig(_create_logging_dict(log_dir))

    # Now that logging has been initialized once, we don't need to call this function again for the duration of program
    # runtime. Set "first_logging_call" variable accordingly.
    global first_logging_call
    first_logging_call = False

    # Optionally test that logging is working as expected.
    if debug:
        logger = logging.getLogger(__name__)
        logger.info('Logging initialized.')
        logger.debug('Logging directory: {0}'.format(log_dir))


def _create_logging_dict(log_directory):
    """
    Creates dictionary-styled logging options.
    :param log_directory: Directory to use for saving logs.
    :return: Dictionary of logging options.
    """
    return {
        'version': 1,
        'filters': {
            # Default level filters.
            'exclude_info_plus': {
                '()': _ExcludeInfoPlusFilter,
            },
            'exclude_warnings_plus': {
                '()': _ExcludeWarningsPlusFilter,
            },
            'exclude_error_plus': {
                '()': _ExcludeErrorPlusFilter,
            },

            # Custom level filters.
            'exclude_channels': {
                '()': _ExcludeChannelsFilter,
            },
            'include_only_auth': {
                '()': _IncludeOnlyAuthFilter,
            },
            'exclude_auth': {
                '()': _ExcludeAuthFilter,
            },
        },
        'formatters': {
            # Minimal logging. Only includes message.
            # Generally meant for terminal "end user" interface display.
            'minimal': {
                'format': '%(message)s',
            },
            # Simple logging. Includes message type and actual message.
            # Generally meant for console logging.
            'simple': {
                'format': '[%(levelname)s] [%(filename)s %(lineno)d]: %(message)s',
            },
            # Basic logging. Includes date, message type, file originated, and actual message.
            # Generally meant for file logging.
            'standard': {
                'format': '%(asctime)s [%(levelname)s] [%(name)s %(lineno)d]: %(message)s',
            },
            # Verbose logging. Includes standard plus the process number and thread id.
            # For when you wanna be really verbose.
            'verbose': {
                'format': '%(asctime)s [%(levelname)s] [%(name)s %(lineno)d] || %(process)d %(thread)d || %(message)s'
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
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'debug.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth', 'exclude_channels'],
            },
            'file_debug_connections': {
                'level': 'DEBUG',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'debug/connections.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth'],
            },
            'file_debug_selenium': {
                'level': 'DEBUG',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'debug/selenium.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
            },
            'file_debug_sql_queries': {
                'level': 'DEBUG',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'sql/queries.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
            },
            'file_debug_sql_schema': {
                'level': 'DEBUG',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'sql/schema.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
            },
            'file_debug_templates': {
                'level': 'DEBUG',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'debug/templates.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
            },
            # Info level - To file.
            'file_info': {
                'level': 'INFO',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'info.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth', 'exclude_channels'],
            },
            # Channels level - To file.
            'file_channels': {
                'level': 'CHANNELS',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'channels.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth', 'exclude_warnings_plus'],
            },
            # Auth info level - To file.
            'file_auth_info': {
                'level': 'AUTH_INFO',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'auth/info.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['include_only_auth'],
            },
            # Simple Ldap Lib - To file.
            'simple_ldap_info': {
                'level': 'INFO',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'debug/simple_ldap.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth'],
            },
            # Warn level - To file.
            'file_warn': {
                'level': 'WARNING',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'warn.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth'],
            },
            # Auth warn level - To file.
            'file_auth_warn': {
                'level': 'AUTH_WARNING',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'auth/warn.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['include_only_auth'],
            },
            # Error level - To file.
            'file_error': {
                'level': 'ERROR',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'error.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['exclude_auth'],
            },
            # Auth info level - To file.
            'file_auth_error': {
                'level': 'AUTH_ERROR',
                'class': log_handler_class,
                'filename': os.path.join(log_directory, 'auth/error.log'),
                'maxBytes': log_handler_file_max_bytes,
                'backupCount': log_handler_file_backup_count,
                'formatter': 'standard',
                'filters': ['include_only_auth'],
            },
            # Error level - To admin email.
            'mail_error': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            # Catch all for all other log types not found below (hopefully).
            '': {
                'handlers': [
                    'console', 'file_debug',
                    'file_info', 'file_channels', 'file_auth_info',
                    'file_warn', 'file_auth_warn',
                    'file_error', 'file_auth_error',
                    'mail_error',
                ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'main': {
                'handlers': [
                    'console', 'file_debug',
                    'file_info', 'file_channels', 'file_auth_info',
                    'file_warn', 'file_auth_warn',
                    'file_error', 'file_auth_error',
                    'mail_error',
                ],
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
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'django.server': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },

            # Standard logging for Django Channels.
            'django.channels': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'django.channels.request': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },
            'django.channels.server': {
                'handlers': ['console', 'file_debug', 'file_info', 'file_warn', 'file_error', 'mail_error', ],
                'level': 'NOTSET',
                'propagate': False,
            },

            # Logging for custom libraries.
            'simple_ldap_lib': {
                'handlers': ['simple_ldap_info'],
                'level': 'NOTSET',
                'propagate': False,
            },
        },
    }


def add_logging_level(levelName, levelNum, methodName=None):
    """
    Code directly imported from
    https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility

    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.
    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.
    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present
    Example
    -------
    >> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >> logging.getLogger(__name__).setLevel("TRACE")
    >> logging.getLogger(__name__).trace('that worked')
    >> logging.trace('so did this')
    >> logging.TRACE
    5
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


#region Logging Filters

class _ExcludeInfoPlusFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """
        Filters out log messages with log level(s):
            (20) INFO
        """
        return record.levelno < 20


class _ExcludeWarningsPlusFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """
        Filters out log messages with log level(s):
            (30) WARNING
        """
        return record.levelno < 30


class _ExcludeErrorPlusFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """

    def filter(self, record):
        """
        Filters out log messages with log level(s):
            (40) Error
        """
        return record.levelno < 40


class _ExcludeChannelsFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """
        Filters out log messages with log level(s):
            (21) CHANNELS
        """
        return record.levelno != 21


class _IncludeOnlyAuthFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """
        Filters out log messages outside of log level(s):
            (25) AUTH_INFO
            (35) AUTH_WARNING
            (45) AUTH_ERROR
        """
        return (record.levelno == 25 or record.levelno == 35 or record.levelno == 45)


class _ExcludeAuthFilter(logging.Filter):
    """
    Class to filter out log messages of a given level.
    See https://stackoverflow.com/a/53257669 for more info.
    """
    def filter(self, record):
        """
        Filters out log messages with log level(s):
            (25) AUTH_INFO
            (35) AUTH_WARNING
            (45) AUTH_ERROR
        """
        return (record.levelno != 25 and record.levelno != 35 and record.levelno != 45)

#endregion Logging Filters
