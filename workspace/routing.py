"""
Site-wide route handling for channels websockets.

Note: Routes will automatically be prefixed with "ws/<url-prefix>/" as defined in allowed_apps.py.
"""

# System Imports.
import logging
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.urls import re_path
from importlib import import_module

# User Imports.
from cae_home import routing as cae_home_routing
from workspace.settings.reusable_settings import debug_print


# Import logger.
# logger = logging.getLogger(__name__)


# Variable to gather all app routing.
url_routes = [
    re_path('^ws/cae_home/', URLRouter(cae_home_routing.websocket_urlpatterns)),
]


# Dynamically grab app routes for url_routes variable. Essentially the same logic as urls.py.
for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
    url_prefix = project_settings['url-prefix']
    for app, app_name in project_settings['related_apps'].items():
        try:
            # First, we dynamically import the new routes via the import_module function.
            # Then, add the new routing to url_routes.
            app_routing = import_module('{0}.routing'.format(app_name))
            url_routes.append(
                re_path(r'^ws/{0}/'.format(url_prefix), URLRouter(app_routing.websocket_urlpatterns))
            )
        except ModuleNotFoundError:
            debug_print("Assuming no routing to import for {0}".format(app_name))
        except:
            # No valid app routes. Skipping.
            debug_print("Error importing routing for {0}".format(app_name), exc_info=True)


# Create actual routes, with authentication.
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            url_routes
        ),
    )
})
