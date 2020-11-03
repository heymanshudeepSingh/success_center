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
