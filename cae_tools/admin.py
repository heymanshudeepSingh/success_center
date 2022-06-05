"""
Admin Views for CAE Tools app.
"""

# System Imports.
from django.conf import settings
from django.contrib import admin

# User Imports.
from . import models


# Only display in admin if in development.
if settings.DEV_MODE:
    admin.site.register(models.ExampleDocsSignatureModel)
