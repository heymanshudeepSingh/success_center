"""
"JavaScript" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_javascript(request):
    """
    Documentation of custom "JavaScript" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/javascript.html', {})
