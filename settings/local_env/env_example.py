"""
Extra (local) settings for Django project.

These are generally custom or optional settings (as in not necessarily mandatory to Django or installed Libraries).
Settings here are likely to change based on Project installation.

For settings that will generally stay the same, regardless of Project installation, see "settings/extra_settings.py".


Note that this is just an example file. Any values committed to this file should be exmaple or "expected default" values.
To use in project, please copy file and save at "settings/local_env/env.py".
"""

# User Class Imports.
from settings.reusable_settings import *


#region Site Serve Settings

# Allowed server hosts.
ALLOWED_HOSTS = [
    # List of domain names the project can serve. Helps prevent HTTP Host Header attacks.
]


# Static/Media file locations.
# Static refers to CSS, JavaScript, Images, etc provided by project. Media refers to any user-uploaded files.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')
STATICFILES_DIRS = (
    # Path to any additional, non-standard static directories.
)

#endregion Site Serve Settings


#region Authentication

# Set desired authentication backend. Defaults to standard Django auth.
AUTHENTICATION_BACKENDS = (
    # 'settings.backends.CaeAuthBackend',
    # 'settings.backends.WmuAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_BACKEND_DEBUG = False

# LDAP settings used when CAEAuthBackend is active.
CAE_LDAP = {
    'host': '',
    'login_dn': '',
    'login_password': '',
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
    'user_search_base': '',
}

#endregion Authentication


#region Database Setup

# Database connection information.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), # SQlite: File Location. MySQL: Database Name.
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'default-character-set': 'utf8',
        'TEST': {
            'NAME': 'testdb.sqlite3',
        },
    }
}

#endregion Database Setup


#region Email Settings

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
ADMINS = []

#endregion Email Settings


#region General Site Settings

# Password for user model seeds.
# This is the password used for all the "default" accounts (both in normal serving and tests).
USER_SEED_PASSWORD = 'temppass2'

# # HTTPS/Security Settings. Used in production.
# SECURE_SSL_HOST = ""
# SECURE_SSL_REDIRECT = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
#
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_SECONDS =
# SECURE_BROWSER_XSS_FILTER = True
# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True

#endregion General Site Settings


#region Third Party Library Settings

# DjangoRest settings.
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# Selenium Integration Test settings.
SELENIUM_TESTS_BROWSER = 'chrome'   # Set to 'firefox' to use firefox browser instead.
SELENIUM_TESTS_HEADLESS = False     # Set to True to run selenium in headless mode (hides browser window).

#endregion Third Party Library Settings
