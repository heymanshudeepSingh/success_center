"""
"Seeds and Fixtures" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_seeds_and_fixtures(request):
    """
    Documentation of custom "Seeds and Fixtures" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/seeds_and_fixtures.html', {})
