"""
Debug/Development views for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# User Imports.
from workspace import logging as init_logging
from cae_tools.utils import test_single_email as utils_test_single_email


# Import logger.
logger = init_logging.get_logger(__name__)


def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'cae_home/index.html', {})
    else:
        raise Http404()


def internal_dev_index(request):
    """
    The internal (cae home) development index page.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return redirect('cae_home:index')
    else:
        raise Http404()


def external_dev_index(request):
    """
    The external (wmu clone) index page.
    Displays front-end information/examples specific to the external site layout and stylings.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'wmu_home/index.html', {})
    else:
        raise Http404()


# region Test Error Views

def test_400_error(request):
    raise SuspiciousOperation('Test 400 Error.')


def test_403_error(request):
    raise PermissionDenied('Test 403 Error.')


def test_500_error(request):
    raise Exception('Test 500 Error.')

# endregion Test Error Views


# region Email Test Views

def test_single_email(request):
    """
    Tests sending of email with "send_mail" function.
    This function is acceptable when a single email is to be sent.
    """
    if settings.DEBUG:
        # Run test.
        utils_test_single_email()

        # Redirect to home.
        return redirect('cae_home:index')
    else:
        raise Http404()

# endregion Email Test Views
