"""
Site-wide URL Configuration.

Note: Urls will automatically be prefixed with "<url-prefix>/" as defined in allowed_apps.py.
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from settings import reusable_settings


urlpatterns = [
    # Admin views.
    url(r'^admin/', admin.site.urls),

    # CAE_Home app views.
    url(r'^', include('cae_home.urls')),

    # CAE Tools app views.
    url(r'^cae_tools/', include('cae_tools.urls')),
]


# Dynamically grab app urls for urlpatterns variable. Essentially the same logic as routing.py.
for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
    url_prefix = project_settings['url-prefix']
    for app, app_name in project_settings['related_apps'].items():
        try:
            # Add app's urls to urlpatterns variable.
            urlpatterns.append(
                url(r'^{0}/'.format(url_prefix), include('{0}.urls'.format(app_name))),
            )
        except ImportError:
            reusable_settings.debug_print('{0}Warning{1}: No valid urls for {2}:{3}. Skipping app url import.'.format(
                reusable_settings.ConsoleColors.bold_yellow,
                reusable_settings.ConsoleColors.reset,
                project,
                app,
            ))

reusable_settings.debug_print('')
