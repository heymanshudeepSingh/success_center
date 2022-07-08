"""
Extra (local) settings for Django project.

These are generally custom or optional settings (as in not necessarily mandatory to Django or installed Libraries).
Settings here are likely to change based on Project installation.

For settings that will generally stay the same, regardless of Project installation, see "settings/extra_settings.py".


Note that this is just an example file. Any values committed to this file should be exmaple or "expected default" values.
To use in project, please copy file and save at "settings/local_env/env.py".
"""

# User Imports.
from workspace.settings.reusable_settings import *


# region User Seed Settings

# Username list for user model seeds.
# These are used as username values for User seed models used in development.
SEED_USERS = [
    # Insert seed user names (as strings) here.
]

# Password for user model seeds.
# This is the password used for all the seeded dev accounts (both in normal serving and tests).
USER_SEED_PASSWORD = 'temppass2'

# endregion User Seed Settings


# region Database Setup

# Database connection information.
DATABASES = {
    # SqLite, for development environments.
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'default-character-set': 'utf8',
        'TEST': {
            'NAME': 'testdb.sqlite3',
        },
    },

    # MySQL, for production environments.
    # To use this, uncomment the "mysqlclient" in project requirements.txt and install to your python environment.
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'cae_workspace',
    #     'USER': 'root',
    #     'PASSWORD': 'root',
    #     'HOST': '127.0.0.1',
    #     'PORT': '3306',
    #     'default-character-set': 'utf8mb4',
    #     'CONN_MAX_AGE': 600,    # See http://www.programmersought.com/article/1815911998/ for info.
    #     'TEST': {
    #         'NAME': 'testdb.sqlite3',
    #     },
    # }
}

# endregion Database Setup


# region Site Serve Settings

# Allowed server hosts.
ALLOWED_HOSTS = [
    # List of domain names the project can serve. Helps prevent HTTP Host Header attacks.
]


# Static/Media file locations.
# Static refers to CSS, JavaScript, Images, etc provided by project. Media refers to any user-uploaded files.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'temp/static/')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'temp/media/')
STATICFILES_DIRS = (
    # Path to any additional, non-standard static directories.
)


# Allows giving static files unique hashes, which force browsers to automatically download when files change.
# However, requires site to be set up to serve static in production mode.
# Uncomment in production. Leave commented out in development.
# STATICFILES_STORAGE = 'workspace.settings.static_storage.ForgivingManifestStaticFilesStorage'

# endregion Site Serve Settings


# region Authentication

# Set desired authentication backend. Defaults to standard Django auth.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',    # Listed first so test users do not attempt to validate to LDAP.
    # 'workspace.ldap_backends.wmu_auth.cae_backend.CaeAuthBackend',
    # 'workspace.ldap_backends.wmu_auth.cae_backend.WmuAuthBackend',
)
AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS = False  # If false, always use LDAP and never store user password in Django.
AUTH_BACKEND_DEBUG = False  # Determines if authentication backend should run debug logging or not. Defaults to off.

# LDAP settings used when CAEAuthBackend is active.
CAE_LDAP = {
    'host': '',
    'login_dn': '',
    'login_password': '',
    'admin_dn': '',
    'admin_password': '',
    'default_uid': '',
    'user_search_base': '',
    'group_dn': '',
    'director_cn': '',
    'attendant_cn': '',
    'admin_cn': '',
    'programmer_cn': '',
}

# LDAP settings used when WmuAuthBackend is active.
WMU_LDAP = {
    'host': '',
    'login_dn': '',
    'login_password': '',
    'default_uid': '',
    'user_search_base': '',
}

# LDAP settings for AdvisingAuthBackend.
# Note that most values are still imported from WMU_LDAP. Only the credentials change.
# This is because the Advising LDAP account has access to student information that the CAE account does not.
ADV_LDAP = {
    'login_dn': '',
    'login_password': '',
}

# endregion Authentication


# region Email Settings

# Email settings.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'    # For SMTP, use 'backends.smtp.EmailBackend'.
EMAIL_HOST = ''                             # Ip address for SMTP email server.
EMAIL_HOST_USER = ''                        # Name for SMTP user.
EMAIL_HOST_PASSWORD = ''                    # Password for SMTP user.
EMAIL_PORT = ''                             # Port for SMTP email server.
EMAIL_USE_TLS = True                        # Explicitly uses TLS for SMTP communication.
DEFAULT_FROM_EMAIL = 'webmaster@localhost'  # Default email address for standard emails.
SERVER_EMAIL = 'root@localhost'             # Default email address for admin error emails.


# Admins to send emails to on error (Only sends if debug = False).
# Should be a list of tuples, one tuple for each admin, where each tuple is format (<user_name>, <user_email>).
ADMINS = []

# endregion Email Settings


# region General Site Settings

# Log folder location
LOGGING_DIRECTORY = os.path.join(BASE_DIR, 'workspace/local_env/logs/')

# # HTTPS/Security Settings. Used in production.
# SECURE_SSL_REDIRECT = True
# SECURE_SSL_HOST = ""
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
#
# SECURE_HSTS_SECONDS =
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = "DENY"
# SECURE_BROWSER_XSS_FILTER = True

# endregion General Site Settings


# region Testing Settings

# UnitTesting Settings.
#   * Provided Prog account should be active for WMU Ldap system.
#   * Provided Student account should be active in both CAE and WMU Ldap systems.
BACKEND_LDAP_TEST_PROG_ID = ''          # BroncoNet for CAE Center Ldap programmer account.
BACKEND_LDAP_TEST_STUDENT_ID = ''       # BroncoNet for active Ldap student.

# Selenium Integration Test Settings.
SELENIUM_TESTS_BROWSER = 'chrome'   # Set to 'firefox' to use firefox browser instead.
SELENIUM_TESTS_HEADLESS = False     # Set to True to run selenium in headless mode (hides browser window).

#enregion Testing Settings


# region Third Party Library Settings

# DjangoRest settings.
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# endregion Third Party Library Settings


# region Project Specific Settings

# Values used in DropOff project.
# Can be left blank if DropOff is not installed locally.
REDMINE_URL = ''
REDMINE_USER = ''
REDMINE_PASSWORD = ''
CUPS_SERVER = ''

# endregion Project Specific Settings
