"""
Site Settings testing Utility Functions and Classes.
"""

# System Imports.
import os

# User Class Imports.
from django.conf import settings
from workspace.settings.reusable_settings import BASE_DIR


def run_ldap_tests():
    """
    Returns a bool indicating if ldap unit tests should run or not.

    This bool is determined by:
        * If the "simple_ldap_lib" library is actually pulled and available.
        * If there are proper LDAP settings in the env file.

    :return: Bool indicating if ldap unit tests should run or not.
    """
    directory_exists = False
    credentials_present = True

    # Get library directory. Make sure that there are items inside it.
    ldap_lib_dir = os.path.join(BASE_DIR, 'workspace/ldap_backends/simple_ldap_lib')
    if os.path.exists(ldap_lib_dir):
        if len(os.listdir(ldap_lib_dir)) > 0:
            # Directory exists and is not empty.
            directory_exists = True

    # Check LDAP credentials. Effectively, check for at least one non-empty string value.
    cae_ldap = settings.CAE_LDAP
    wmu_ldap = settings.WMU_LDAP
    adv_ldap = settings.ADV_LDAP
    for key, value in cae_ldap.items():
        if str(value) != '':
            credentials_present = True
    for key, value in wmu_ldap.items():
        if str(value) != '':
            credentials_present = True
    for key, value in adv_ldap.items():
        if str(value) != '':
            credentials_present = True

    # Check if both test values passed.
    if directory_exists and credentials_present:
        # Directory is present and env has some sort of credential. Return True to okay running LDAP tests.
        return True
    else:
        # One or both checks failed. Do not run any LDAP unit tests.
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
