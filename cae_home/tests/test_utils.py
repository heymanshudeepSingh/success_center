"""
Tests for CAE Home app utils.

Files located at:
* cae_home/utils.py
* cae_home/tests/utils.py

Not to be confused with literal cae_home/tests/utils.py file, which provides extra overall utility logic for testing.
"""

# System Imports.
import logging, unittest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
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


# Module Variables.
default_password = settings.USER_SEED_PASSWORD


class CAEHomeUtilsTests(IntegrationTestCase):
    """
    Tests to ensure util logic functions as expected.
    Tested logic is from "cae_home/tests/utils.py - IntegrationTestCase" class.
    """
    @classmethod
    def setUpTestData(cls):
        # Run parent setup logic.
        super().setUpTestData()

        # Create general user groups.
        create_groups()

    def test_create_user(self):
        """
        Tests create_user() utility function.
        """
        with self.subTest('Basic user creation'):
            test_user_1 = self.create_user('test_user_1')

            # Verify user created.
            self.assertTrue(isinstance(test_user_1, get_user_model()))
            self.assertEqual(test_user_1.username, 'test_user_1')

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_1, 'password_string'))
            self.assertEqual(test_user_1.password_string, default_password)

            # Verify user Permissions. Should have none.
            self.assertEqual(len(test_user_1.user_permissions.all()), 0)

            # Verify user Groups. Should have none.
            self.assertEqual(len(test_user_1.groups.all()), 0)

        with self.subTest('With different password'):
            password = 'newTestValue12345'
            test_user_2 = self.create_user('test_user_2', password=password)

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_2, 'password_string'))
            self.assertEqual(test_user_2.password_string, password)

            # Verify user Permissions. Should have none.
            self.assertEqual(len(test_user_2.user_permissions.all()), 0)

            # Verify user Groups. Should have none.
            self.assertEqual(len(test_user_2.groups.all()), 0)

        with self.subTest('With single permission added'):
            test_user_3 = self.create_user('test_user_3', permissions='add_permission')

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_3, 'password_string'))
            self.assertEqual(test_user_3.password_string, default_password)

            # Verify added user Permissions.
            user_permission_list = test_user_3.user_permissions.all()
            self.assertEqual(len(user_permission_list), 1)
            self.assertIn(Permission.objects.get(codename='add_permission'), user_permission_list)

            # Verify user Groups. Should have none.
            self.assertEqual(len(test_user_3.groups.all()), 0)

        with self.subTest('With permission set added'):
            test_user_4 = self.create_user(
                'test_user_4',
                permissions=['add_permission', 'change_permission', 'delete_permission'],
            )

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_4, 'password_string'))
            self.assertEqual(test_user_4.password_string, default_password)

            # Verify added user Permissions.
            user_permission_list = test_user_4.user_permissions.all()
            self.assertEqual(len(user_permission_list), 3)
            self.assertIn(Permission.objects.get(codename='add_permission'), user_permission_list)
            self.assertIn(Permission.objects.get(codename='change_permission'), user_permission_list)
            self.assertIn(Permission.objects.get(codename='delete_permission'), user_permission_list)

            # Verify user Groups. Should have none.
            self.assertEqual(len(test_user_4.groups.all()), 0)

        with self.subTest('With single group added'):
            test_user_5 = self.create_user('test_user_5', groups='CAE Admin')

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_5, 'password_string'))
            self.assertEqual(test_user_5.password_string, default_password)

            # Verify direct user Permissions. Should have none (but note that group itself does have associated perms).
            self.assertEqual(len(test_user_2.user_permissions.all()), 0)

            # Verify added user Groups.
            user_group_list = test_user_5.groups.all()
            self.assertEqual(len(user_group_list), 1)
            self.assertIn(Group.objects.get(name='CAE Admin'), user_group_list)

        with self.subTest('With group set added'):
            test_user_6 = self.create_user(
                'test_user_6',
                groups=['CAE Admin', 'CAE Attendant', 'CAE Programmer'],
            )

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user_6, 'password_string'))
            self.assertEqual(test_user_6.password_string, default_password)

            # Verify user Permissions. Should have none.
            self.assertEqual(len(test_user_2.user_permissions.all()), 0)

            # Verify added user Groups.
            user_group_list = test_user_6.groups.all()
            self.assertEqual(len(user_group_list), 3)
            self.assertIn(Group.objects.get(name='CAE Admin'), user_group_list)
            self.assertIn(Group.objects.get(name='CAE Attendant'), user_group_list)
            self.assertIn(Group.objects.get(name='CAE Programmer'), user_group_list)

    def test_get_user(self):
        """
        Tests get_user() utility function.
        """
        # Create test user.
        test_user = self.create_user('test_user')

        with self.subTest('Success - With User model value'):
            return_value = self.get_user(test_user)

            # Verify models match.
            self.assertEqual(test_user, return_value)

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user, 'password_string'))
            self.assertTrue(test_user.password_string, default_password)

        with self.subTest('Success - With username value'):
            return_value = self.get_user('test_user')

            # Verify models match.
            self.assertEqual(test_user, return_value)

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(test_user, 'password_string'))
            self.assertTrue(test_user.password_string, default_password)

        with self.subTest('Success - Different password'):
            password = 'newTestValue12345'
            return_value = self.get_user('test_user', password=password)

            # Verify models match.
            self.assertEqual(test_user, return_value)

            # Verify password string. Used for easy view testing in other tests.
            self.assertTrue(hasattr(return_value, 'password_string'))
            self.assertTrue(return_value.password_string, password)

        with self.subTest('Failure - User does not exist'):
            with self.assertRaises(get_user_model().DoesNotExist):
                self.get_user('Bad Value')

        with self.subTest('Failure - With iterable values'):
            # Pass list.
            with self.assertRaises(TypeError):
                self.get_user([1, 2, 3])

            # Pass tuple.
            with self.assertRaises(TypeError):
                self.get_user((1, 2, 3))

            # Pass queryset.
            with self.assertRaises(TypeError):
                self.get_user(get_user_model().objects.all())

    def test_add_user_permission(self):
        """
        Tests add_user_permission() utility function.
        """
        test_user = self.create_user('test_user')

        # Verify starting with no permissions.
        self.assertEqual(len(test_user.user_permissions.all()), 0)

        with self.subTest('With Permission model value'):
            self.add_user_permission(Permission.objects.get(codename='add_permission'), test_user)

            # Verify permission added.
            user_permission_list = test_user.user_permissions.all()
            self.assertEqual(len(user_permission_list), 1)
            self.assertIn(Permission.objects.get(codename='add_permission'), user_permission_list)

        with self.subTest('With codename value'):
            self.add_user_permission('change_permission', test_user)

            # Verify permission added.
            user_permission_list = test_user.user_permissions.all()
            self.assertEqual(len(user_permission_list), 2)
            self.assertIn(Permission.objects.get(codename='add_permission'), user_permission_list)
            self.assertIn(Permission.objects.get(codename='change_permission'), user_permission_list)

        with self.subTest('With name value'):
            self.add_user_permission('Can delete permission', test_user)

            # Verify permission added.
            user_permission_list = test_user.user_permissions.all()
            self.assertEqual(len(user_permission_list), 3)
            self.assertIn(Permission.objects.get(codename='add_permission'), user_permission_list)
            self.assertIn(Permission.objects.get(codename='change_permission'), user_permission_list)
            self.assertIn(Permission.objects.get(codename='delete_permission'), user_permission_list)

        with self.subTest('Permission does not exist'):
            with self.assertRaises(Permission.DoesNotExist):
                self.add_user_permission('Bad Value', test_user)

        with self.subTest('User does not exist'):
            with self.assertRaises(get_user_model().DoesNotExist):
                self.add_user_permission('add_permission', 'Bad Value')

    def test_add_user_group(self):
        """
        Tests add_user_group() utility function.
        """
        test_user = self.create_user('test_user')

        # Verify starting with no groups.
        self.assertEqual(len(test_user.groups.all()), 0)

        with self.subTest('With Group model value'):
            self.add_user_group(Group.objects.get(name='CAE Admin'), test_user)

            # Verify permission added.
            user_group_list = test_user.groups.all()
            self.assertEqual(len(user_group_list), 1)
            self.assertIn(Group.objects.get(name='CAE Admin'), user_group_list)

        with self.subTest('With name value'):
            self.add_user_group('CAE Attendant', test_user)

            # Verify permission added.
            user_group_list = test_user.groups.all()
            self.assertEqual(len(user_group_list), 2)
            self.assertIn(Group.objects.get(name='CAE Admin'), user_group_list)
            self.assertIn(Group.objects.get(name='CAE Attendant'), user_group_list)

        with self.subTest('Group does not exist'):
            with self.assertRaises(Group.DoesNotExist):
                self.add_user_group('Bad Value', test_user)

        with self.subTest('User does not exist'):
            with self.assertRaises(get_user_model().DoesNotExist):
                self.add_user_group('CAE Admin', 'Bad Value')


class CAEHomeViewTests(IntegrationTestCase):
    """
    Tests to ensure views load as expected.
    Tested logic is from file "cae_home/utils.py".
    """
    @classmethod
    def setUpTestData(cls):
        # Run parent setup logic.
        super().setUpTestData()

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
        """
        Test for LDAP get_or_create_login_user() utility function, which either gets or creates a (Login) User model,
        using LDAP data.
        """
        # Check if LDAP is enabled. Test accordingly.
        if run_ldap_tests():
            # Ldap enabled. Should either return a (login) User model, or None if invalid BroncoNet.
            with self.subTest('Ldap enabled, with invalid BroncoNet'):
                # Invalid BroncoNet. Should return None.
                return_val = get_or_create_login_user_model(self.request, 'abc1234')
                self.assertIsNone(return_val)

            with self.subTest('Ldap enabled, with valid BroncoNet, and corresponding model doesn\'t exist yet.'):
                # Valid BroncoNet. Should create and return new User model.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                user_model = models.User.objects.get(username=self.test_student_account)
                self.assertEqual(return_val, user_model)

            with self.subTest('Ldap enabled, with valid BroncoNet, and corresponding model already exists.'):
                # Valid BroncoNet. Should get and return existing User model.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                self.assertEqual(return_val, user_model)

        else:
            # Ldap submodule or credentials missing. Should return a TemplateResponse object.
            with self.subTest('Ldap not enabled.'):
                # Invalid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_login_user_model(self.request, 'abc1234')
                self.assertTrue(isinstance(return_val, TemplateResponse))

                # Valid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_login_user_model(self.request, self.test_student_account)
                self.assertTrue(isinstance(return_val, TemplateResponse))

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test_get_or_create_wmu_user(self):
        """
        Test for LDAP get_or_create_wmu_user() utility function, which either gets or creates a WmuUser model,
        using LDAP data.
        """
        # Check if LDAP is enabled. Test accordingly.
        if run_ldap_tests():
            # Ldap enabled. Should either return a WmuUser model, or None if invalid BroncoNet.
            with self.subTest('Ldap enabled, with invalid BroncoNet'):
                # Invalid BroncoNet. Should return None.
                return_val = get_or_create_wmu_user_model(self.request, 'abc1234')
                self.assertIsNone(return_val)

            with self.subTest('Ldap enabled, with valid BroncoNet, and corresponding model doesn\'t exist yet.'):
                # Valid BroncoNet. Should create and return new WmuUser model.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                user_model = models.WmuUser.objects.get(bronco_net=self.test_student_account)
                self.assertEqual(return_val, user_model)

            with self.subTest('Ldap enabled, with valid BroncoNet, and corresponding model already exists.'):
                # Valid BroncoNet. Should get and return existing WmuUser model.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                self.assertEqual(return_val, user_model)

        else:
            # Ldap submodule or credentials missing. Should return a TemplateResponse object.
            with self.subTest('Ldap not enabled.'):
                # Invalid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_wmu_user_model(self.request, 'abc1234')
                self.assertTrue(isinstance(return_val, TemplateResponse))

                # Valid BroncoNet. But Ldap not set up so should return TemplateResponse.
                return_val = get_or_create_wmu_user_model(self.request, self.test_student_account)
                self.assertTrue(isinstance(return_val, TemplateResponse))
