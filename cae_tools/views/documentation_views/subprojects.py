"""
"Subproject" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_subprojects(request):
    """
    Documentation of custom "Subprojects" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/subprojects.html', {})
