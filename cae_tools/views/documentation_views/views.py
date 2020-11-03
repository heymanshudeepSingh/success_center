"""
"View" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_views(request):
    """
    Documentation of custom "Views" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/views.html', {})
