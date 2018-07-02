"""
Views for CAE_Home App.
"""
from django.conf import settings
from django.shortcuts import render


def index(request):
    """
    Root site url. Displays links to all added sub-projects.
    """
    sub_project_sites = [
        app_settings['site'] for app_settings in settings.INSTALLED_CAE_PROJECTS.values() if 'site' in app_settings
    ]
    return render(request, 'cae_home/index.html', {
        'sub_project_sites': sub_project_sites,
    })
