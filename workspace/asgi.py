"""
ASGI entrypoint. Configures Django and then runs the application defined in the ASGI_APPLICATION setting.
"""

# System Imports.
import os
import django
from channels.routing import get_default_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workspace.settings.settings")
django.setup()
application = get_default_application()
