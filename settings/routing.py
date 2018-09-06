"""
Site-wide route handling for channels websockets.

Note: Routes will automatically be prefixed with "ws/<url-prefix>/" as defined in allowed_apps.py.
"""

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.conf.urls import url

from cae_home import routing


# Variable to gather all app routing.
url_routes = [
    url('^ws/cae_home/', URLRouter(routing.websocket_urlpatterns)),
]


# Dynamically grab app routes for url_routes variable. Essentially the same logic as urls.py.
for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
    url_prefix = project_settings['url-prefix']
    for app, app_name in project_settings['related_apps'].items():
        try:
            # Slight magic here.
            # First, we grab a string of the expected route file path.
            get_string = '{0}.{1}'.format(project, app)
            # Next, exec us execute a string as part of an import statement. We specifically
            # import onto an already defined variable so that we don't get compilation errors.
            exec('from apps.{0} import routing'.format(get_string, app))
            # Finally, we add the new, overridden routing variable to url_routes.
            url_routes.append(
                url(r'^ws/{0}/'.format(url_prefix), URLRouter(routing.websocket_urlpatterns))
            )
        except ImportError:
            # No valid app routes. Skipping.
            pass

# Create actual routes, with authentication.
application = ProtocolTypeRouter({
    # Note, django views are "added by default".
    'websocket': AuthMiddlewareStack(
        URLRouter(
            url_routes
        ),
    )
})
