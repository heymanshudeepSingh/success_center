"""
Specific logic for custom authentication backends.

Note that, to work, these need the simple_ldap_lib git submodule imported, and the correct env settings set.
"""

# System Imports.
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

# User Class Imports.
from cae_home import models
from workspace import logging as init_logging
from workspace.ldap_backends.base_auth import AbstractLDAPBackend
from workspace.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend


# Import logger.
logger = init_logging.get_logger(__name__)


class CaeAuthBackend(AbstractLDAPBackend):
    """
    Custom authentication through the CAE Center LDAP.
    """
    def setup_abstract_class(self):
        """
        Note: "check_credentials" value is set to False, because otherwise it will ping the LDAP server to verify
            the "master" credentials every time this Auth Backend is called.

            When set to active in settings, this backend is used every time a page needs to check permissions. So
            enabling "check_credentials" would potentially add a lot of extra time to each page load.
        """
        # Set allowed email value in username.
        self.regex_username_match = self.regex_username_match.format('wmich.edu')

        # Set ldap connection settings.
        self.ldap_lib.set_host(settings.CAE_LDAP['host'])
        self.ldap_lib.set_master_account(
            settings.CAE_LDAP['login_dn'],
            settings.CAE_LDAP['login_password'],
            check_credentials=False,
            get_info=self.get_info,
        )
        self.ldap_lib.set_search_base(settings.CAE_LDAP['user_search_base'])
        self.ldap_lib.set_uid_attribute(settings.CAE_LDAP['default_uid'])

    def create_or_update_user_model(self, uid, password=None):
        """
        Attempts to get and update User model with given username.
        In the event that no such model exists, instead create it from scratch using ldap info.

        Should only be called on known, valid and authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return: Instance of User model.
        """
        try:
            # Call model to verify existence.
            user = models.User.objects.get(username=uid)

            # If we got this far, then model exists. Update.
            return self._update_user_model(uid, password)
        except models.User.DoesNotExist:
            # User model doesn't exist. Create new model.
            return self._create_user_model(uid, password)

    def _create_user_model(self, uid, password):
        """
        Creates new User model, using pulled ldap information.
        Logic here should be "first time model creation" logic.

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "_create_or_update_user_model" function.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return: Instance of User model.
        """
        # Connect to LDAP server and pull user's full info.
        ldap_user_info = self.get_ldap_user_info(uid, attributes=['uid', 'givenName', 'sn', ])

        # Check if we got LDAP response. If not, user does not exist in CAE LDAP.
        if ldap_user_info is not None:

            logger.auth_info('{0}: Attempting to create new user model...'.format(uid))

            # Create new user.
            login_user, created = models.User.objects.get_or_create(username=uid)

            # Double check that user was created. If not, then duplicate user Id's exists.
            if not created:
                # Duplicate Id's exist.
                # Most likely, there's a logic error in code and "_update_user_model" should have been called.
                login_user = None
                error_message = '{0}: Attempted to create user but user with id already exists.'.format(uid)
                logger.auth_error(error_message)
                raise ValidationError(error_message)

            # Set password based on AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS setting.
            if settings.AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS and password is not None:
                login_user.set_password(password)
                login_user.save()

            # Set general user values.
            login_user.email = '{0}@wmich.edu'.format(uid)
            login_user.first_name = ldap_user_info['givenName'][0].strip()
            login_user.last_name = ldap_user_info['sn'][0].strip()

            # Save model.
            login_user.save()

            logger.auth_info('{0}: Created user new user model. Now setting groups...'.format(uid))

            # Model created. Now run update logic to ensure all fields are properly set.
            login_user = self._update_user_model(uid, password)

            logger.auth_info('{0}: Imported Main Campus user info. User creation complete.'.format(uid))

            return login_user

        else:
            # User does not exist in CAE LDAP. Try WMU LDAP instead.
            from workspace.ldap_backends.wmu_auth import wmu_backend
            wmu_ldap = wmu_backend.WmuAuthBackend()
            return wmu_ldap.create_or_update_user_model(uid, password)

    def _update_user_model(self, uid, password):
        """
        Updates User model, using pulled Ldap information.
        Logic here should be fine to potentially run on every user login instance (including first).

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "create_or_update_user_model" function.
        :param uid: Confirmed valid ldap uid.
        :return: Instance of User model.
        """
        # Pull user info.
        login_user = models.User.objects.get(username=uid)
        ldap_user_groups = self.get_ldap_user_groups(uid)

        # Set user group types.
        user_groups = login_user.groups.all().values_list('name', flat=True)
        if ldap_user_groups['director']:
            # Check if user is already in group.
            if 'CAE Director' not in user_groups:
                login_user.groups.add(Group.object.get(name='CAE Director'))
                logger.auth_info('{0}: Added user to CAE Director group.'.format(uid))
        if ldap_user_groups['attendant']:
            # Check if user is already in group.
            if 'CAE Attendant' not in user_groups:
                login_user.groups.add(Group.objects.get(name='CAE Attendant'))
                logger.auth_info('{0}: Added user to CAE Attendant group.'.format(uid))
        if ldap_user_groups['admin']:
            # Check if user is already in group.
            if 'CAE Admin' not in user_groups:
                login_user.groups.add(Group.objects.get(name='CAE Admin'))
                logger.auth_info('{0}: Added user to CAE Admin group.'.format(uid))
        if ldap_user_groups['programmer']:
            # Check if user is already in group.
            if 'CAE Programmer' not in user_groups:
                login_user.groups.add(Group.objects.get(name='CAE Programmer'))
                login_user.is_staff = True
                logger.auth_info('{0}: Added user to CAE Programmer group.'.format(uid))

        # Save model.
        login_user.save()
        logger.auth_info('{0}: CAE Center User groups set for user.'.format(uid))
        logger.auth_info('{0}: Attempting to get Main Campus user info...'.format(uid))

        # Check for associated Wmu model info.
        wmu_ldap = WmuAuthBackend()
        wmu_ldap.create_or_update_user_model(uid, password)
        wmu_ldap.create_or_update_wmu_user_model(uid)

        logger.auth_info('{0}: User model has been updated.'.format(uid))

        # Return fresh instance of model, in case instance was updated by check for Wmu User model.
        return models.User.objects.get(username=uid)

    def get_ldap_user_groups(self, uid):
        """
        Check if user is in any CAE Center groups.
        Note: Does not verify that passed uid is valid. In such a case, all groups will simply return False.
        :param uid: User id to check.
        :return: Dict of booleans for possible group membership.
        """
        self.ldap_lib.bind_server()

        user_groups = {
            'director': False,
            'attendant': False,
            'admin': False,
            'programmer': False,
        }

        # Check for ldap directors group match.
        ldap_directors = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['director_cn']),
            attributes=['memberUid'],
        )
        if ldap_directors is not None and uid in ldap_directors['memberUid']:
            user_groups['director'] = True

        # Check for ldap attendants group match.
        ldap_attendants = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['attendant_cn']),
            attributes=['memberUid'],
        )
        if ldap_attendants is not None and uid in ldap_attendants['memberUid']:
            user_groups['attendant'] = True

        # Check for ldap admins group match.
        ldap_admins = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['admin_cn']),
            attributes=['memberUid'],
        )
        if ldap_admins is not None and uid in ldap_admins['memberUid']:
            user_groups['admin'] = True

        # Check for ldap programmers group match.
        ldap_programmers = self.ldap_lib.search(
            search_base=settings.CAE_LDAP['group_dn'],
            search_filter='(cn={0})'.format(settings.CAE_LDAP['programmer_cn']),
            attributes=['memberUid'],
        )
        if ldap_programmers is not None and uid in ldap_programmers['memberUid']:
            user_groups['programmer'] = True

        self.ldap_lib.unbind_server()

        return user_groups
