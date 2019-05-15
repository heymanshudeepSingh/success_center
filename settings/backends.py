"""
Custom authentication backends.
"""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from cae_home import models
from settings import simple_ldap_lib
from settings import extra_settings


logger = extra_settings.logging.getLogger(__name__)


class CaeAuthBackend(object):
    """
    Custom authentication through the CAE Center LDAP.
    """
    def __init__(self):
        self.ldap_lib = simple_ldap_lib.SimpleLdap()
        self.ldap_lib.set_host(settings.CAE_LDAP['host'])
        self.ldap_lib.set_master_account(settings.CAE_LDAP['login_dn'], settings.CAE_LDAP['login_password'])
        self.ldap_lib.set_search_base(settings.CAE_LDAP['user_search_base'])

    def authenticate(self, request, username=None, password=None):
        """
        Takes user input and attempts authentication.
        :param username: Value from username field.
        :param password: Value from password field.
        :return: Valid user object on success. | None on failure.
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Attempting CAE user login...')

        # Check what format username was provided as.
        user_id = self.parse_username(username)

        try:
            # Attempt to get user object.
            user = models.User.objects.get(**user_id)

            # Validate user object.
            if user:
                # User object found in local Django database. Use standard Django auth.
                user = self.validate_user(user, password)
            else:
                user = None

            if user is None:
                # Failed user login attempt.
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: CAE user login failed.')
            return user

        except models.User.DoesNotExist:
            # User object not found in local Django database. Attempt ldap query.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: CAE user not found in Django database.')
            user = self.ldap_validate_user(user_id, password)
            return user

    def parse_username(self, username):
        """
        Allows user to attempt login with username or associated email.
        :param username: String user entered into "username" field.
        :return: Dictionary of values to attempt auth with.
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Parsing username...')

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
            logger.info('Auth Backend: Attempting Django validation...')

        # Check password.
        if user.check_password(password):
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Logging in...')
            return user
        else:
            # Bad password.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Bad password. Cancelling login.')
            return None

    def ldap_validate_user(self, user_id, password):
        """
        Attempts to validate user through ldap. If found, will create a new user account using ldap info.
        :return:
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Attempting CAE ldap validation...')

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
                logger.info('Auth Backend: {0}'.format(auth_search_return[1]))
            user = self.create_new_user(uid, password)
        else:
            # Invalid ldap credentials.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: {0}'.format(auth_search_return[1]))
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
            logger.info('Auth Backend: Attempting to create new user model...')

        # Connect to server and pull user's full info.
        self.ldap_lib.bind_server()
        ldap_user = self.ldap_lib.search(
            search_filter='(uid={0})'.format(uid),
            attributes=['uid', 'givenName', 'sn',]
        )

        # Get ldap groups.
        # Check for ldap directors group match.
        ldap_directors = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['director_cn']),
            attributes=['memberUid'],
        )
        if ldap_directors is not None:
            ldap_directors = ldap_directors['memberUid']
        else:
            ldap_directors = []
        # Check for ldap attendants group match.
        ldap_attendants = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['attendant_cn']),
            attributes=['memberUid'],
        )
        if ldap_attendants is not None:
            ldap_attendants = ldap_attendants['memberUid']
        else:
            ldap_attendants = []
        # Check for ldap admins group match.
        ldap_admins = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['admin_cn']),
            attributes=['memberUid'],
        )
        if ldap_admins is not None:
            ldap_admins = ldap_admins['memberUid']
        else:
            ldap_admins = []
        # Check for ldap programmers group match.
        ldap_programmers = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['programmer_cn']),
            attributes=['memberUid'],
        )
        if ldap_programmers is not None:
            ldap_programmers = ldap_programmers['memberUid']
        else:
            ldap_programmers = []
        self.ldap_lib.unbind_server()

        # Create new user.
        model_user, created = models.User.objects.get_or_create(username=uid)

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
                logger.info('Auth Backend: Created user new user model {0}. Now setting groups...'.format(uid))

            # Set user group types.
            if uid in ldap_directors:
                model_user.groups.add(Group.object.get(name='CAE Director'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: Added user to CAE Director group.')
            if uid in ldap_attendants:
                model_user.groups.add(Group.objects.get(name='CAE Attendant'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: Added user to CAE Attendant group.')
            if uid in ldap_admins:
                model_user.groups.add(Group.objects.get(name='CAE Admin'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: Added user to CAE Admin group.')
            if uid in ldap_programmers:
                model_user.groups.add(Group.objects.get(name='CAE Programmer'))
                model_user.is_staff = True
                model_user.is_superuser = True
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: Added user to CAE Programmer group.')

            # Save model.
            model_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: User groups set. User creation complete.'.format(uid))

        else:
            # Error. This shouldn't ever happen.
            model_user = None
            raise ValidationError('Error: Attempted to create user {0} but user with id already exists.'.format(uid))

        return model_user

    def get_user(self, user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except models.User.DoesNotExist:
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: User not found.')
            return None


class WmuAuthBackend(object):
    """
    Custom authentication through the WMU main campus LDAP.
    """
    def __init__(self):
        self.ldap_lib = simple_ldap_lib.SimpleLdap()
        self.ldap_lib.set_host(settings.WMU_LDAP['host'])
        self.ldap_lib.set_master_account(
            settings.WMU_LDAP['login_dn'],
            settings.WMU_LDAP['login_password'],
            get_info='NONE',
        )
        self.ldap_lib.set_search_base(settings.WMU_LDAP['user_search_base'])

    def authenticate(self, request, username=None, password=None):
        """
        Takes user input and attempts authentication.
        :param username: Value from username field.
        :param password: Value from password field.
        :return: Valid user object on success. | None on failure.
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Attempting WMU user login...')

        # Check what format username was provided as.
        user_id = self.parse_username(username)

        try:
            # Attempt to get user object.
            user = models.User.objects.get(**user_id)

            # Validate user object.
            if user:
                # User object found in local Django database. Use standard Django auth.
                user = self.validate_user(user, password)
            else:
                user = None

            if user is None:
                # Failed user login attempt.
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('Auth Backend: WMU user login failed.')
            return user

        except models.User.DoesNotExist:
            # User object not found in local Django database. Attempt ldap query.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: WMU user not found in Django database.')
            user = self.ldap_validate_user(user_id, password)
            return user

    def parse_username(self, username):
        """
        Allows user to attempt login with username or associated email.
        :param username: String user entered into "username" field.
        :return: Dictionary of values to attempt auth with.
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Parsing username...')

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
            logger.info('Auth Backend: Attempting Django validation...')

        # Check password.
        if user.check_password(password):
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Logging in...')
            return user
        else:
            # Bad password.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Bad password. Cancelling login.')
            return None

    def ldap_validate_user(self, user_id, password):
        """
        Attempts to validate user through ldap. If found, will create a new user account using ldap info.
        :return:
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('Auth Backend: Attempting WMU ldap validation...')

        # Check if input was email or username. Parse to uid accordingly.
        # Note that if email, it should always be a wmu email. Thus the parse should get a bronconet id.
        if 'email' in user_id.keys():
            uid = user_id['email'].split('@')[0]
        else:
            uid = user_id['username']

        auth_search_return = self.ldap_lib.authenticate_with_uid(
            uid,
            password,
            search_filter='(uid={0})'.format(uid),
            get_info='NONE',
            is_cae_ldap=False,
        )

        if auth_search_return[0]:
            # User validated successfully through ldap. Create new django user.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: {0}'.format(auth_search_return[1]))
            user = self.create_new_user(uid, password)
        else:
            # Invalid ldap credentials.
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: {0}'.format(auth_search_return[1]))
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
            logger.info('Auth Backend: Attempting to create new user model...')

        # Connect to server and pull user's full info.
        self.ldap_lib.bind_server(get_info='NONE')
        ldap_user = self.ldap_lib.search(
            search_filter='(uid={0})'.format(uid),
            attributes=['wmuBannerID', 'wmuFirstName', 'wmuMiddleName', 'wmuLastName', 'mail', 'wmuProgramCode']
        )
        self.ldap_lib.unbind_server()

        # Create new user.
        model_user, created = models.User.objects.get_or_create(username=uid)

        # Double check that user was created. If not, then duplicate user ids exist somehow. Error.
        if created:
            # Set password.
            model_user.set_password(password)
            model_user.save()

            # Set general (login) user values.
            model_user.email = '{0}@wmich.edu'.format(uid)
            model_user.first_name = ldap_user['wmuFirstName'][0].strip()
            model_user.last_name = ldap_user['wmuLastName'][0].strip()

            # Save model in case of error.
            model_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Created user new user model {0}. Now setting groups...'.format(uid))

            # Set related WMU User model info.
            try:
                # Attempt to get related model. Just to see if it exists or not.
                wmu_user = models.WmuUser.objects.get(bronco_net=uid)
            except models.WmuUser.DoesNotExist:
                # Create new related model.
                winno = ldap_user['wmuBannerID'][0]
                try:
                    first_name = ldap_user['wmuFirstName'][0].strip()
                except KeyError:
                    first_name = ''
                try:
                    middle_name = ldap_user['wmuMiddleName'][0].strip()
                except KeyError:
                    middle_name = ''
                try:
                    last_name = ldap_user['wmuLastName'][0].strip()
                except KeyError:
                    last_name = ''
                try:
                    official_email = ldap_user['mail'][0].strip()
                except KeyError:
                    official_email = '{0}@wmich.edu'.format(uid)

                major = models.Major.objects.get(slug='unk')

                wmu_user = models.WmuUser.objects.create(
                    bronco_net=uid,
                    winno=winno,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    official_email=official_email,
                    major=major,
                )

            # Save models.
            model_user.save()
            wmu_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: Related WMU User model set. User creation complete.'.format(uid))

        else:
            # Error. This shouldn't ever happen.
            model_user = None
            raise ValidationError('Error: Attempted to create user {0} but user with id already exists.'.format(uid))

        return model_user

    def get_user(self, user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except models.User.DoesNotExist:
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('Auth Backend: User not found.')
            return None
