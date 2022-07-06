"""
Tool views for CAE Tools app.
"""

# System Imports.
from django.contrib import messages
from django.template.response import TemplateResponse

# User Imports.


def color_tool(request):
    """
    Color tool.
    """
    # Add depreciated warning messages.
    messages.warning(request, 'This page is no longer maintained, and is broken as of 2021.')
    messages.warning(
        request,
        (
            'Adobe has a team of full-time professionals that maintain something better than we could possibly make. '
            'Use this page to reference "official" wmu colors. Please see https://color.adobe.com for a much better '
            'version of what this page was trying to be.'
        ),
    )
    messages.warning(request, 'Please see https://color.adobe.com')

    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
