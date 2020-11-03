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
