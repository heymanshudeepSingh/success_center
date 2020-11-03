"""
Misc views for CAE Tools app.
"""

# System Imports.
from django.shortcuts import redirect

# User Imports.


def index(request):
    """
    CAE Tools index.
    Currently only redirects to color tool
    """
    return redirect('cae_tools:color_tool')
