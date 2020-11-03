"""
Tool views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def color_tool(request):
    """
    Color tool.
    """
    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
