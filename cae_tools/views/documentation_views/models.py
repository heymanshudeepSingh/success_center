"""
"Models" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_models(request):
    """
    Documentation of custom "Model" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/models.html', {})
