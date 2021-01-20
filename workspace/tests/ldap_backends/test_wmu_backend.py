"""
Tests for Wmu Authentication Backend.
"""

# System Imports.
import unittest
from django.conf import settings
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from workspace.tests.utils import (
    run_ldap_tests,
    prog_or_student_test_account_is_populated,
    prog_test_account_is_populated,
    student_test_account_is_populated
)
if run_ldap_tests():
    from workspace.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend


class WmuAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper WMU Auth Backend implementation.
    """
    @classmethod
    def setUpTestData(cls):
        if run_ldap_tests():
            cls.wmu_backend = WmuAuthBackend()
            cls.current_time = timezone.now()
            cls.time_format = '%Y%m%d%H%M%S%z'

            # Get optional environment test accounts.
            if prog_test_account_is_populated():
                cls.test_ceas_prog_account = str(settings.BACKEND_LDAP_TEST_PROG_ID)
            if student_test_account_is_populated():
                cls.test_student_account = str(settings.BACKEND_LDAP_TEST_STUDENT_ID)

    #region User Create/Update Functions

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__create_user_model(self):
        """
        To reduce calls to main campus Ldap during testing, we'll test "create", "update", "create_or_update" functions
        here.

        Note that this method should only be called after user is validated. Thus, password is not used for
        authentication at this point, and is only needed so it can be associated with the user model, if the local
        settings permit such.
        """
        # Get initial values.
        bronco_net = settings.BACKEND_LDAP_TEST_STUDENT_ID
        fake_pass = settings.USER_SEED_PASSWORD

        # Create user model.
        login_user = self.wmu_backend.create_or_update_user_model(bronco_net, fake_pass)

        # Check that we got back what we expected.
        self.assertTrue(isinstance(login_user, models.User))
        self.assertEqual(login_user.username, bronco_net)
        self.assertTrue(login_user.is_active)

        # Now update.
        updated_login_user = self.wmu_backend.create_or_update_user_model(bronco_net, fake_pass)

        # Check that returned value is the same as original (I'm not sure how else to test without knowing what student
        # we're accessing).
        self.assertEqual(updated_login_user, login_user)

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__create_wmu_user_model(self):
        """
        To reduce calls to main campus Ldap during testing, we'll test "create", "update", "create_or_update" functions
        here.

        Note that this method should only be called after user is validated. Thus, password is not used for
        authentication at this point, and is only needed so it can be associated with the user model, if the local
        settings permit such.
        """
        # Get initial values.
        bronco_net = settings.BACKEND_LDAP_TEST_STUDENT_ID
        fake_pass = settings.USER_SEED_PASSWORD

        # Create user model.
        wmu_user = self.wmu_backend.create_or_update_wmu_user_model(bronco_net, fake_pass)

        # Check that we got back what we expected.
        self.assertTrue(isinstance(wmu_user, models.WmuUser))
        self.assertEqual(wmu_user.bronco_net, bronco_net)
        self.assertGreater(len(wmu_user.winno), 7)
        self.assertEqual(wmu_user.is_active, True)
        self.assertGreater(len(wmu_user.major.all()), 0)

        # Now update.
        updated_wmu_user = self.wmu_backend.create_or_update_wmu_user_model(bronco_net, fake_pass)

        # Check that returned value is the same as original (I'm not sure how else to test without knowing what student
        # we're accessing).
        self.assertEqual(updated_wmu_user, wmu_user)

    #endregion User Create/Update Functions

    #region User Ldap Status Functions

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__verify_user_ldap_status_wmu_enrolled(self):
        # Tests based on CAE Center programmer account.
        if prog_test_account_is_populated():
            # Using the CAE Programmers account. Verify status.
            user_is_active, user_in_retention = self.wmu_backend.verify_user_ldap_status(
                self.test_ceas_prog_account,
                set_model_active_fields=False,
            )
            self.assertFalse(user_is_active)
            self.assertFalse(user_in_retention)

        # Tests based on active Student account.
        if student_test_account_is_populated():
            # Using an active student account. Verify status.
            user_is_active, user_in_retention = self.wmu_backend.verify_user_ldap_status(
                self.test_student_account,
                set_model_active_fields=False,
            )
            self.assertTrue(user_is_active)
            self.assertTrue(user_in_retention)

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test___verify_user_ldap_status_wmu_enrolled(self):
        with self.subTest('With wmuEnrolled field True.'):
            ldap_info = {
                'wmuEnrolled': ['True'],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (True, True),
            )

        with self.subTest('With wmuEnrolled field False, iNetUserStatus False.'):
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': [''],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, False),
            )

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and currently employed.'):
            # Aka wmuEmployeeExpiration equal to or after current date.

            # Set to "2 days from now", to ensure it's after current date.
            employee_expiration = self.current_time + timezone.timedelta(days=2)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (True, True),
            )

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Student Retention period.'):
            # (Aka, wmuStudentExpiration before current date, but within 1 year.)

            # Set to "1 day ago" to check just having expired.
            student_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, True),
            )

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            student_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, True),
            )

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Employee Retention period.'):
            # Aka, wmuEmployeeExpiration before current date, but within 1 year.

            # Set to "1 day ago" to check just having expired.
            employee_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, True),
            )

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            employee_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, True),
            )

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
            self.assertEqual(
                self.wmu_backend._verify_user_ldap_status(self.test_ceas_prog_account, ldap_info),
                (False, False),
            )

    #endregion User Ldap Status Functions

    #region Ldap Get Attr Functions

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test___get_all_user_info_from_bronconet(self):
        # Tests based on CAE Center programmer account.
        if prog_test_account_is_populated():
            # Using the CAE Programmers account. Slightly more thorough testing.
            # Mostly just test a few common values to make sure we retrieved them.

            # Get ldap results.
            ldap_results = self.wmu_backend._get_all_user_info_from_bronconet(self.test_ceas_prog_account)

            # Test values.
            self.assertIsNotNone(ldap_results)
            self.assertEqual(len(ldap_results), 29)
            self.assertEqual(ldap_results['uid'][0], self.test_ceas_prog_account)
            self.assertEqual(ldap_results['sn'][0], 'Programmers')
            self.assertEqual(ldap_results['givenName'][0], 'CAE')
            self.assertEqual(ldap_results['gecos'][0], 'Programmers, CAE')
            self.assertEqual(ldap_results['displayName'][0], 'Programmers, CAE')
            self.assertEqual(ldap_results['mail'][0], 'cae-programmers@wmich.edu')
            self.assertEqual(ldap_results['inetUserStatus'][0], 'active')

        # Tests based on active Student account.
        if student_test_account_is_populated():
            # Using an active student account. For privacy reasons, we can only test so much.

            # Get ldap results.
            ldap_results = self.wmu_backend._get_all_user_info_from_bronconet(self.test_student_account)

            # Test values.
            self.assertIsNotNone(ldap_results)
            self.assertGreater(len(ldap_results), 0)
            self.assertEqual(ldap_results['uid'][0], self.test_student_account)
            self.assertEqual(ldap_results['mail'][0][-10:], '@wmich.edu')

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test___get_all_user_info_from_winno(self):
        # Tests based on CAE Center programmer account.
        if prog_test_account_is_populated():
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')

        # Tests based on active Student account.
        if student_test_account_is_populated():
            # Get ldap Winno.
            winno = self.wmu_backend.get_winno_from_bronconet(self.test_student_account)

            # Get ldap results.
            ldap_results = self.wmu_backend._get_all_user_info_from_winno(winno)

            # Using an active student account. For privacy reasons, we can only test so much.
            self.assertIsNotNone(ldap_results)
            self.assertGreater(len(ldap_results), 0)
            self.assertEqual(ldap_results['uid'][0], self.test_student_account)
            self.assertEqual(ldap_results['mail'][0][-10:], '@wmich.edu')

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__get_winno_from_bronconet(self):
        # Tests based on CAE Center programmer account.
        if prog_test_account_is_populated():
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')

        # Tests based on active Student account.
        if student_test_account_is_populated():
            # Get ldap Winno.
            winno = self.wmu_backend.get_winno_from_bronconet(self.test_student_account)

            # Using an active student account. For privacy reasons, we can only test so much.
            # Check that we got a Winno.
            self.assertIsNotNone(winno)

            # Get value and assert it has characters?
            # Not sure what else we can test without direct comparison.
            self.assertGreater(len(winno), 0)

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    @unittest.skipUnless(prog_or_student_test_account_is_populated(), 'No Ldap User specified. Skipping Ldap tests.')
    def test__get_bronconet_from_winno(self):

        # Tests based on CAE Center programmer account.
        if prog_test_account_is_populated():
            # Using the CAE Programmers account. Skip test.
            unittest.skip('Programmer account does not have an associated Winno. Cannot test.')

        # Tests based on active Student account.
        if student_test_account_is_populated():
            # Get ldap Winno to test with.
            winno = self.wmu_backend.get_winno_from_bronconet(self.test_student_account)

            # Verify we got a Winno back.
            self.assertIsNotNone(winno)

            # Get ldap BroncoNet.
            bronco_net = self.wmu_backend.get_bronconet_from_winno(winno)

            # Using an active student account. For privacy reasons, we can only test so much.
            # Check that we got a BroncoNet.
            self.assertIsNotNone(bronco_net)

            # Verify match.
            self.assertEqual(bronco_net, self.test_student_account)

    #endregion Ldap Get Attr Functions
