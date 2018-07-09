"""
Site-wide URL Configuration
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Admin views.
    url(r'^admin/', admin.site.urls),

    # CAE_Home app views.
    url(r'^', include('cae_home.urls')),
]


# Add dynamically generated root urls.
for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
    url_prefix = project_settings['url-prefix']
    for app, app_name in project_settings['related_apps'].items():
        try:
            urlpatterns.append(
                url(r'^{0}/'.format(url_prefix), include('{0}.urls'.format(app_name))),
            )
        except ImportError:
            # No valid app urls. Skipping.
            pass
