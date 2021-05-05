"""
"Test" documentation views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.


def docs_running_tests(request):
    """
    Documentation of running project tests.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/testing/running_tests.html', {})


def docs_base_test_case(request):
    """
    Documentation of using the BaseTestCase utility test class.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/testing/base_test_case.html', {})


def docs_integration_test_case(request):
    """
    Documentation of using the IntegrationTestCase utility test class.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/testing/integration_test_case.html', {})


def docs_live_server_test_case(request):
    """
    Documentation of using the LiveServerTestCase utility test class.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/testing/live_server_test_case.html', {})
