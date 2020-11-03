"""
"Test" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_tests(request):
    """
    Documentation of custom "Test" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/tests.html', {})
