"""
"LDAP" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_ldap(request):
    """
    Documentation of custom "LDAP" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/ldap.html', {})


def docs_ldap_setup(request):
    """
    Documentation of LDAP setup.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/ldap/setup.html', {})


def docs_ldap_auth_backends(request):
    """
    Documentation of custom Django Auth backends.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/ldap/auth_backends.html', {})


def docs_ldap_utility_connectors(request):
    """
    Documentation of custom LDAP Utility Connectors.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/ldap/utility_connectors.html', {})
