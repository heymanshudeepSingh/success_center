"""
Core settings for Django project.

These are settings that are essentially expected by Django or Third Party Libraries.
(See "settings/allowed_apps.py" file for INSTALLED_APPS variable and related logic.)
"""

# User Class Imports.
from settings.reusable_settings import *


debug_print("===== Base Settings =====")


# Application definition

from settings.allowed_apps import (
    INSTALLED_APPS, INSTALLED_CAE_PROJECTS, INSTALLED_APP_DETAILS, ADMIN_REORDER, INSTALLED_APP_URL_DICT
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'admin_reorder.middleware.ModelAdminReorder',

    'cae_home.middleware.GetUserProfileMiddleware',
    'cae_home.middleware.GetProjectDetailMiddleware',
    'cae_home.middleware.GetUserSiteOptionsMiddleware',
    'cae_home.middleware.SetTimezoneMiddleware',

    'cae_home.middleware.HandleExceptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # 'DIRS': [os.path.join(BASE_DIR, 'cae_home/templates/cae_home/errors')], # Internal error views.
        # 'DIRS': [os.path.join(BASE_DIR, 'cae_home/templates/error_views')],   # External error views.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WEBPACK_LOADER = {
    'CICO': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': os.path.join(BASE_DIR, '/apps/CICO/cico_core/static/cico_core/dist/'),  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, '/apps/CICO/cico_core/static/cico_core/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}

ASGI_APPLICATION = 'settings.routing.application'
WSGI_APPLICATION = 'settings.wsgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
        'TEST_CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        }
    }
}


# User Model.
AUTH_USER_MODEL = 'cae_home.User'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Detroit'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Import "extra" settings.
# Includes things like logging and local settings.
from settings.extra_settings import *


# Force additional blank line for debug printing.
debug_print('')
