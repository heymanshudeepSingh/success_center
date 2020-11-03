"""
"Template" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_templates(request):
    """
    Documentation of custom "Template" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/templates.html', {})
