"""
Site Settings testing Utility Functions and Classes.
"""

# System Imports.

# User Class Imports.
from django.conf import settings


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
