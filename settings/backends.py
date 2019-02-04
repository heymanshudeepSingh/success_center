"""
Custom authentication backends.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from cae_home.models import User


class CaeAuthBackend(object):
    """
    Custom CAE Center authentication.
    """
    def authenticate(self, username=None, password=None):
        """
        Takes user input and attempts authentication.
        :param username: Value from username field.
        :param password: Value from password field.
        :return: Valid user object on success. | None on failure.
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Attempting user login...')

        try:
            # Check if user attempted login with email.
            if '@' in username:
                try:
                    # Attempt with "username" as email.
                    validate_email(username)
                    kwargs = {'email': username}
                except ValidationError:
                    # Not sure what the user attempted with. Assume normal username.
                    kwargs = {'username': username}
            else:
                # Use as normal username.
                kwargs = {'username': username}

            # Attempt to get user object.
            user = User.objects.get(**kwargs)

            # Valdate user object.
            if user:
                if settings.AUTH_BACKEND_DEBUG:
                    print('Auth Backend: Found user object.')

                # Check password.
                if user.check_password(password):
                    if settings.AUTH_BACKEND_DEBUG:
                        print('Auth Backend: Logging in...')
                    return user
                else:
                    # Bad password.
                    if settings.AUTH_BACKEND_DEBUG:
                        print('Auth Backend: Bad password. Cancelling login.')

            # Failed user login attempt.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User login failed.')
            return None

        except User.DoesNotExist:
            # Error. Failed user login attempt.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User not found.')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User not found.')
            return None
