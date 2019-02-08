"""
Custom authentication backends.
"""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from cae_home.models import User
from settings import simple_ldap_lib


class CaeAuthBackend(object):
    """
    Custom CAE Center authentication.
    """
    def __init__(self):
        self.ldap_lib = simple_ldap_lib.SimpleLdap()
        self.ldap_lib.set_host(settings.LDAP_HOST)
        self.ldap_lib.set_master_account(settings.LDAP_DN, settings.LDAP_PASS)
        self.ldap_lib.set_search_base(settings.LDAP_SEARCH_BASE)

    def authenticate(self, request, username=None, password=None):
        """
        Takes user input and attempts authentication.
        :param username: Value from username field.
        :param password: Value from password field.
        :return: Valid user object on success. | None on failure.
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Attempting user login...')

        # Check what format username was provided as.
        user_id = self.parse_username(username)

        try:
            # Attempt to get user object.
            user = User.objects.get(**user_id)

            # Validate user object.
            if user:
                # User object found in local Django database. Use standard Django auth.
                user = self.validate_user(user, password)
            else:
                user = None

            if user is None:
                # Failed user login attempt.
                if settings.AUTH_BACKEND_DEBUG:
                    print('Auth Backend: User login failed.')
            return user

        except User.DoesNotExist:
            # User object not found in local Django database. Attempt ldap query.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User not found in Django database.')
            user = self.ldap_validate_user(user_id, password)
            return user

    def parse_username(self, username):
        """
        Allows user to attempt login with username or associated email.
        :param username: String user entered into "username" field.
        :return: Dictionary of values to attempt auth with.
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Parsing username...')

        username = username.strip()

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
        return kwargs

    def validate_user(self, user, password):
        """
        Validates given user object. Uses standard Django auth logic.
        :param user:
        :return: Valid user | None on failure
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Attempting Django validation...')

        # Check password.
        if user.check_password(password):
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: Logging in...')
            return user
        else:
            # Bad password.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: Bad password. Cancelling login.')
            return None

    def ldap_validate_user(self, user_id, password):
        """
        Attempts to validate user through ldap. If found, will create a new user account using ldap info.
        :return:
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Attempting ldap validation...')

        # Check if input was email or username. Parse to uid accordingly.
        # Note that if email, it should always be a wmu email. Thus the parse should get a bronconet id.
        if 'email' in user_id.keys():
            uid = user_id['email'].split('@')[0]
        else:
            uid = user_id['username']

        auth_search_return = self.ldap_lib.authenticate_with_uid(uid, password, search_filter='(uid={0})'.format(uid))

        if auth_search_return[0]:
            # User validated successfully through ldap. Create new django user.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: {0}'.format(auth_search_return[1]))
            user = self.create_new_user(uid, password)
        else:
            # Invalid ldap credentials.
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: {0}'.format(auth_search_return[1]))
            user = None

        return user

    def create_new_user(self, uid, password):
        """
        Attempts to create new user, using pulled ldap information.
        Should only be called on known, valid and authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return:
        """
        if settings.AUTH_BACKEND_DEBUG:
            print('Auth Backend: Attempting to create new user model...')

        # Connect to server and pull user's full info.
        self.ldap_lib.bind_server()
        ldap_user = self.ldap_lib.search(
            search_filter='(uid={0})'.format(uid),
            attributes=['uid', 'givenName', 'sn',]
        )

        # Get ldap user groups.
        ldap_attendants = self.ldap_lib.search(
            search_base=settings.LDAP_GROUP_DN,
            search_filter='({0})'.format(settings.LDAP_ATTENDANT_CN),
            attributes=['memberUid'],
        )['memberUid']
        ldap_admins = self.ldap_lib.search(
            search_base=settings.LDAP_GROUP_DN,
            search_filter='({0})'.format(settings.LDAP_ADMIN_CN),
            attributes=['memberUid'],
        )['memberUid']
        ldap_programmers = self.ldap_lib.search(
            search_base=settings.LDAP_GROUP_DN,
            search_filter='({0})'.format(settings.LDAP_PROGRAMMER_CN),
            attributes=['memberUid'],
        )['memberUid']

        # Create new user.
        model_user, created = User.objects.get_or_create(username=uid)

        # Double check that user was created. If not, then duplicate user ids exist somehow. Error.
        if created:
            # Set password.
            model_user.set_password(password)
            model_user.save()

            # Set general user values.
            model_user.email = '{0}@wmich.edu'.format(uid)
            model_user.first_name = ldap_user['givenName'][0].strip()
            model_user.last_name = ldap_user['sn'][0].strip()

            # Save model in case of error.
            model_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: Created user new user model {0}. Now setting groups...'.format(uid))

            # Set user group types.
            if uid in ldap_attendants:
                model_user.groups.add(Group.objects.get(name='CAE Attendant'))
                if settings.AUTH_BACKEND_DEBUG:
                    print('Auth Backend: Added user to CAE Attendant group.')
            if uid in ldap_admins:
                model_user.groups.add(Group.objects.get(name='CAE Admin'))
                if settings.AUTH_BACKEND_DEBUG:
                    print('Auth Backend: Added user to CAE Admin group.')
            if uid in ldap_programmers:
                model_user.groups.add(Group.objects.get(name='CAE Programmer'))
                model_user.is_staff = True
                model_user.is_superuser = True
                if settings.AUTH_BACKEND_DEBUG:
                    print('Auth Backend: Added user to CAE Programmer group.')

            # Save model.
            model_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User groups set. User creation complete.'.format(uid))

        else:
            # Error. This shouldn't ever happen.
            model_user = None
            raise ValidationError('Error: Attempted to create user {0} but user with id already exists.'.format(uid))

        return model_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            if settings.AUTH_BACKEND_DEBUG:
                print('Auth Backend: User not found.')
            return None
