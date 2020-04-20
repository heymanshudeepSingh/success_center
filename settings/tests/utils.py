"""
Site Settings testing Utility Functions and Classes.
"""

# System Imports.
import os

# User Class Imports.
from django.conf import settings
from settings.reusable_settings import BASE_DIR


def run_ldap_tests():
    """
    Returns a bool indicating if ldap unit tests should run or not.

    This bool is determined by:
    * If the "simple_ldap_lib" library is actually pulled and available.

    :return: Bool indicating if ldap unit tests should run or not.
    """
    # Get library directory. Make sure that there are items inside it.
    ldap_lib_dir = os.path.join(BASE_DIR, 'settings/simple_ldap_lib')
    if os.path.exists(ldap_lib_dir):
        if len(os.listdir(ldap_lib_dir)) > 0:
            return True

    # If we made it this far, then we failed checks. Do not run unit tests.
    return False


def prog_test_account_is_populated():
    """
    Checks if CAE Center programmer account values are populated in local env file.
    Used to determine if some Ldap test sections should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    # Check if account is populated.
    if settings.BACKEND_LDAP_TEST_PROG_ID is not None and str(settings.BACKEND_LDAP_TEST_PROG_ID) != '':
        return True
    else:
        return False


def student_test_account_is_populated():
    """
    Checks if test student values are populated in local env file.
    Used to determine if some Ldap test sections should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    # Check if account is populated.
    if settings.BACKEND_LDAP_TEST_STUDENT_ID is not None and str(settings.BACKEND_LDAP_TEST_STUDENT_ID) != '':
        return True
    else:
        return False


def prog_or_student_test_account_is_populated():
    """
    Checks if either of the two above methods return True.
    Used to determine if some Ldap tests should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    # Check if accounts are populated.
    if prog_test_account_is_populated() or student_test_account_is_populated():
        return True
    else:
        return False
