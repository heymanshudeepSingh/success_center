"""
Misc views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def index(request):
    """
    CAE Tools index.
    """
    return TemplateResponse(request, 'cae_tools/index.html', {})


def documentation(request):
    """
    Index for documentation of custom Workspace project logic.
    """
    return TemplateResponse(request, 'cae_tools/documentation.html', {})
