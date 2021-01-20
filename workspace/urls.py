"""
Site-wide URL Configuration.

Note: Urls will automatically be prefixed with "<url-prefix>/" as defined in allowed_apps.py.
"""

# System Imports.
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from rest_framework import routers

# User Class Imports.
from .settings import reusable_settings
from cae_home import views


router = routers.DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)


# Special view handling.
handler400 = 'cae_home.views.handler400'
handler403 = 'cae_home.views.handler403'
handler404 = 'cae_home.views.handler404'
handler500 = 'cae_home.views.handler500'


# General url handling.
urlpatterns = [
    # Admin views.
    path('admin/', admin.site.urls),

    # DjangoRest urls.
    path('api/', include(router.urls)),
    # url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # CAE_Home app views.
    path('', include('cae_home.urls')),
]


# Debug only urls.
if settings.DEV_URLS:
    urlpatterns += [
        # CAE Tools app views.
        path('dev/', include('cae_tools.urls', namespace='dev')),
        path('cae_tools/', include('cae_tools.urls', namespace='cae_tools')),
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