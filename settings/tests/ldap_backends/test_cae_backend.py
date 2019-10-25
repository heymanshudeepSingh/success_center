"""
Tests for CAE Home app Forms.
"""

# System Imports.
import unittest
from django.conf import settings
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from settings.ldap_backends.wmu_auth.cae_backend import CaeAuthBackend


def are_ldap_test_values_populated():
    """
    Checks if "test ldap account" values are populated in local env file.
    Used to determine if Ldap tests should run or not.
    :return: Bool indicating if values are populated.
    """
    if str(settings.CAE_LDAP_TEST_NAME) != '' and str(settings.CAE_LDAP_TEST_PASS) != '':
        return True
    else:
        return False


class AdvisingAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper Cae Center Auth Backend implementation.
    """
