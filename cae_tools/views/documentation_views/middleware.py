"""
"Middleware" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_middlware(request):
    """
    Documentation of custom "Middleware" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/middleware.html', {})
