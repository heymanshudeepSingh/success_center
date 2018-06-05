"""
Local settings .env file.

Commited values should just be example or "expected default" values.
Modify per local environment needs.
"""


# User Class Imports.
from settings.reusable_settings import *


# Static/Media file locations.
# Static refers to CSS, JavaScript, Images, etc provided by project. Media refers to any user-uploaded files.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_URL = '/static/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')
STATICFILES_DIRS = (
    # Path to any additional, non-standard static directories.
)


# Allowed server hosts.
ALLOWED_HOSTS = [
    # List of domain names the project can serve. Helps prevent HTTP Host Header attacks.
]


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
    }
}


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
