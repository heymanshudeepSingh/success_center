"""
"Settings" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_settings(request):
    """
    Documentation of custom "Settings" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings.html', {})


def docs_settings_organization(request):
    """
    Documentation of project settings organization.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings/organization.html', {})


def docs_settings_local_environment(request):
    """
    Documentation of local environment settings.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings/local_environment.html', {})


def docs_settings_dev_password(request):
    """
    Documentation of development (seeder) password.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings/dev_password.html', {})


def docs_settings_logging(request):
    """
    Documentation of project logging.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/settings/logging.html', {})
