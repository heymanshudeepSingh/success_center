"""
Tests for CAE Home app Views.
"""

# System Imports.
from django.apps import apps
from django.conf import settings
from django_expanded_test_cases import IntegrationTestCase
from django.urls import reverse
from unittest.mock import patch

# User Imports.
from cae_home.management.commands.seeders.user import create_groups, create_permission_group_users


class CAEHomeViewTests(IntegrationTestCase):
    """
    Tests to ensure CaeHome views load as expected.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Logic to initialize model/testing variable data.
        This is run exactly once, before any class tests are run.
        """
        # Call parent logic.
        super().setUpTestData()

        # Get list of all installed apps.
        cls.installed_app_list = [app.label for app in apps.get_app_configs()]

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Call parent logic.
        super().setUp()

        # Initialize user and group models.
        create_groups()
        create_permission_group_users()

    def test_login_page(self):
        """
        Tests login view.
        """
        # Test unauthenticated.
        self.assertGetResponse(
            'cae_home:login',
            auto_login=False,
            expected_title='Login | CAE Center',
            expected_header='Login',
            expected_content=[
                'Username:',
                'Password:',
                'Keep Me Logged In:',
                'Submit',
            ],
        )


        # # Test authenticated as various users.
        # if 'cae_web_core' in self.installed_app_list:
        #     # Test CAE Web login redirects.
        #     with self.subTest('Test Login View when already logged in as CAE Director user.'):
        #         self.client.login(username='cae_director', password='test')
        #         response = self.client.get(reverse('cae_home:login'))
        #         self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #         # Quickly check template.
        #         response = self.client.get(reverse('cae_home:login'), follow=True)
        #         self.assertContains(response, 'Employee Shift Stats')
        #
        #     with self.subTest('Test Login View when already logged in as CAE Building Coordinator user.'):
        #         self.client.login(username='cae_building_coordinator', password='test')
        #         response = self.client.get(reverse('cae_home:login'))
        #         self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #         # Quickly check template.
        #         response = self.client.get(reverse('cae_home:login'), follow=True)
        #         self.assertContains(response, 'Employee Shift Stats')
        #
        #     with self.subTest('Test Login View when already logged in as CAE Attendant user.'):
        #         self.client.login(username='cae_attendant', password='test')
        #         response = self.client.get(reverse('cae_home:login'))
        #         self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #         # Quickly check template.
        #         response = self.client.get(reverse('cae_home:login'), follow=True)
        #         self.assertContains(response, 'CAE Center Contact Info')
        #
        #     with self.subTest('Test Login View when already logged in as CAE Admin user.'):
        #         self.client.login(username='cae_admin', password='test')
        #         response = self.client.get(reverse('cae_home:login'))
        #         self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #         # Quickly check template.
        #         response = self.client.get(reverse('cae_home:login'), follow=True)
        #         self.assertContains(response, 'Employee Shift Stats')
        #
        #     if settings.DEV_URLS:
        #         # Test in development mode.
        #         with self.subTest('Test Login View when already logged in as CAE Programmer user.'):
        #             self.client.login(username='cae_programmer', password='test')
        #             response = self.client.get(reverse('cae_home:login'))
        #             self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #             # Quickly check template.
        #             response = self.client.get(reverse('cae_home:login'), follow=True)
        #             self.assertContains(response, 'CAE Home Index Page')
        #     else:
        #         # Test in production mode.
        #         with self.subTest('Test Login View when already logged in as CAE Programmer user.'):
        #             self.client.login(username='cae_programmer', password='test')
        #             response = self.client.get(reverse('cae_home:login'))
        #             self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)
        #
        #             # Quickly check template.
        #             response = self.client.get(reverse('cae_home:login'), follow=True)
        #             self.assertContains(response, 'Employee Shift Stats')

    # def test_login_redirect(self):
    #     """
    #     Tests login_redirect view.
    #     """
    #     # Test unauthenticated.
    #     response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #     self.assertRedirects(response, reverse('cae_home:login'))
    #
    #     # Quickly check template.
    #     self.assertContains(response, 'Login')
    #     self.assertContains(response, 'Username:')
    #
    #     # Test authenticated.
    #     if 'cae_web_core' in self.installed_app_list:
    #         # Test CAE Web login redirects.
    #         with self.subTest('Test Login_Redirect View with CAE Director user.'):
    #             self.client.login(username='cae_director', password='test')
    #             response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_shifts:stats'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'Employee Shift Stats')
    #
    #         with self.subTest('Test Login_Redirect View with CAE Building Coordinator user.'):
    #             self.client.login(username='cae_building_coordinator', password='test')
    #             response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_shifts:stats'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'Employee Shift Stats')
    #
    #         with self.subTest('Test Login_Redirect View with CAE Attendant user.'):
    #             self.client.login(username='cae_attendant', password='test')
    #             response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'CAE Center Contact Info')
    #
    #         with self.subTest('Test Login_Redirect View with CAE Admin user.'):
    #             self.client.login(username='cae_admin', password='test')
    #             response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_shifts:stats'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'Employee Shift Stats')
    #
    #         if settings.DEV_URLS:
    #             # Test in development mode.
    #             with self.subTest('Test Login_Redirect View with CAE Programmer user.'):
    #                 self.client.login(username='cae_programmer', password='test')
    #                 response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #                 self.assertRedirects(response, reverse('cae_home:index'))
    #
    #                 # Quickly check template.
    #                 self.assertContains(response, 'CAE Home Index Page')
    #         else:
    #             # Test in production mode.
    #             with self.subTest('Test Login_Redirect View with CAE Programmer user.'):
    #                 self.client.login(username='cae_programmer', password='test')
    #                 response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
    #                 self.assertRedirects(response, reverse('cae_web_shifts:stats'))
    #
    #                 # Quickly check template.
    #                 self.assertContains(response, 'Employee Shift Stats')
    #
    # def test_logout(self):
    #     """
    #     Tests logout view.
    #     """
    #     # Test unauthenticated.
    #     response = self.client.get(reverse('cae_home:logout'))
    #     self.assertRedirects(response, reverse('cae_home:login'))
    #
    #     # Test authenticated.
    #     if 'cae_web_core' in self.installed_app_list:
    #         # Test CAE Web login redirects.
    #         with self.subTest('Test Logout View with CAE Director user.'):
    #             self.client.login(username='cae_director', password='test')
    #             response = self.client.get(reverse('cae_home:logout'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'CAE Center Contact Info')
    #
    #         with self.subTest('Test Logout View with CAE Building Coordinator user.'):
    #             self.client.login(username='cae_building_coordinator', password='test')
    #             response = self.client.get(reverse('cae_home:logout'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'CAE Center Contact Info')
    #
    #         with self.subTest('Test Logout View with CAE Attendant user.'):
    #             self.client.login(username='cae_attendant', password='test')
    #             response = self.client.get(reverse('cae_home:logout'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'CAE Center Contact Info')
    #
    #         with self.subTest('Test Logout View with CAE Admin user.'):
    #             self.client.login(username='cae_admin', password='test')
    #             response = self.client.get(reverse('cae_home:logout'), follow=True)
    #             self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #             # Quickly check template.
    #             self.assertContains(response, 'CAE Center Contact Info')
    #
    #         if settings.DEV_URLS:
    #             # Test in development mode.
    #             with self.subTest('Test Logout View with CAE Programmer user.'):
    #                 self.client.login(username='cae_programmer', password='test')
    #                 response = self.client.get(reverse('cae_home:logout'), follow=True)
    #                 self.assertRedirects(response, reverse('cae_home:index'))
    #
    #                 # Quickly check template.
    #                 self.assertContains(response, 'CAE Home Index Page')
    #         else:
    #             # Test in production mode.
    #             with self.subTest('Test Logout View with CAE Programmer user.'):
    #                 self.client.login(username='cae_programmer', password='test')
    #                 response = self.client.get(reverse('cae_home:logout'), follow=True)
    #                 self.assertRedirects(response, reverse('cae_web_core:index'))
    #
    #                 # Quickly check template.
    #                 self.assertContains(response, 'CAE Center Contact Info')
    #
    # def test_profile_edit(self):
    #     """
    #     Tests profile edit view.
    #     """
    #     # Test unauthenticated.
    #     user = self.get_user('cae_admin', password='test')
    #     slug = user.userintermediary.slug
    #     response = self.client.get(reverse('cae_home:user_edit'))
    #     self.assertRedirects(
    #         response,
    #         reverse('cae_home:login') + '?next=' + reverse('cae_home:user_edit')
    #     )
    #
    #     # Quickly check template.
    #     response = self.client.get(reverse('cae_home:user_edit'), follow=True)
    #     self.assertContains(response, 'Login')
    #     self.assertContains(response, 'Username:')
    #
    #     # Test authenticated.
    #     self.client.login(username=user.username, password=user.password_string)
    #     response = self.client.get(reverse('cae_home:user_edit'))
    #     self.assertTrue(response.status_code, 200)
    #
    #     # Quickly check template.
    #     self.assertContains(response, 'Edit User {0}'.format(user.username))

    # region Dev View Tests

    def test_index(self):
        """
        Tests the core index of the site.
        This should only be accessible in development environments.
        """
        # Page refers to dev-only urls. Thus only test in development environments.
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:index'))
            self.assertEqual(response.status_code, 200)

            # Quickly check template.
            self.assertContains(response, 'CAE Home Index Page')

    # @patch('django_expanded_test_cases.test_cases.integration_test_case.ETC_ALLOW_MESSAGE_PARTIALS', True)
    def test_internal_dev_index(self):
        """
        Test the internal (cae_home) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:internal_dev_index'))
            self.assertEqual(response.status_code, 302)

            # # Quickly check template.
            # self.assertContains(response, 'CAE Home CSS Examples')

    def test_external_dev_index(self):
        """
        Test the external (wmu) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:external_dev_index'))
            self.assertEqual(response.status_code, 200)

            # Quickly check template.
            self.assertContains(response, 'WMU Index Page')

    # endregion Dev View Tests
