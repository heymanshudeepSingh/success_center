"""
Tests for CAE Home app Forms.
"""

# System Imports.
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase
from settings.ldap_backends import wmu_auth


class WmuAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper WMU Auth Backend implementation.
    """
    @classmethod
    def setUpTestData(cls):
        cls.wmu_backend = wmu_auth.WmuAuthBackend()
        cls.current_time = timezone.now()
        cls.time_format = '%Y%m%d%H%M%S%z'

    def test__verify_user_ldap_status_wmu_enrolled(self):
        with self.subTest('With wmuEnrolled field True.'):
            ldap_info = {
                'wmuEnrolled': ['True'],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (True, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus False.'):
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': [''],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, False))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and currently employed.'):
            # Aka wmuEmployeeExpiration equal to or after current date.

            # Set to "2 days from now", to ensure it's after current date.
            employee_expiration = self.current_time + timezone.timedelta(days=2)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (True, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Student Retention period.'):
            # (Aka, wmuStudentExpiration before current date, but within 1 year.)

            # Set to "1 day ago" to check just having expired.
            student_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, True))

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            student_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuStudentExpiration': [student_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, True))

        with self.subTest('With wmuEnrolled field False, iNetUserStatus True, and within Employee Retention period.'):
            # Aka, wmuEmployeeExpiration before current date, but within 1 year.

            # Set to "1 day ago" to check just having expired.
            employee_expiration = self.current_time - timezone.timedelta(days=1)
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, True))

            # Set to "11 months, 20 days ago" to check almost out of retention period.
            employee_expiration = self.current_time - timezone.timedelta(days=((11 * (365/12)) + 20))
            ldap_info = {
                'wmuEnrolled': ['False'],
                'inetUserStatus': ['active'],
                'wmuEmployeeExpiration': [employee_expiration.strftime(self.time_format)],
            }
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, True))

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
            self.assertEqual(self.wmu_backend._verify_user_ldap_status_wmu_enrolled(ldap_info), (False, False))


class AdvisingAuthBackendTests(IntegrationTestCase):
    """
    Tests to ensure proper Advising Auth Backend implementation.
    """
    @classmethod
    def setUpTestData(cls):
        cls.adv_backend = wmu_auth.AdvisingAuthBackend()

    def test__create_new_user_from_ldap(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._create_new_user_from_ldap()

    # region User Auth

    def test_authenticate(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.authenticate()

    def test__parse_username(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._parse_username()

    def test__validate_django_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._validate_django_user()

    def test__validate_ldap_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._validate_ldap_user()

    def test_user_can_authenticate(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.user_can_authenticate()

    def test_get_user(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.get_user()

    #endregion User Auth

    # region User Permissions

    def test__get_user_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_user_permissions()

    def test__get_group_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_group_permissions()

    def test__get_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_permissions()

    def test_get_user_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_user_permissions()

    def test_get_group_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend._get_group_permissions()

    def test_get_all_permissions(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.get_all_permissions()

    def test_has_perm(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.has_perm()

    def test_has_module_perms(self):
        with self.assertRaises(NotImplementedError):
            self.adv_backend.has_module_perms()

    # endregion User Permissions

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
