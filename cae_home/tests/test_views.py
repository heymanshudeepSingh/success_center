"""
Tests for CAE_Home Views.
"""

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from os import devnull

from cae_home.management.commands.seeders.user import create_groups


class CAEHomeViewTests(TestCase):
    """
    Tests to ensure views load as expected.
    """
    @classmethod
    def setUpTestData(cls):
        # Load all relevant fixtures.
        create_groups()
        with open(devnull, 'a') as null:
            call_command('loaddata', 'full_models/site_themes', stdout=null)

        # Create models.
        cls.user = get_user_model().objects.create_user('test', '', 'test')


    def test_login(self):
        """
        Tests login and auth views.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_home:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

        # response = self.client.get(reverse('cae_home:login_redirect'))
        # self.assertRedirects(response, reverse('cae_home:login'))
        # response = self.client.get(reverse('cae_home:logout'))
        # self.assertRedirects(response, reverse('cae_home:login'))
        #
        # # Test authenticated.
        # self.client.login(username='test', password='test')
        # response = self.client.get(reverse('cae_home:login'))
        # self.assertRedirects(response, reverse('cae_home:login_redirect'))
        #
        # response = self.client.get(reverse('cae_home:login_redirect'))
        # self.assertRedirects(response, reverse('cae_home:index'))
        #
        # response = self.client.get(reverse('cae_home:logout'))
        # self.assertRedirects(response, reverse('cae_home:index'))

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

    def test_internal_dev_index(self):
        """
        Test the internal (cae_home) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:internal_dev_index'))
            self.assertEqual(response.status_code, 200)

    def test_external_dev_index(self):
        """
        Test the external (wmu) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:external_dev_index'))
            self.assertEqual(response.status_code, 200)

    #endregion Dev View Tests
