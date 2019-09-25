"""
Specific logic for custom authentication backends.

Note that, to work, these need the simple_ldap_lib git submodule imported, and the correct env settings set.
"""

# System Imports.
from abc import abstractmethod
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from phonenumber_field.phonenumber import PhoneNumber

# User Class Imports.
from .base_auth import AbstractLDAPBackend
from cae_home import models
from settings import extra_settings


# Import logger.
logger = extra_settings.logging.getLogger(__name__)


class AbstractWmuBackend(AbstractLDAPBackend):
    """
    Abstract child of "AbstractLDAPBackend".
    The only difference is that it contains an additional method for creating a WMU user model.
    This is used for both CAE and WMU Authentication.

    Not included in the base abstract backend to keep it as generic and "universal" as possible.
    """

    # region Abstract Methods

    @abstractmethod
    def setup_abstract_class(self):
        """
        See parent class for description.
        """
        pass

    @abstractmethod
    def _create_new_user_from_ldap(self, uid, password):
        """
        See parent class for description.
        """
        pass

    # endregion Abstract Methods


class CaeAuthBackend(AbstractWmuBackend):
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
        # Set debug logging class name.
        self.debug_class = 'CAE'

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

    def _create_new_user_from_ldap(self, uid, password):
        """
        Attempts to create new user, using pulled ldap information.
        Should only be called on known, valid and authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return:
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('{0} Auth Backend: Attempting to create new user model...'.format(self.debug_class))

        # Connect to server and pull user's full info.
        ldap_user_info = self.get_ldap_user_info(uid, attributes=['uid', 'givenName', 'sn',])
        ldap_user_groups = self.get_ldap_user_groups(uid)

        # Create new user.
        login_user, created = models.User.objects.get_or_create(username=uid)

        # Double check that user was created. If not, then duplicate user ids exist somehow. Error.
        if created:
            # Set password.
            login_user.set_password(password)
            login_user.save()

            # Set general user values.
            login_user.email = '{0}@wmich.edu'.format(uid)
            login_user.first_name = ldap_user_info['givenName'][0].strip()
            login_user.last_name = ldap_user_info['sn'][0].strip()

            # Save model in case of error.
            login_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Created user new user model {1}. Now setting groups...'.format(
                    self.debug_class,
                    uid,
                ))

            # Set user group types.
            if ldap_user_groups['director']:
                login_user.groups.add(Group.object.get(name='CAE Director'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Added user to CAE Director group.'.format(self.debug_class))
            if ldap_user_groups['attendant']:
                login_user.groups.add(Group.objects.get(name='CAE Attendant'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Added user to CAE Attendant group.'.format(self.debug_class))
            if ldap_user_groups['admin']:
                login_user.groups.add(Group.objects.get(name='CAE Admin'))
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Added user to CAE Admin group.'.format(self.debug_class))
            if ldap_user_groups['programmer']:
                login_user.groups.add(Group.objects.get(name='CAE Programmer'))
                login_user.is_staff = True
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Added user to CAE Programmer group.'.format(self.debug_class))

            # Save model.
            login_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: CAE Center User groups set for user {1}.'.format(self.debug_class, uid))
                logger.info('{0} Auth Backend: Attempting to get Main Campus user info...'.format(self.debug_class))

            wmu_ldap = WmuAuthBackend()
            wmu_ldap.update_or_create_wmu_user_model(uid)

            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Imported Main Campus user info. User creation complete for user {1}.'.format(
                    self.debug_class,
                    uid,
                ))

        else:
            # Error. This shouldn't ever happen.
            login_user = None
            raise ValidationError('Error: Attempted to create user {0} but user with id already exists.'.format(uid))

        return login_user

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


class WmuAuthBackend(AbstractWmuBackend):
    """
    Custom authentication through the WMU main campus LDAP.
    """
    def setup_abstract_class(self):
        """
        Note: "check_credentials" value is set to False, because otherwise it will ping the LDAP server to verify
            the "master" credentials every time this Auth Backend is called.

            When set to active in settings, this backend is used every time a page needs to check permissions. So
            enabling "check_credentials" would potentially add a lot of extra time to each page load.
        """
        # Set debug logging class name.
        self.debug_class = 'WMU'

        # Set allowed email value in username.
        self.regex_username_match = self.regex_username_match.format('wmich.edu')

        # Set ldap connection settings.
        self.get_info = 'NONE'
        self.ldap_lib.set_host(settings.WMU_LDAP['host'])
        self.ldap_lib.set_master_account(
            settings.WMU_LDAP['login_dn'],
            settings.WMU_LDAP['login_password'],
            check_credentials=False,
            get_info=self.get_info,
        )
        self.ldap_lib.set_search_base(settings.WMU_LDAP['user_search_base'])
        self.ldap_lib.set_uid_attribute(settings.WMU_LDAP['default_uid'])

    def _create_new_user_from_ldap(self, uid, password):
        """
        Attempts to create new user, using pulled ldap information.
        Should only be called on known, valid and authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        """
        if settings.AUTH_BACKEND_DEBUG:
            logger.info('{0} Auth Backend: Attempting to create new User model...'.format(self.debug_class))

        # Create new user.
        login_user, created = models.User.objects.get_or_create(username=uid)

        # Double check that user was created. If not, then duplicate user ids exist somehow. Error.
        if created:
            # Set password.
            login_user.set_password(password)
            login_user.save()

            # Set general (login) user values.
            login_user.email = '{0}@wmich.edu'.format(uid)

            # Save model in case of error.
            login_user.save()
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Created user new User model {1}. Now creating WmuUser model...'.format(
                    self.debug_class,
                    uid,
                ))

            self.update_or_create_wmu_user_model(uid)

            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Related WMU User model set. User creation complete for user {1}.'.format(
                    self.debug_class,
                    uid,
                ))

        else:
            # Error. This shouldn't ever happen.
            login_user = None
            raise ValidationError(
                'Error: Attempted to create user {0} but user with id already exists.'.format(uid))

        return login_user

    def get_bronconet_from_winno(self, winno):
        """
        Attempts to get bronconet from student winno.
        :param winno: Student winno to use in search.
        """
        # Get value from server.
        self.ldap_lib.bind_server(get_info=self.get_info)
        bronco_net = self.ldap_lib.search(search_filter='(wmuBannerId={0})'.format(winno), attributes=['wmuUID'])

        if bronco_net is not None:
            bronco_net = bronco_net['wmuUID'][0]

        # Check if bad bronco_net. Occurs in some older accounts.
        if bronco_net is not None and len(bronco_net) > 8:
            bronco_net = self.ldap_lib.search(search_filter='(wmuBannerId={0})'.format(winno), attributes=['uid'])
            bronco_net = bronco_net['uid'][0]

        self.ldap_lib.unbind_server()
        return bronco_net

    def update_or_create_wmu_user_model(self, uid, winno=None):
        """
        Attempts to get and update WmuUser model with given bronconet.
        In the event that no such model exists, instead create it from scratch using ldap info from main campus.
        :param uid: Id of user to get.
        :return: Instance of WmuUser model.
        """
        # Attempt to get related model. Just to see if it exists or not. If it does exist, update if applicable.
        try:
            wmu_user = models.WmuUser.objects.get(bronco_net=uid)

            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: WmuUser model found for "{1}". Attempting to update...'.format(
                    self.debug_class,
                    uid,
                ))

            # WmuUser model exists. Attempt to update information.
            adv_ldap = AdvisingAuthBackend()

            # Update major.
            adv_ldap.add_or_update_major(uid)

            # Refresh all model data and return.
            return models.WmuUser.objects.get(bronco_net=uid)

        except models.WmuUser.DoesNotExist:
            # Doesn't exist. Create new WmuUser model.

            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Could not find WmuUser model for "{1}". Creating new one...'.format(
                    self.debug_class,
                    uid,
                ))

            # Get win number info.
            if winno is None:
                winno = self.get_ldap_user_attribute(uid, 'wmuBannerID')
                if winno is None or winno == '':
                    raise ValidationError('User {0} got empty winno from Main Campus LDAP.'.format(uid))

            # Get first name info.
            first_name = self.get_ldap_user_attribute(uid, 'wmuFirstName')
            if first_name is None or first_name == '':
                first_name = self.get_backup_ldap_name(uid, first_name=True)

            # Get middle name info.
            middle_name = self.get_ldap_user_attribute(uid, 'wmuMiddleName')

            # Get last name info.
            last_name = self.get_ldap_user_attribute(uid, 'wmuLastName')
            if last_name is None or last_name == '':
                last_name = self.get_backup_ldap_name(uid, last_name=True)

            # Get email info.
            official_email = self.get_ldap_user_attribute(uid, 'mail')
            if official_email is None or official_email == '':
                official_email = '{0}@wmich.edu'.format(uid)

            adv_ldap = AdvisingAuthBackend()
            returned_majors = adv_ldap.get_student_major(uid)

            models.WmuUser.objects.create(
                bronco_net=uid,
                winno=winno,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                official_email=official_email,
            )

            # Update major.
            adv_ldap.add_or_update_major(uid)

        # Attempt to update user profile.
        user_profile = models.Profile.get_profile(uid)
        if user_profile is None:
            raise ValueError('Could not find profile for user {0}.'.format(uid))

        # Get phone number info.
        phone_number = self.get_ldap_user_attribute(uid, 'homePhone')
        if phone_number is not None and phone_number != '':
            user_profile.phone_number = PhoneNumber.from_string(phone_number)
        user_profile.save()

        return models.WmuUser.objects.get(bronco_net=uid)

    def get_backup_ldap_name(self, uid, first_name=False, last_name=False):
        """
        Function to get a "backup name" in case either first or last name fails to return from wmu main campus.
        (First/last name values are required for WMUUser models).

        Attempts values in this order: givenName/sn, displayName, gecos, cn, bronconet_id.
        :param uid: User ID to search names for.
        :param first_name: Boolean indicating if is first name.
        :param last_name: Boolean indicating if is last name.
        :return: Name to use, or "Unknown" if all attempts failed.
        """
        # Attempt to get "givenName" or "sn" values. These seem to user first/last name values directly.
        if first_name:
            backup_name = self._format_backup_name(self.get_ldap_user_attribute(uid, 'givenName'))
        elif last_name:
            backup_name = self._format_backup_name(self.get_ldap_user_attribute(uid, 'sn'))
        else:
            backup_name = None

        # Attempt to get "displayName" value. Attempts to be full user's name, in proper "display" format?
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self.get_ldap_user_attribute(uid, 'displayName'))

        # Attempt to get "gecos" value. Seems to be an alternative to "givenName"?
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self.get_ldap_user_attribute(uid, 'gecos'))

        # Attempt to get "cn" value as last fallback attempt. Seems to be array of multiple possible versions of the
        # user's full name.
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self.get_ldap_user_attribute(uid, 'cn'))

        # All above attempts failed. Default to uid.
        if backup_name is None or backup_name == '':
            backup_name = uid

        return backup_name

    def _format_backup_name(self, backup_name):
        """
        Changes Ldap name value to desired format.
        :param backup_name: Value to format.
        :return: Formatted name string | None.
        """
        # If in array, get inner value, or None for empty arrays.
        if isinstance(backup_name, list):
            if len(backup_name) > 0:
                backup_name = backup_name[0]
            else:
                backup_name = None

        # If is string, then strip extra whitespace characters.
        if isinstance(backup_name, str):
            if len(backup_name) > 0:
                backup_name = backup_name.strip()
            else:
                backup_name = None
        else:
            # If not a string, then set to None.
            backup_name = None

        return backup_name


class AdvisingAuthBackend(AbstractWmuBackend):
    """
    It seems the CAE Center credentials for WMU LDAP are missing some student fields.
    Thus, we need to use advising credentials at times, but we want to use only when absolutely necessary.
    """
    def setup_abstract_class(self):
        # Set debug logging class name.
        self.debug_class = 'ADV'

        # Set ldap connection settings.
        self.get_info = 'NONE'
        self.ldap_lib.set_host(settings.WMU_LDAP['host'])
        self.ldap_lib.set_master_account(
            settings.ADV_LDAP['login_dn'],
            settings.ADV_LDAP['login_password'],
            check_credentials=False,
            get_info=self.get_info,
        )
        self.ldap_lib.set_search_base(settings.WMU_LDAP['user_search_base'])
        self.ldap_lib.set_uid_attribute(settings.WMU_LDAP['default_uid'])

        # "NotImplemenetedError" text.
        self._not_implemented_string = 'This method is intentionally unimplemented for AdvisingAuthBackend. To use ' \
                                       'this method, please invoke from CaeAuthBackend or WmuAuthBackend instead.'

    def _create_new_user_from_ldap(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    # region User Auth

    def authenticate(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def _parse_username(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def _validate_django_user(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def _validate_ldap_user(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def user_can_authenticate(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def get_user(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    #endregion User Auth

    # region User Permissions

    def _get_user_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def _get_group_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def _get_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def get_user_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def get_group_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def get_all_permissions(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def has_perm(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    def has_module_perms(self, *args, **kwargs):
        raise NotImplementedError(self._not_implemented_string)

    # endregion User Permissions

    def add_or_update_major(self, uid):
        """
        Checks with main campus and attempts to add/update related Majors for WmuUser.
        Note: This assumes Django already has a WmuUser model for the associated uid. Will fail otherwise.
        :param uid: BroncoNet value for WmuUser.
        """
        wmu_user = models.WmuUser.objects.get(bronco_net=uid)

        returned_majors = self.get_student_major(uid)

        # Check if student is currently associated with more than one major.
        if isinstance(returned_majors, list):
            # Student is associated with more than one major. Handle for all.
            for returned_major in returned_majors:

                # Check each major to see if relation is in django's models and active.
                if not models.WmuUserMajorRelationship.check_if_user_has_major_active(wmu_user, returned_major):
                    # Relation not found. Create new.
                    if settings.AUTH_BACKEND_DEBUG:
                        logger.info('{0} Auth Backend: Django major "{1}" does not match new User\'s return value '
                                    'from ldap "{2}". Updating...'.format(
                            self.debug_class,
                            wmu_user.major.all(),
                            returned_majors,
                        ))
                    models.WmuUserMajorRelationship.objects.create(
                        wmu_user=wmu_user,
                        major=returned_major,
                    )

        else:
            # Student is only associated with one major.
            returned_major = returned_majors

            # Check if relation is in django's models and active.
            if not models.WmuUserMajorRelationship.check_if_user_has_major_active(wmu_user, returned_major):
                # Relation not found. Create new.
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Django major "{1}" does not match new User\'s return value from '
                                'ldap "{2}". Updating...'.format(
                        self.debug_class,
                        wmu_user.major.all(),
                        returned_majors,
                    ))
                models.WmuUserMajorRelationship.objects.create(
                    wmu_user=wmu_user,
                    major=returned_major,
                )

    def get_student_major(self, uid):
        """
        Gets major(s) for given WmuUser model.
        :param uid: Bronconet corresponding to student.
        :return: Django Major model corresponding to student.
        """
        # Get win number info.
        winno = self.get_ldap_user_attribute(uid, 'wmuBannerID')


        # Attempt to get student major "ProgramCode".
        student_code = self.get_ldap_user_attribute(uid, 'wmuStudentMajor')

        # Check if program code was valid.
        if student_code is not None and student_code != '':
            if settings.AUTH_BACKEND_DEBUG:
                logger.info('{0} Auth Backend: Found student wmuProgramCode: {1}'.format(self.debug_class, student_code))

            search_base = 'ou=Majors,ou=WMUCourses,o=wmich.edu,dc=wmich,dc=edu'
            search_filter = '(wmuStudentMajor={0})'.format(student_code)
            attributes = 'ALL_ATTRIBUTES'

            if isinstance(student_code, list):
                major_list = []
                for code in student_code:
                    major_list.append(self._get_student_major(code, search_base, search_filter, attributes))
                return major_list
            else:
                major = self._get_student_major(student_code, search_base, search_filter, attributes)

            return major
        else:

            if settings.AUTH_BACKEND_DEBUG:
                logger.warning(
                    '{0} Auth Backend: Failed to get wmuStudentMajor LDAP field for {1}. Defaulting to "Unknown" major.'.format(
                        self.debug_class,
                        uid
                    ))
            return models.Major.objects.get(slug='unk')

    def _get_student_major(self, student_code, search_base, search_filter, attributes):
        """
        Get Django Major model for with provided information.
        :param student_code: Student code to search for model of.
        :param search_base: LDAP main campus search_base for Major info.
        :param search_filter: LDAP main campus search_filter for Major info.
        :param attributes: LDAP main campus attributes to get for Major info.
        :return: Major model.
        """
        # First check that a student code was passed.
        if student_code is not None and student_code != '':
            # Attempt to get full major info from LDAP.
            self.ldap_lib.bind_server(get_info=self.get_info)
            ldap_major = self.ldap_lib.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=attributes,
            )
            self.ldap_lib.unbind_server()

            if ldap_major is not None:
                # Got valid response from LDAP.
                if settings.AUTH_BACKEND_DEBUG:
                    logger.info('{0} Auth Backend: Found ldap_major: {1}'.format(self.debug_class, ldap_major))

                try:
                    # Attempt to get major.
                    major = models.Major.objects.get(student_code=student_code)
                    if settings.AUTH_BACKEND_DEBUG:
                        logger.info('{0} Auth Backend: Found Django Major: {1}'.format(self.debug_class, major))
                    return major
                except models.Major.DoesNotExist:
                    if settings.AUTH_BACKEND_DEBUG:
                        logger.info('{0} Auth Backend: Django Major does not exist. Creating new...'.format(
                        self.debug_class,
                    ))

                    # Get major's department.
                    department = self._get_major_department(ldap_major)

                    # Get major's program_code.
                    program_code = self._get_major_program_code(ldap_major)

                    # Get major's display_name.
                    display_name = self._get_major_display_name(ldap_major)

                    # Get major's degree_level.
                    degree_level = self._get_degree_level_from_program_code(program_code)

                    try:
                        return models.Major.objects.create(
                            department=department,
                            student_code=student_code,
                            program_code=program_code,
                            name=display_name,
                            degree_level=degree_level,
                            slug=slugify(student_code),
                        )
                    except Exception as err:
                        logger.error('Failed to create major: {0}'.format(err))
                        return models.Major.objects.get(slug='unk')

            else:
                # Could not get valid response from LDAP. Default to unknown.
                return models.Major.objects.get(slug='unk')

        else:
            # Passed student code was not a real value. Skip fetch attempt and just return unknown major.
            return models.Major.objects.get(slug='unk')

    def _get_major_department(self, ldap_major):
        """
        Attempts to get Django Department model for major.
        :param ldap_major: LDAP information for major.
        :return: Django Department model for major.
        """
        try:
            # Attempt to read ldap value.
            ldap_department = str(ldap_major['wmuDepartmentName'][0]).strip()

            try:
                # Attempt to get Django model.
                return models.Department.objects.get(name=ldap_department)
            except models.Department.DoesNotExist:
                return models.Department.objects.create(
                    name=ldap_department,
                    slug=slugify(ldap_department),
                )

        except (KeyError, IndexError):
            return models.Department.objects.get(slug='na-unknown')

    def _get_major_display_name(self, ldap_major):
        """
        Attempts to parse display_name from LDAP Major information.
        :param ldap_major: LDAP information for Major
        :return: display_name for Major.
        """
        # Attempt to get major's display_name.
        try:
            return str(ldap_major['displayName'][0]).strip()
        except KeyError:
            # 'displayName' field does not exist for entry. Attempt to use title.
            try:
                return str(ldap_major['title'][0]).strip()
            except KeyError:
                # 'title' field does not exist for entry. Default to student_code value.
                return str(ldap_major['wmuStudentMajor'][0]).strip()

    def _get_major_program_code(self, ldap_major):
        """
        Attempts to parse program_code from LDAP Major information.
        :param ldap_major: LDAP information for Major.
        :return: program_code for Major.
        """
        # Attempt to get full program code.
        try:
            program_code = ldap_major['wmuProgramCode']

            # Check if multiple program_codes exist for major.
            if len(program_code) > 1:
                # Two or more program_codes exist for major.
                # Check each one for format we want. Should be of format "*-*-*" where each "*" is one or more letters.
                for code in program_code:
                    code_split = code.split('-')
                    if len(code_split) == 3:
                        return str(code).strip()

                # If we made it this far, then the code format we want is not present. Just use first one.
                return str(program_code[0]).strip()
            elif len(program_code) == 1:
                # Only one program_code exists for major.
                return str(program_code[0]).strip()
            else:
                # The program_code field did not return anything meaningful. Default to student_code value.
                return str(ldap_major['wmuProgramCode'][0]).strip()
        except KeyError:
            # 'wmuProgramCode' field does not exist for entry. Default to student_code value.
            return str(ldap_major['wmuStudentMajor'][0]).strip()

    def _get_degree_level_from_program_code(self, program_code):
        """
        Attempts to parse degree_level from program_code.
        :param program_code: The LDAP program_code for the Major.
        :return: The Major's degree_level.
        """
        # Attempt to get degree level.
        program_split = program_code.split('-')
        if len(program_split) == 3:
            # Parse from our preferred format.
            degree_key = program_split[1]

            if degree_key[:3] == 'PHD':
                return models.Major.get_degree_level_as_int('Phd')
            elif degree_key[:2] == 'MS':
                return models.Major.get_degree_level_as_int('Masters')
            elif degree_key[:2] == 'BS':
                return models.Major.get_degree_level_as_int('Bachelors')
            elif degree_key[:2] == 'AS':
                return models.Major.get_degree_level_as_int('Associates')
            else:
                return models.Major.get_degree_level_as_int('Unknown')

        elif len(program_split) == 2:
            program_split = program_split[0]

            # First trim off right hand side of code that we don't want.
            program_split = program_split[:3]
            # Then trim off left hand side of code that we don't want.
            program_split = program_split[-2:]

            if program_split == 'MS':
                return models.Major.get_degree_level_as_int('Masters')
            elif program_split == 'BS':
                return models.Major.get_degree_level_as_int('Bachelors')
            elif program_split == 'AS':
                return models.Major.get_degree_level_as_int('Associates')
            else:
                return models.Major.get_degree_level_as_int('Unknown')

        elif len(program_split) == 1:
            # Could not split. There was no "-" character in program_code.
            program_split = program_split[0]

            # Check if program_code is only 4 characters.
            if len(program_split) == 4:
                program_char = program_split[3]

                # Check last character.
                if program_char == 'P':
                    return models.Major.get_degree_level_as_int('Associates')
                elif program_char == 'J':
                    return models.Major.get_degree_level_as_int('Bachelors')
                elif program_char == 'M' or program_char == 'Q':
                    return models.Major.get_degree_level_as_int('Masters')
                elif program_char == 'D':
                    return models.Major.get_degree_level_as_int('Phd')
                else:
                    return models.Major.get_degree_level_as_int('Unknown')

        else:
            # Unkown program_code format.
            logger.warning('{0} Auth Backend: Could not parse degree_level from program_code "{1}".'.format(
                self.debug_class,
                program_code,
            ))
            return models.Major.get_degree_level_as_int('Unknown')
