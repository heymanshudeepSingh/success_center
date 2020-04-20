"""
Tests for CAE Center Authentication Backend.
"""

# System Imports.
import unittest
from django.conf import settings
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from settings.tests.utils import run_ldap_tests
from settings.tests.utils import prog_or_student_test_account_is_populated
from settings.tests.utils import prog_test_account_is_populated, student_test_account_is_populated
if run_ldap_tests():
    from settings.ldap_backends.wmu_auth.cae_backend import CaeAuthBackend


class CaeAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper Cae Center Auth Backend implementation.
    """
