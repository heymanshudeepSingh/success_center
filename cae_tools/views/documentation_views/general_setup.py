"""
"General Setup" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_general_setup(request):
    """
    Documentation of custom "General Setup" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/general_setup.html', {})
