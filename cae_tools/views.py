"""
Views for CAE Tools app.
"""

from django.shortcuts import redirect
from django.template.response import TemplateResponse


def index(request):
    """
    CAE Tools index.
    Currently only redirects to color tool
    """
    return redirect('cae_tools:color_tool')


def color_tool(request):
    """
    Color tool.
    """
    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
