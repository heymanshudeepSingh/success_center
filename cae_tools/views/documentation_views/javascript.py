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


def docs_javascript_passing_variables(request):
    """
    Documentation of passing view/template variables to JavaScript code.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/javascript/passing_variables.html', {})


def docs_javascript_libraries(request):
    """
    Documentation of JavaScript libraries included in Workspace.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/javascript/libraries.html', {})
