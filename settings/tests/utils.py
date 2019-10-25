"""
Site Settings testing Utility Functions and Classes.
"""

# System Imports.

# User Class Imports.
from django.conf import settings


def prog_test_account_is_populated():
    """
    Checks if CAE Center programmer account values are populated in local env file.
    Used to determine if some Ldap test sections should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    if settings.BACKEND_LDAP_TEST_PROG_NAME is not None and str(settings.BACKEND_LDAP_TEST_PROG_NAME) != '':
        return True
    else:
        return False


def student_test_account_is_populated():
    """
    Checks if test student values are populated in local env file.
    Used to determine if some Ldap test sections should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    if settings.BACKEND_LDAP_TEST_STUDENT_NAME is not None and str(settings.BACKEND_LDAP_TEST_STUDENT_NAME):
        return True
    else:
        return False


def prog_or_student_test_account_is_populated():
    """
    Checks if either of the two above methods return True.
    Used to determine if some Ldap tests should run or be skipped.
    :return: Bool indicating if values are populated.
    """
    if prog_test_account_is_populated() or student_test_account_is_populated():
        return True
    else:
        return False
