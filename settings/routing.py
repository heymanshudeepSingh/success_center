"""
Site-wide route handling for channels websockets.

Note: Routes will automatically be prefixed with "ws/<url-prefix>/" as defined in allowed_apps.py.
"""
import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.conf.urls import url
from importlib import import_module

from cae_home import routing as cae_home_routing

logger = logging.getLogger(__name__)


# Variable to gather all app routing.
url_routes = [
    url('^ws/cae_home/', URLRouter(cae_home_routing.websocket_urlpatterns)),
]


# Dynamically grab app routes for url_routes variable. Essentially the same logic as urls.py.
for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
    url_prefix = project_settings['url-prefix']
    for app, app_name in project_settings['related_apps'].items():
        try:
            # First, we dynamically import the new routes via the import_module function.
            # Then, add the new routing to url_routes.
            app_routing = import_module('apps.{0}.{1}.routing'.format(project, app))
            url_routes.append(
                url(r'^ws/{0}/'.format(url_prefix), URLRouter(app_routing.websocket_urlpatterns))
            )
        except ModuleNotFoundError:
            logger.info("Assuming no routing to import for %s.%s", project, app)
        except:
            # No valid app routes. Skipping.
            logger.exception(
                "Error importing routing for %s.%s", project, app,
                exc_info=True)


# Create actual routes, with authentication.
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            url_routes
        ),
    )
})
