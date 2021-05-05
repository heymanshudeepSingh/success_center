"""
"CSS" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_css(request):
    """
    Documentation of custom "CSS" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/css.html', {})


def docs_css_general_logic(request):
    """
    Documentation of general CSS logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/css/general_logic.html', {})


def docs_css_using_flexbox(request):
    """
    Documentation of Flexbox CSS logic.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/css/using_flexbox.html', {})
