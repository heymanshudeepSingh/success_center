"""
Views for CAE_Home App.
"""

from django.template.response import TemplateResponse


def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    """
    return TemplateResponse(request, 'cae_home/index.html', {})
