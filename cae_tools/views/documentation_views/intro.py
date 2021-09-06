"""
"General Setup" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.

def docs_intro_first_steps(request):
    """
    Documentation of "first steps".
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/first_steps.html', {})


def docs_intro(request):
    """
    Documentation of project introduction.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/introduction.html', {})


def docs_intro_setup(request):
    """
    Documentation of "general project setup".
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/setup.html', {})


def docs_intro_managepy(request):
    """
    Documentation of "manage.py" usage.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/managepy.html', {})


def docs_intro_virtual_environments(request):
    """
    Documentation of "Python virtual environments".
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/virtual_environments.html', {})


def docs_intro_helper_scripts(request):
    """
    Documentation of "project bash helper scripts".
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/intro/helper_scripts.html', {})
