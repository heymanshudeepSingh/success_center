"""
Tests for CAE Tools app.
"""

# System Imports.
import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

# User Class Imports.
from cae_home.tests.utils import IntegrationTestCase

# Module-level Variables.
from workspace.ldap_backends import simple_ldap_lib
from workspace.tests.utils import run_ldap_tests

cae_center_ldap_test_users = ['cae_director',
                              'cae_admin',
                              'cae_programmer',
                              'cae_admin_ga',
                              'cae_programmer_ga', ]


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
            reverse('cae_tools:ldap_utility'),
            'Login | CAE Center',
            expected_redirect_url=(
                reverse('cae_home:login') + '?next=' + reverse('cae_tools:ldap_utility')
            ),
        )

        # Test authenticated as whitelist user groups.
        whitelist_users = cae_center_ldap_test_users
        self.assertWhitelistUserAccess(
            reverse('cae_tools:ldap_utility'),
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
            reverse('cae_tools:ldap_utility'),
            None,
            blacklist_users,
            status=403,
        )
