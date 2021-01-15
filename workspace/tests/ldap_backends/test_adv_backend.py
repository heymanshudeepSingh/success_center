"""
Tests for Advising Authentication Backend.
"""

# System Imports.
import unittest

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from workspace.tests.utils import run_ldap_tests
from workspace.tests.utils import prog_or_student_test_account_is_populated
from workspace.tests.utils import prog_test_account_is_populated, student_test_account_is_populated
if run_ldap_tests():
    from workspace.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend



class AdvisingAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper Advising Auth Backend implementation.
    """
    @classmethod
    def setUpTestData(cls):
        if run_ldap_tests():
            cls.adv_backend = AdvisingAuthBackend()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__create_new_user_from_ldap(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.create_or_update_user_model()

    # region User Auth

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_authenticate(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.authenticate()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__parse_username(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._parse_username()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__validate_django_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._validate_django_user()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__validate_ldap_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._validate_ldap_user()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_user_can_authenticate(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.user_can_authenticate()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_get_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.get_user()

    #endregion User Auth

    # region User Permissions

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_user_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_user_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_group_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_group_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_get_user_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_user_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_get_group_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_group_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_get_all_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.get_all_permissions()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_has_perm(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.has_perm()

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test_has_module_perms(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.has_module_perms()

    # endregion User Permissions

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_major_department(self):
        na_department = models.Department.objects.create(name='NA/Unknown', slug='na-unknown')

        with self.subTest('Department model does not yet exist.'):
            # First, verify that department does not exist.
            with self.assertRaises(models.Department.DoesNotExist):
                models.Department.objects.get(name='Test Department')

            # Create mock ldap object.
            ldap_major = {
                'wmuDepartmentName': ['Test Department'],
            }
            returned_department = self.adv_backend._get_major_department(ldap_major)
            department_model = models.Department.objects.get(name='Test Department')
            self.assertEqual(returned_department, department_model)

        with self.subTest('Department model does exist.'):
            # Verify that department now exists.
            department_model = models.Department.objects.get(name='Test Department')

            # Create mock ldap object.
            ldap_major = {
                'wmuDepartmentName': ['Test Department'],
            }
            self.assertEqual(self.adv_backend._get_major_department(ldap_major), department_model)

        with self.subTest('"wmuDepartmentName" field not present in ldap_major.'):
            ldap_major = {}
            self.assertEqual(self.adv_backend._get_major_department(ldap_major), na_department)

        with self.subTest('"wmuDepartmentName" field is empty for ldap_major.'):
            ldap_major = {
                'wmuDepartmentName': [],
            }
            self.assertEqual(self.adv_backend._get_major_department(ldap_major), na_department)

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_major_display_name(self):
        with self.subTest('"displayName" field is present.'):
            # Create mock ldap object.
            ldap_major = {
                'displayName': ['Test Name'],
            }
            self.assertEqual(self.adv_backend._get_major_display_name(ldap_major), 'Test Name')

        with self.subTest('"displayName" field not present, but "title" field is.'):
            # Create mock ldap object.
            ldap_major = {
                'title': ['Test Title'],
            }
            self.assertEqual(self.adv_backend._get_major_display_name(ldap_major), 'Test Title')

        with self.subTest('"displayName" and "title" fields not present, but "wmuStudentMajor" field is.'):
            # Create mock ldap object.
            ldap_major = {
                'wmuStudentMajor': ['Test Code'],
            }
            self.assertEqual(self.adv_backend._get_major_display_name(ldap_major), 'Test Code')

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_major_program_code(self):
        with self.subTest('Single program_code in ldap object.'):
            # Create mock ldap object.
            ldap_major = {
                'wmuProgramCode': ['A-BSE-IENJ']
            }
            self.assertEqual(self.adv_backend._get_major_program_code(ldap_major), 'A-BSE-IENJ')

        with self.subTest('Multiple program_codes in ldap object. Version 1.'):
            # Create mock ldap object.
            ldap_major = {
                'wmuProgramCode': ['ABSEIND-IENJ', 'A-BSE-IENJ']
            }
            self.assertEqual(self.adv_backend._get_major_program_code(ldap_major), 'A-BSE-IENJ')

        with self.subTest('Multiple program_codes in ldap object. Version 2'):
            # Create mock ldap object.
            ldap_major = {
                'wmuProgramCode': ['ABSEIND-IENJ', 'IENJ']
            }
            self.assertEqual(self.adv_backend._get_major_program_code(ldap_major), 'ABSEIND-IENJ')

    @unittest.skipUnless(run_ldap_tests(), 'Missing criteria for LDAP. Skipping Ldap tests.')
    def test__get_degree_level_from_program_code(self):
        # Test with preferred code format.
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('A-BSE-IENJ'), 2)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('A-MSE-IENM'), 3)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('A-PHD-IEND'), 4)

        # Test with 2 length format.
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('ABSEIND-IENJ'), 2)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('AMSEIND-IENM'), 3)

        # Test with 1 length format.
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('IENP'), 1)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('IENJ'), 2)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('IENM'), 3)
        self.assertEqual(self.adv_backend._get_degree_level_from_program_code('IEND'), 4)
