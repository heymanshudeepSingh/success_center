"""
Views for CAE_Home App.
"""

from django.conf import settings
from django.shortcuts import render


def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    """
    # Get all imported projects and related apps.
    imported_projects = [
        app_settings['site'] for app_settings in settings.INSTALLED_CAE_PROJECTS.values() if 'site' in app_settings
    ]

    return render(request, 'cae_home/index.html', {
        'imported_projects': imported_projects,
    })
