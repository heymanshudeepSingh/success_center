"""
Tests for Settings app.
"""

# System Imports.
from django.conf import settings
from django.test import TestCase,TransactionTestCase
from django.core.management import call_command
from os import devnull


class DropOffCoreViewTests(TestCase, TransactionTestCase):
    """
    Tests to ensure valid settings values.
    """
    def test_debug_aliases(self):
        """
        Tests settings alias for DEBUG mode.

        As per "settings/extra_settings.py" file, note that Django's default DEBUG setting will always come back "False"
        when running UnitTests.

        The logic is that "there's no need to ever test development-specific things so we make it unavailable."
        Of course, for our project, that's not true, so we have instead aliased the setting to other variables, which
        will come back correctly based on tests.

        This test it to ensure all aliases come back as expected.
        """
        # Check based on DEV_URLS. Should be True when DEBUG is True.
        if settings.DEV_URLS is True:
            self.assertTrue(settings.DEV_MODE)
            self.assertTrue(settings.DEBUG_MODE)
            self.assertFalse(settings.PROD_MODE)
        else:
            self.assertFalse(settings.DEV_MODE)
            self.assertFalse(settings.DEBUG_MODE)
            self.assertTrue(settings.PROD_MODE)

        # Check based on DEV_MODE. Should be True when DEBUG is True.
        if settings.DEV_MODE is True:
            self.assertTrue(settings.DEV_URLS)
            self.assertTrue(settings.DEBUG_MODE)
            self.assertFalse(settings.PROD_MODE)
        else:
            self.assertFalse(settings.DEV_URLS)
            self.assertFalse(settings.DEBUG_MODE)
            self.assertTrue(settings.PROD_MODE)

        # Check based on DEBUG_MODE. Should be True when DEBUG is True.
        if settings.DEBUG_MODE is True:
            self.assertTrue(settings.DEV_URLS)
            self.assertTrue(settings.DEV_MODE)
            self.assertFalse(settings.PROD_MODE)
        else:
            self.assertFalse(settings.DEV_URLS)
            self.assertFalse(settings.DEV_MODE)
            self.assertTrue(settings.PROD_MODE)

        # Check based on PROD_MODE. Should be False when DEBUG is False.
        if settings.PROD_MODE:
            self.assertFalse(settings.DEV_URLS)
            self.assertFalse(settings.DEBUG_MODE)
            self.assertFalse(settings.DEV_MODE)
        else:
            self.assertTrue(settings.DEV_URLS)
            self.assertTrue(settings.DEBUG_MODE)
            self.assertTrue(settings.DEV_MODE)
