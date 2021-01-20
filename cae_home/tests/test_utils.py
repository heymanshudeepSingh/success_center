"""
Tests for CAE Home app utils.

Not to be confused with cae_home/tests/utils.py, which provides extra overall utility logic for testing.
"""

# System Imports.
import logging, unittest
from django.conf import settings
from django.core.management import call_command
from django.template.response import TemplateResponse
from django.test.client import Client
from os import devnull

# User Class Imports.
from cae_home import models
from cae_home.management.commands.fixtures.user import create_groups
from cae_home.utils import get_or_create_login_user_model, get_or_create_wmu_user_model
from cae_home.tests.utils import IntegrationTestCase
from workspace.tests.utils import run_ldap_tests, student_test_account_is_populated


class CAEHomeViewTests(IntegrationTestCase):
    """
    Tests to ensure views load as expected.
    """
    @classmethod
    def setUpTestData(cls):
        # Create general user groups.
        create_groups()

        # Get an arbitrary request.
        cls.client = Client()
        cls.request = cls.client.get('info/servers/')
        if student_test_account_is_populated():
            cls.test_student_account = str(settings.BACKEND_LDAP_TEST_STUDENT_ID)

        # Load all relevant fixtures.
        with open(devnull, 'a') as null:
            call_command('loaddata', 'production_models/site_themes', stdout=null)

        # Disable logging for tests.
        logging.disable(logging.CRITICAL)

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test_get_or_create_login_user(self):

        # Check if LDAP is enabled. Test accordingly.
        if run_ldap_tests():
            # Ldap enabled. Should either return a (login) User model, or None if invalid BroncoNet.
            with self.subTest('With invalid BroncoNet'):
                # Invalid BroncoNet. Should return None.
                return_val = get_or_create_login_user_model(self.request, 'abc1234')
                self.assertIsNone(return_val)

            with self.subTest('With valid BroncoNet, and corresponding model doesn\'t exist yet.'):
                # Valid BroncoNet. Should create and return new User model.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                user_model = models.User.objects.get(username=self.test_student_account)
                self.assertEqual(return_val, user_model)

            with self.subTest('With valid BroncoNet, and corresponding model already exists.'):
                # Valid BroncoNet. Should get and return existing User model.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                self.assertEqual(return_val, user_model)

        else:
            # Ldap submodule or credentials missing. Should return a TemplateResponse object.
            with self.subTest(''):
                # Invalid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_login_user_model(self.request, 'abc1234')
                self.assertTrue(isinstance(return_val, TemplateResponse))

                # Valid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                self.assertTrue(isinstance(return_val, TemplateResponse))

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test_get_or_create_wmu_user(self):

        # Check if LDAP is enabled. Test accordingly.
        if run_ldap_tests():
            # Ldap enabled. Should either return a WmuUser model, or None if invalid BroncoNet.
            with self.subTest('With invalid BroncoNet'):
                # Invalid BroncoNet. Should return None.
                return_val = get_or_create_wmu_user_model(self.request, 'abc1234')
                self.assertIsNone(return_val)

            with self.subTest('With valid BroncoNet, and corresponding model doesn\'t exist yet.'):
                # Valid BroncoNet. Should create and return new WmuUser model.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                user_model = models.WmuUser.objects.get(bronco_net=self.test_student_account)
                self.assertEqual(return_val, user_model)

            with self.subTest('With valid BroncoNet, and corresponding model already exists.'):
                # Valid BroncoNet. Should get and return existing WmuUser model.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                self.assertEqual(return_val, user_model)

        else:
            # Ldap submodule or credentials missing. Should return a TemplateResponse object.
            with self.subTest(''):
                # Invalid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_wmu_user_model(self.request, 'abc1234')
                self.assertTrue(isinstance(return_val, TemplateResponse))

                # Valid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                self.assertTrue(isinstance(return_val, TemplateResponse))
