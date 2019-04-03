"""
Tests for CAE_Home Home Views.
"""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .. import models


class HomeViewTests(TestCase):
    """
    Tests to ensure views load as expected.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_theme = models.SiteTheme.objects.create(name='wmu', slug='wmu')

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
