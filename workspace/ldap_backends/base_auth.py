"""
Base/Universal logic for custom authentication backends.

Note that, to work, this needs the simple_ldap_lib git submodule imported, and the correct env settings set.
"""

# System Imports.
import re
from abc import ABC, abstractmethod
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from importlib import import_module

# User Class Imports.
from cae_home import models
from workspace import logging as init_logging
from workspace.ldap_backends import simple_ldap_lib


# Import logger.
logger = init_logging.get_logger(__name__)


class AbstractLDAPBackend(ABC):
    """
    Custom, abstract LDAP authentication class.

    The module "ABC" defines this as an "Abstract Base Class". To use this, another class must inherit it.
    The decorator "@abstractmethod" defines a method as abstract. The inheriting class must override these methods
    or else an error will occur on initialization.
    """
    def __init__(self):
        """
        Init method for class.
        If necessary, can adjust/override any values in the "setup_abstract_class" method for inheriting children.
        """
        self.regex_username_match = r'([a-zA-Z0-9]+)(($)|(@{0}$))'    # Regex to compare username to.
        self.get_info = 'SCHEMA'    # "get_info" value used in LDAP connection binds.

        self.ldap_lib = simple_ldap_lib.SimpleLdap()

        self.setup_abstract_class()

    #region Abstract Methods

    @abstractmethod
    def setup_abstract_class(self):
        """
        Abstract method for logic to be run on inheriting class's __init__ function.

        In this case, it should contain values to connect to LDAP for the SimpleLdapLibrary.
        If the "get_info" attribute should be anything other than "SCHEMA", also change that here.
        """
        pass

    @abstractmethod
    def create_or_update_user_model(self, uid, password):
        """
        Abstract method for creating a new user, using pulled ldap information.

        Only called on known, valid and already authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return: Newly created Django User object.
        """
        pass

    #endregion Abstract Methods


    #region User Auth

    def authenticate(self, request, username=None, password=None):
        """
        Takes user input and attempts authentication.
        :param username: Value from username field.
        :param password: Value from password field.
        :return: Valid user object on success. | None on failure.
        """
        try:
            logger.auth_info('{0}: Attempting user login...'.format(username))

            # Check what format username was provided as.
            user_id = self._parse_username(username)

            if user_id is None:
                logger.auth_warning('{0}: User login failed.'.format(username))
                return None

            # Check if we should use Django User Model passwords.
            if settings.AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS:
                # Logic to use Django User Model passwords.
                # Ldap is only used on first user login to create initial user model. Then Django User Model is used for
                # all future logins.
                try:
                    # Attempt to get user object.
                    user = models.User.objects.get(**user_id)

                    # Validate user object.
                    if user:
                        # User object found in local Django database. Use standard Django auth.
                        user = self._validate_django_user(user, password)

                        # Check that user is active.
                        if user and not self.user_can_authenticate(user):
                            user = None
                    else:
                        user = None

                    if user is None:
                        # Failed user login attempt.
                        logger.auth_warning('{0}: User login failed.'.format(username))
                    else:
                        # Run login hook logic for user.
                        self.run_user_login_hooks(request, user)
                    return user

                except models.User.DoesNotExist:
                    # User object not found in local Django database. Attempt ldap query.
                    logger.auth_info('{0}: User not found in Django database.'.format(username))
                    user = self._validate_ldap_user(user_id, password)

                    # Run login hook logic for user.
                    self.run_user_login_hooks(request, user)

                    return user
            else:
                # Logic to exclusively use Ldap User passwords.
                # Ldap is used every time. Password info is never saved to Django User Models.
                user = self._validate_ldap_user(user_id, password)

                # Run login hook logic for user.
                self.run_user_login_hooks(request, user)

                return user
        except Exception as err:
            logger.auth_error('Error during auth: {0}'.format(err), exc_info=True)
            raise (err)

    def _parse_username(self, username):
        """
        Allows user to attempt login with username or associated email.
        :param username: String user entered into "username" field.
        :return: Dictionary of values to attempt auth with.
        """
        logger.auth_info('{0}: Parsing username...'.format(username))

        # Check for any nonstandard characters. If so, skip login.
        # (Should be standard numbers/letters, optionally with "@wmich.edu" appended.)
        if not re.match(self.regex_username_match, username):
            logger.auth_info('{0}: Attempted login with invalid characters.'.format(username))
            return None
        else:
            # Remove whitespace and set all characters to lowercase.
            username = username.strip().lower()

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

    def _validate_django_user(self, user, password):
        """
        Validates given user object. Uses standard Django auth logic.
        :param user:
        :return: Valid user | None on failure
        """
        logger.auth_info('{0}: Attempting Django validation...'.format(user))

        # Check password.
        if user.check_password(password):
            logger.auth_info('{0}: Logging in...'.format(user))
            return user
        else:
            # Bad password.
            logger.auth_info('{0}: Bad password. Cancelling login.'.format(user))
            return None

    def _validate_ldap_user(self, user_id, password):
        """
        Attempts to validate user through ldap. If found, will create a new user account using ldap info.
        """
        logger.auth_info('{0}: Attempting Ldap validation...'.format(user_id))

        # Check if input was email or username. Parse to uid accordingly.
        # Note that if email, it should always be a wmu email. Thus the parse should get a bronconet id.
        if 'email' in user_id.keys():
            uid = user_id['email'].split('@')[0]
        else:
            uid = user_id['username']

        auth_search_return = self.ldap_lib.authenticate_with_unknown_uid(
            uid,
            password,
            search_filter='(uid={0})'.format(uid),
            get_info='NONE',
        )

        if auth_search_return[0]:
            # User validated successfully through ldap. Create new django user.
            logger.auth_info('{0}: {1}'.format(user_id, auth_search_return[1]))
            user = self.create_or_update_user_model(uid, password)
        else:
            # Invalid ldap credentials.
            logger.auth_info('{0}: {1}'.format(user_id, auth_search_return[1]))
            user = None

        return user

    def user_can_authenticate(self, user):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Reject users with is_active=False. Custom user models that don't have that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Attempts to get user with passed pk.
        """
        try:
            user = get_user_model()._default_manager.get(pk=user_id)
        except get_user_model().DoesNotExist:
            user = None
        if user and not self.user_can_authenticate(user):
            user = None

        if user is None and settings.AUTH_BACKEND_DEBUG:
            logger.auth_info('{0}: User not found.'.format(user_id))
        return user

    def run_user_login_hooks(self, request, user):
        """
        Runs user login hooks for included apps.
        Allows apps to run additional, custom logic for user.
        :param request: Associated web request object.
        :param user: User model of newly authenticated user.
        """
        # Check if login was successful.
        if user is None:
            # User not provided. Login not successful.
            return

        # If we made it this far, login was successful. Run login hooks.
        logger.auth_info('{0}: Login successful. Running user login hooks.'.format(user))

        # Call all login user logic hooks for included apps.
        for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
            for app, app_name in project_settings['related_apps'].items():
                try:
                    # Attempt to call app hook.
                    app_hook = import_module('{0}.management.user_hooks'.format(app_name))
                    app_hook.LoginHooks(request, user)
                except ModuleNotFoundError:
                    # User login hooks do not exist for app. Skip.
                    pass

    #endregion User Auth


    #region User Permissions

    def _get_user_permissions(self, user_obj):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Gets individual permissions for user.
        """
        return user_obj.user_permissions.all()

    def _get_group_permissions(self, user_obj):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Gets group permissions for user.
        """
        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Gets permission value specified in "from_name"?
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, {'%s.%s' % (ct, name) for ct, name in perms})
        return getattr(user_obj, perm_cache_name)

    def get_user_permissions(self, user_obj, obj=None):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Return a set of permission strings the user `user_obj` has from their `user_permissions`.
        """
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Return a set of permission strings the user `user_obj` has from the groups they belong.
        """
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Gets all permissions, both user and group based.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = {
                *self.get_user_permissions(user_obj),
                *self.get_group_permissions(user_obj),
            }
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Checks if user has a specific permission.
        """
        return user_obj.is_active and perm in self.get_all_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        """
        Default django method, imported from "contrib.auth.backends.ModelBackend".

        Return True if user_obj has any permissions in the given app_label.
        """
        return user_obj.is_active and any(
            perm[:perm.index('.')] == app_label
            for perm in self.get_all_permissions(user_obj)
        )

    #endregion User Permissions


    #region User LDAP Attribute Methods

    def get_ldap_user_info(self, uid, attributes=None):
        """
        Gets attribute(s) info for given user. Can get multiple attributes at once (or all of them).
        WARNING: Returns None if any if any given attribute(s) does not exist.
        :param uid: User id to search for.
        :param attributes: Attributes to search for. If not provided, then gets all attributes for user.
        :return: None if bad user_id or attribute | Dict of user's attributes.
        """
        # Validate vars.
        if attributes is None:
            attributes = 'ALL_ATTRIBUTES'
        elif not isinstance(attributes, list) and attributes != 'ALL_ATTRIBUTES':
            raise ValidationError('Attributes var must be a of type [list | None].')

        # Get value from server.
        self.ldap_lib.bind_server(get_info=self.get_info)
        user_attributes = self.ldap_lib.search(search_filter='(uid={0})'.format(uid), attributes=attributes)
        self.ldap_lib.unbind_server()

        # Check server response.
        if user_attributes is None:
            warn_message = '{0}: Search returned no results. Double check that the uid was correct.Otherwise, '\
                'attribute did not exist for entry.'.format(uid)
            logger.auth_warning(warn_message)
        return user_attributes

    def get_ldap_user_attribute(self, uid, attribute):
        """
        Gets a single attribute's info for given user.
        Safer than above method to use if LDAP entries are not uniform.
        :param uid: User id to search for.
        :param attribute: String of attribute to search for.
        :return: None if bad user_id or attribute | String of user attribute.
        """
        # Validate vars.
        if attribute is None or not isinstance(attribute, str):
            raise ValidationError('Attribute must be of type string.')
        attribute = attribute.strip()
        if attribute == '':
            raise ValidationError('Attribute cannot be an empty string.')

        # Get value from server.
        self.ldap_lib.bind_server(get_info=self.get_info)
        user_attribute = self.ldap_lib.search(search_filter='(uid={0})'.format(uid), attributes=[attribute])
        self.ldap_lib.unbind_server()

        # Check server response.
        if user_attribute is None:
            warn_message = '{0}: Search returned no results. Double check that the uid was correct. Otherwise, '\
                ' attribute did not exist for entry.'.format(uid)
            logger.auth_warning(warn_message)
        else:
            # Format server response.
            user_attribute = user_attribute[attribute]

            # Check if is list.
            if isinstance(user_attribute, list):
                if len(user_attribute) == 1:
                    # Attribute is one value. Just get value.
                    user_attribute = user_attribute[0].strip()
                elif len(user_attribute) > 1:
                    # Attribute has multiple entries. Leave as is.
                    pass
                else:
                    # Attribute returned as empty.
                    user_attribute = ''

            # Check if string.
            elif isinstance(user_attribute, str):
                user_attribute = user_attribute.strip()

        return user_attribute

    #endregion User LDAP Attribute Methods
