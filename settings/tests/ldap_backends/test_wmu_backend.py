"""
Tests for CAE Home app Forms.
"""

# System Imports.
import unittest
from django.conf import settings
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from settings.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend


def are_ldap_test_values_populated():
    """
    Checks if "test ldap account" values are populated in local env file.
    Used to determine if Ldap tests should run or not.
    :return: Bool indicating if values are populated.
    """
    if str(settings.CAE_LDAP_TEST_NAME) != '' and str(settings.CAE_LDAP_TEST_PASS) != '':
        return True
    else:
        return False


class WmuAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper WMU Auth Backend implementation.
    """
    @classmethod
    def setUpTestData(cls):
        cls.wmu_backend = WmuAuthBackend()
        cls.current_time = timezone.now()
        cls.time_format = '%Y%m%d%H%M%S%z'

        # Get optional environment test account.
        if str(settings.CAE_LDAP_TEST_NAME) != '':
            cls.test_ldap_account_name = str(settings.CAE_LDAP_TEST_NAME)
        else:
            cls.test_ldap_account_name = None
        if str(settings.CAE_LDAP_TEST_PASS) != '':
            cls.test_ldap_account_pass = str(settings.CAE_LDAP_TEST_PASS)
        else:
            cls.test_ldap_account_pass = None

    #region User Create/Update Functions

    #endregion User Create/Update Functions

    #region User Ldap Status Functions

    @unittest.skipUnless(are_ldap_test_values_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__verify_user_ldap_status_wmu_enrolled(self):
        # Two possible test types, based on env values.
        if self.test_ldap_account_name == 'ceas_prog':
            # Using the CAE Programmers account. Verify that is active.
            user_is_active, user_in_retention = self.wmu_backend.verify_user_ldap_status(
                self.test_ldap_account_name,
                set_model_active_fields=False,
            )
            self.assertFalse(user_is_active)
            self.assertFalse(user_in_retention)
        else:
            # Probably using a personal account.
            # For now, we can assume the account is active and test the same as the CAE Programmer account.
            # But technically we have no way to verify the given user is active. May want to change in the future?
            user_is_active, user_in_retention = self.wmu_backend.verify_user_ldap_status(
                self.test_ldap_account_name,
                set_model_active_fields=False,
            )
            self.assertTrue(user_is_active)
            self.assertTrue(user_in_retention)

    def test___verify_user_ldap_status_wmu_enrolled(self):
        with self.subTest('With wmuEnrolled field True.'):
            ldap_info = {
                'wmuEnrolled': ['True'],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (True, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus False.'):
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': [''],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, False))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and currently employed.'):
            # Aka wmuEmployeeExpiration equal to or after current date.

            # Set to "2 days from now", to ensure it's after current date.
            employee_expiration = self.current_time + timezone.timedelta(days=2)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (True, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Student Retention period.'):
            # (Aka, wmuStudentExpiration before current date, but within 1 year.)

            # Set to "1 day ago" to check just having expired.
            student_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, True))

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            student_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Employee Retention period.'):
            # Aka, wmuEmployeeExpiration before current date, but within 1 year.

            # Set to "1 day ago" to check just having expired.
            employee_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, True))

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            employee_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within neither Retention period.'):
            # Aka, neither wmuStudentExpiration or wmuEmployeeExpiration within 1 year.

            # Set to "1 year and 2 days ago" to check just out of retention period.
            overall_expiration = self.current_time - timezone.timedelta(days=367)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [overall_expiration.strftime(self.time_format)],
                'wmuEmployeeExpiration': [overall_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status(ldap_info), (False, False))

    #endregion User Ldap Status Functions

    #region Ldap Get Attr Functions

    @unittest.skipUnless(are_ldap_test_values_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test___get_all_user_info_from_bronconet(self):
        # Get ldap results.
        ldap_results = self.wmu_backend._get_all_user_info_from_bronconet(self.test_ldap_account_name)

        # Two possible test types, based on env values.
        if self.test_ldap_account_name == 'ceas_prog':
            # Using the CAE Programmers account. Slightly more thorough testing.
            # Mostly just test a few common values to make sure we retrieved them.
            self.assertIsNotNone(ldap_results)
            self.assertEqual(len(ldap_results), 29)
            self.assertEqual(ldap_results['uid'][0], self.test_ldap_account_name)
            self.assertEqual(ldap_results['sn'][0], 'Programmers')
            self.assertEqual(ldap_results['givenName'][0], 'CAE')
            self.assertEqual(ldap_results['gecos'][0], 'Programmers, CAE')
            self.assertEqual(ldap_results['displayName'][0], 'Programmers, CAE')
            self.assertEqual(ldap_results['mail'][0], 'cae-programmers@wmich.edu')
            self.assertEqual(ldap_results['inetUserStatus'][0], 'active')
        else:
            # Probably using a personal account. For privacy reasons, we can only test so much.
            self.assertIsNotNone(ldap_results)
            self.assertGreater(len(ldap_results), 0)
            self.assertEqual(ldap_results['uid'][0], self.test_ldap_account_name)
            self.assertEqual(ldap_results['mail'][0][-10:], '@wmich.edu')

    @unittest.skipUnless(are_ldap_test_values_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test___get_all_user_info_from_winno(self):
        # Two possible test types, based on env values.
        if self.test_ldap_account_name == 'ceas_prog':
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')
        else:
            # Get ldap results.
            ldap_results = self.wmu_backend._get_all_user_info_from_winno(self.test_ldap_account_name)

            # Probably using a personal account. For privacy reasons, we can only test so much.
            self.assertIsNotNone(ldap_results)
            self.assertGreater(len(ldap_results), 0)
            self.assertEqual(ldap_results['uid'][0], self.test_ldap_account_name)
            self.assertEqual(ldap_results['mail'][0][-10:], '@wmich.edu')

    @unittest.skipUnless(are_ldap_test_values_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__get_winno_from_bronconet(self):
        # Two possible test types, based on env values.
        if self.test_ldap_account_name == 'ceas_prog':
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')
        else:
            # Get ldap Winno.
            winno = self.wmu_backend.get_winno_from_bronconet(self.test_ldap_account_name)

            # Probably using a personal account. For privacy reasons, we can only test so much.
            # Check that we got a Winno.
            self.assertIsNotNone(winno)

            # Get value and assert it has characters?
            # Not sure what else we can test without direct comparison.
            self.assertGreater(len(winno), 0)

    @unittest.skipUnless(are_ldap_test_values_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__get_bronconet_from_winno(self):

        # Two possible test types, based on env values.
        if self.test_ldap_account_name == 'ceas_prog':
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')
        else:
            # Get ldap Winno to test with.
            winno = self.wmu_backend.get_winno_from_bronconet(self.test_ldap_account_name)

            # Verify we got a Winno back.
            self.assertIsNotNone(winno)

            # Get ldap BroncoNet.
            bronco_net = self.wmu_backend.get_bronconet_from_winno(winno)

            # Probably using a personal account. For privacy reasons, we can only test so much.
            # Check that we got a BroncoNet.
            self.assertIsNotNone(bronco_net)

            # Verify match.
            self.assertEqual(bronco_net, self.test_ldap_account_name)

    #endregion Ldap Get Attr Functions
