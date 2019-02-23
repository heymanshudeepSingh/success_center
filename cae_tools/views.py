"""
Views for CAE Tools app.
"""

from django.template.response import TemplateResponse


def color_tool(request):
    """
    Color tool.
    """
    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
