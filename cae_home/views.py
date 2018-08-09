"""
Views for CAE_Home App.
"""

from django.template.response import TemplateResponse


def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    """
    return TemplateResponse(request, 'cae_home/index.html', {})


def wmu_test(request):
    """
    "WMU clone" test page. Used for development of imitation WMU layout.
    """
    return TemplateResponse(request, 'wmu_home/index.html', {})
