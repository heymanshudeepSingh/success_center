"""
"Settings" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_settings(request):
    """
    Documentation of custom "Settings" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings.html', {})
