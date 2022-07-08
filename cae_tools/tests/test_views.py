"""
Tests for CAE Tools app.
"""

# System Imports.
import unittest
from django.contrib.auth import get_user_model
from django.urls import reverse

# User Imports.
from cae_home.tests.utils import IntegrationTestCase
from workspace.tests.utils import run_ldap_tests
from workspace.settings.reusable_settings import CAE_CENTER_GROUPS


@unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
class LdapUtilityTests(IntegrationTestCase):
    """
    Tests to ensure valid CAEWeb Shifts manager views.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Logic to initialize model/testing variable data.
        This is run exactly once, before any class tests are run.
        """
        # Call parent logic.
        super().setUpTestData()

    def test__ldap_utility_redirect(self):
        """
        Tests user cannot access ldap page without login.
        """
        # Test unauthenticated. Should lead to login page.
        self.assertGetResponse(
            reverse('cae_tools:padl_utility'),
            'Login | CAE Center',
            expected_redirect_url=(
                reverse('cae_home:login') + '?next=' + reverse('cae_tools:padl_utility')
            ),
        )

        # Test authenticated as whitelist user groups.
        whitelist_users = CAE_CENTER_GROUPS
        self.assertWhitelistUserAccess(
            reverse('cae_tools:padl_utility'),
            'LDAP | Search CAE Dev & Tools',
            whitelist_users,
            expected_content=[
                'LDAP | Search CAE Dev & Tools',
                'CAE LDAP User Info',
                'Search By:',
                'Value:',
            ],
        )

        # Test authenticated as blacklist user groups.
        blacklist_users = get_user_model().objects.filter(is_active=True).exclude(username__in=whitelist_users)
        self.assertBlacklistUserAccess(
            reverse('cae_tools:padl_utility'),
            None,
            blacklist_users,
            status=403,
        )
