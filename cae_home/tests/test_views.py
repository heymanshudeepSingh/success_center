"""
Tests for CAE_Home Views.
"""

from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from os import devnull

from cae_home.management.commands.seeders.user import create_groups, create_permission_group_users


class CAEHomeViewTests(TestCase):
    """
    Tests to ensure views load as expected.
    """
    @classmethod
    def setUpTestData(cls):
        # Get list of all installed apps.
        cls.installed_app_list = [app.label for app in apps.get_app_configs()]

        # Load all relevant fixtures.
        create_groups()
        create_permission_group_users(default_password='test')
        with open(devnull, 'a') as null:
            call_command('loaddata', 'full_models/site_themes', stdout=null)

        # Create models.
        cls.user = get_user_model().objects.create_user('test', '', 'test')

    def test_login(self):
        """
        Tests login view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_home:login'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Username:')

        # Test authenticated.
        if 'cae_web_core' in self.installed_app_list:
            # Test CAE Web login redirects.
            with self.subTest('Test Login View with CAE Director user.'):
                self.client.login(username='cae_director', password='test')
                response = self.client.get(reverse('cae_home:login'))
                self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                # Quickly check template.
                response = self.client.get(reverse('cae_home:login'), follow=True)
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login View with CAE Building Coordinator user.'):
                self.client.login(username='cae_building_coordinator', password='test')
                response = self.client.get(reverse('cae_home:login'))
                self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                # Quickly check template.
                response = self.client.get(reverse('cae_home:login'), follow=True)
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login View with CAE Attendant user.'):
                self.client.login(username='cae_attendant', password='test')
                response = self.client.get(reverse('cae_home:login'))
                self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                # Quickly check template.
                response = self.client.get(reverse('cae_home:login'), follow=True)
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login View with CAE Admin user.'):
                self.client.login(username='cae_admin', password='test')
                response = self.client.get(reverse('cae_home:login'))
                self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                # Quickly check template.
                response = self.client.get(reverse('cae_home:login'), follow=True)
                self.assertContains(response, 'CAE Center Contact Info')

            if settings.DEV_URLS:
                # Test in development mode.
                with self.subTest('Test Login View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:login'))
                    self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                    # Quickly check template.
                    response = self.client.get(reverse('cae_home:login'), follow=True)
                    self.assertContains(response, 'CAE Home Index Page')
            else:
                # Test in production mode.
                with self.subTest('Test Login View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:login'))
                    self.assertRedirects(response, reverse('cae_home:login_redirect'), target_status_code=302)

                    # Quickly check template.
                    response = self.client.get(reverse('cae_home:login'), follow=True)
                    self.assertContains(response, 'CAE Center Contact Info')

    def test_login_redirect(self):
        """
        Tests login_redirect view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
        self.assertRedirects(response, reverse('cae_home:login'))

        # Quickly check template.
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Username:')

        # Test authenticated.
        if 'cae_web_core' in self.installed_app_list:
            # Test CAE Web login redirects.
            with self.subTest('Test Login_Redirect View with CAE Director user.'):
                self.client.login(username='cae_director', password='test')
                response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login_Redirect View with CAE Building Coordinator user.'):
                self.client.login(username='cae_building_coordinator', password='test')
                response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login_Redirect View with CAE Attendant user.'):
                self.client.login(username='cae_attendant', password='test')
                response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Login_Redirect View with CAE Admin user.'):
                self.client.login(username='cae_admin', password='test')
                response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            if settings.DEV_URLS:
                # Test in development mode.
                with self.subTest('Test Login_Redirect View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                    self.assertRedirects(response, reverse('cae_home:index'))

                    # Quickly check template.
                    self.assertContains(response, 'CAE Home Index Page')
            else:
                # Test in production mode.
                with self.subTest('Test Login_Redirect View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:login_redirect'), follow=True)
                    self.assertRedirects(response, reverse('cae_web_core:index'))

                    # Quickly check template.
                    self.assertContains(response, 'CAE Center Contact Info')

    def test_logout(self):
        """
        Tests logout view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_home:logout'))
        self.assertRedirects(response, reverse('cae_home:login'))

        # Test authenticated.
        if 'cae_web_core' in self.installed_app_list:
            # Test CAE Web login redirects.
            with self.subTest('Test Logout View with CAE Director user.'):
                self.client.login(username='cae_director', password='test')
                response = self.client.get(reverse('cae_home:logout'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Logout View with CAE Building Coordinator user.'):
                self.client.login(username='cae_building_coordinator', password='test')
                response = self.client.get(reverse('cae_home:logout'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Logout View with CAE Attendant user.'):
                self.client.login(username='cae_attendant', password='test')
                response = self.client.get(reverse('cae_home:logout'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            with self.subTest('Test Logout View with CAE Admin user.'):
                self.client.login(username='cae_admin', password='test')
                response = self.client.get(reverse('cae_home:logout'), follow=True)
                self.assertRedirects(response, reverse('cae_web_core:index'))

                # Quickly check template.
                self.assertContains(response, 'CAE Center Contact Info')

            if settings.DEV_URLS:
                # Test in development mode.
                with self.subTest('Test Logout View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:logout'), follow=True)
                    self.assertRedirects(response, reverse('cae_home:index'))

                    # Quickly check template.
                    self.assertContains(response, 'CAE Home Index Page')
            else:
                # Test in production mode.
                with self.subTest('Test Logout View with CAE Programmer user.'):
                    self.client.login(username='cae_programmer', password='test')
                    response = self.client.get(reverse('cae_home:logout'), follow=True)
                    self.assertRedirects(response, reverse('cae_web_core:index'))

                    # Quickly check template.
                    self.assertContains(response, 'CAE Center Contact Info')


    #region Dev View Tests

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

    def test_internal_dev_index(self):
        """
        Test the internal (cae_home) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:internal_dev_index'))
            self.assertEqual(response.status_code, 200)

            # Quickly check template.
            self.assertContains(response, 'CAE Home CSS Examples')

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

    #endregion Dev View Tests
