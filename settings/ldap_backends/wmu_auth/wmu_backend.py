"""
Specific logic for custom authentication backends.

Note that, to work, these need the simple_ldap_lib git submodule imported, and the correct env settings set.
"""

# System Imports.
import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber

# User Class Imports.
from cae_home import models
from settings import logging as init_logging
from settings.ldap_backends.base_auth import AbstractLDAPBackend
from settings.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend


# Import logger.
logger = init_logging.get_logger(__name__)


class WmuAuthBackend(AbstractLDAPBackend):
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

    #region User Create/Update Functions

    def create_or_update_user_model(self, uid, password):
        """
        Attempts to get and update User model with given username.
        In the event that no such model exists, instead create it from scratch using ldap info.

        Should only be called on known, valid and authenticated users.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :return: Instance of User model.
        """
        # Get user's LDAP info.
        user_ldap_info = self._get_all_user_info_from_bronconet(uid)

        try:
            # Call model to verify existence.
            user = models.User.objects.get(username=uid)

            # If we got this far, then model exists. Update.
            return self._update_user_model(uid, user_ldap_info)
        except models.User.DoesNotExist:
            # User model doesn't exist. Create new model.
            return self._create_user_model(uid, password, user_ldap_info)

    def _create_user_model(self, uid, password, user_ldap_info):
        """
        Creates new User model, using pulled ldap information.
        Logic here should be "first time model creation" logic.

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "create_or_update_user_model" function.
        :param uid: Confirmed valid ldap uid.
        :param password: Confirmed valid ldap pass.
        :param user_ldap_info: User's info from LDAP.
        :return: Instance of User model.
        """
        logger.auth_info('{0}: Attempting to create new User model...'.format(uid))

        # Create new user.
        login_user, created = models.User.objects.get_or_create(username=uid)

        # Double check that user was created. If not, then duplicate user Id's exists.
        if not created:
            # Duplicate Id's exist.
            # Most likely, there's a logic error in code and "_update_user_model" should have been called.
            login_user = None
            error_message = '{0}: Attempted to create user but uid already exists.'.format(uid)
            logger.auth_error(error_message)
            raise ValidationError(error_message)

        # Set password based on AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS setting.
        if settings.AUTH_BACKEND_USE_DJANGO_USER_PASSWORDS:
            login_user.set_password(password)
            login_user.save()

        # Set general (login) user values.
        login_user.email = '{0}@wmich.edu'.format(uid)

        # Save model.
        login_user.save()

        logger.auth_info('{0}: Set up "User" model. Now creating "WmuUser" model...'.format(uid))

        # Model created. Now run update logic to ensure all fields are properly set.
        login_user = self._update_user_model(uid, user_ldap_info)

        logger.auth_info('{0}: "WmuUser" model set. User creation complete.'.format(uid))

        return login_user

    def _update_user_model(self, uid, user_ldap_info):
        """
        Updates User model, using pulled Ldap information.
        Logic here should be fine to potentially run on every user login instance (including first).

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "create_or_update_user_model" function.
        :param uid: BroncoNet of user to update.
        :param user_ldap_info: User's info from LDAP.
        :return: Instance of User model.
        """
        # For now, just make sure the associated Wmu User model is created and up to date.
        self.create_or_update_wmu_user_model(uid, user_ldap_info=user_ldap_info)

        # Verify and set user ldap "active" status, according to main campus.
        self.verify_user_ldap_status(uid)

        logger.auth_info('{0}: User model has been updated.'.format(uid))

        # Return fresh instance of model, in case instance was updated by check for Wmu User model.
        return models.User.objects.get(username=uid)

    def create_or_update_wmu_user_model(self, uid, winno=None, skip_update=False, user_ldap_info=None):
        """
        Attempts to get and update WmuUser model with given BroncoNet.
        In the event that no such model exists, instead create it from scratch using ldap info from main campus.

        Should only be called on known, valid and authenticated users.
        :param uid: Id of user to get.
        :param winno: Optional winno field to eliminate a main campus LDAP call.
        :param skip_update: Boolean that prevents WmuUser model update attempts, if False.
        :param user_ldap_info: User's info from LDAP.
        :return: Instance of Wmu User model.
        """
        # Get user LDAP info, if not provided.
        if user_ldap_info is None:
            user_ldap_info = self._get_all_user_info_from_bronconet(uid)

        # Attempt to get related model. Just to see if it exists or not. If it does exist, update if applicable.
        try:
            # Call model to verify existence.
            wmu_user = models.WmuUser.objects.get(bronco_net=uid)

            # If we got this far, then model exists. Check if we want to update it.
            if not skip_update:
                # skip_update bool is False. Proceeding to update WmuUser values, if possible.
                logger.auth_info('{0}: WmuUser model found. Attempting to update...'.format(uid))
                wmu_user = self._update_wmu_user_model(uid, user_ldap_info)

            else:
                # skip_update bool is True. Skipping WmuUser update attempt.
                logger.auth_info('{0}: WmuUser model found, but Bool "only_create" is True. Skipping update.'.format(
                    uid,
                ))

        except models.WmuUser.DoesNotExist:
            # WmuUser model doesn't exist. Create new WmuUser model.
            logger.auth_info('{0}: Could not find WmuUser model. Creating new one...'.format(uid))
            wmu_user = self._create_wmu_user_model(uid, user_ldap_info, winno=winno)

        return wmu_user

    def _create_wmu_user_model(self, uid, user_ldap_info, winno=None):
        """
        Creates new Wmu User model, using pulled Ldap information.
        Logic here should be "first time model creation" logic.

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "create_or_update_wmu_user_model" function.
        :param uid: BroncoNet of user to create.
        :param user_ldap_info: User's LDAP info.
        :param winno: Optional winno field to eliminate a main campus LDAP call.
        :return: Instance of Wmu User model.
        """
        # Attempt to get related Django User model.
        try:
            login_user = models.User.objects.get(username=uid)
        except models.User.DoesNotExist:
            login_user = None

        # Get win number info.
        if winno is None:
            winno = self._parse_user_ldap_field(user_ldap_info, 'wmuBannerID')
            if winno is None or winno == '':
                raise ValidationError('User {0} got empty winno from Main Campus LDAP.'.format(uid))

        # Get first name info.
        if login_user is not None and login_user.first_name != '':
            # Associated login user exists and has name info. Use that.
            first_name = login_user.first_name
        else:
            # Associated login user does not exist or does not have name info. Check LDAP.
            first_name = self._parse_user_ldap_field(user_ldap_info, 'wmuFirstName')
            if first_name is None or first_name == '':
                first_name = self.get_backup_ldap_name(uid, first_name=True, user_ldap_info=user_ldap_info)

        # Get middle name info.
        middle_name = self._parse_user_ldap_field(user_ldap_info, 'wmuMiddleName')

        if login_user is not None and login_user.last_name != '':
            # Associated login user exists and has name info. Use that.
            last_name = login_user.last_name
        else:
            # Associated login user does not exist or does not have name info. Check LDAP.
            last_name = self._parse_user_ldap_field(user_ldap_info, 'wmuLastName')
            if last_name is None or last_name == '':
                last_name = self.get_backup_ldap_name(uid, last_name=True, user_ldap_info=user_ldap_info)

        # Get email info.
        if login_user is not None and login_user.email != '':
            # Associated login user exists and has email info. Use that.
            official_email = login_user.email
        else:
            # Associated login user does not exist or does not have email info. Check LDAP.
            official_email = self._parse_user_ldap_field(user_ldap_info, 'mail')
            if official_email is None or official_email == '':
                official_email = '{0}@wmich.edu'.format(uid)

        # Create WmuUser model.
        models.WmuUser.objects.create(
            bronco_net=uid,
            winno=winno,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            official_email=official_email,
        )

        # Check all field values in User model. Set if they were not set.
        if login_user is not None:
            set_value = False

            # Check first name.
            if login_user.first_name != first_name:
                login_user.first_name = first_name
                set_value = True

            # Check last name.
            if login_user.last_name != last_name:
                login_user.last_name = last_name
                set_value = True

            # Check email.
            if login_user.email != official_email:
                login_user.email = official_email
                set_value = True

            # If any User value was set, save changes.
            if set_value:
                login_user.save()

        # Attempt to update user profile.
        user_profile = models.Profile.get_profile(uid)
        if user_profile is None:
            logger.auth_error('{0}: Could not find profile for user.'.format(uid))
            raise ValueError('Could not find profile for user {0}.'.format(uid))

        # Get phone number info.
        phone_number = self._parse_user_ldap_field(user_ldap_info, 'homePhone')
        if phone_number is not None and phone_number != '':
            user_profile.phone_number = PhoneNumber.from_string(phone_number)
        user_profile.save()

        # Model created. Now run update logic to ensure all fields are properly set.
        return self._update_wmu_user_model(uid, user_ldap_info)

    def _update_wmu_user_model(self, uid, user_ldap_info):
        """
        Updates Wmu User model, using pulled Ldap information.
        Logic here should be fine to potentially run on every user login instance (including first).

        Should only be called on known, valid and authenticated users.
        Should only invoke this method through the "create_or_update_wmu_user_model" function.
        :param uid: BroncoNet of user to update.
        :param user_ldap_info: User's LDAP info.
        :return: Instance of Wmu User model.
        """
        # WmuUser model exists. Attempt to update information.
        adv_ldap = AdvisingAuthBackend()

        # Update major.
        adv_ldap.add_or_update_major(uid)

        logger.auth_info('{0}: WmuUser model has been updated.'.format(uid))

        # Return fresh instance of model, in case instance was updated by Advising Auth logic.
        return models.WmuUser.objects.get(bronco_net=uid)

    #endregion User Create/Update Functions

    #region User Ldap Status Functions

    def verify_user_ldap_status(self, uid, set_model_active_fields=True):
        """
        Verifies if student/employee is still enrolled/employed, according to main campus LDAP.
        If student is not enrolled/employed, we do a few extra checks to see if we can get useful data anyways.
        :param uid: BroncoNet of student to check.
        :param set_model_active_fields: Bool indicating if user "active" fields should be set based on ldap status.
        :return: None if no ldap data returned | (True, True) if actively enrolled/employed |
            (False, True) if not enrolled/employed, but within retention period (12 months) |
            (False, False) if not enrolled/employed, and outside of retention period.
        """
        # Attempt to get full student info from LDAP.
        ldap_info = self._get_all_user_info_from_bronconet(uid)

        # Now parse user ldap info.
        if ldap_info is not None:
            user_ldap_status = self._verify_user_ldap_status(uid, ldap_info)

            # Check if we should update User and Wmu User model "active" fields.
            if set_model_active_fields:
                # Fields need updating.
                user_ldap_status_is_active = user_ldap_status[0]
                user_ldap_status_in_retention = user_ldap_status[1]

                # Get models.
                login_user = models.User.objects.get(username=uid)
                wmu_user = models.WmuUser.objects.get(bronco_net=uid)

                # Set active fields.
                login_user.active = user_ldap_status_is_active
                wmu_user.active = user_ldap_status_in_retention

                # Save models.
                login_user.save()
                wmu_user.save()

            return user_ldap_status
        else:
            # Ldap info failed to return.

            # Check if we should update User and Wmu User model "active" fields.
            if set_model_active_fields:
                # Get models.
                login_user = models.User.objects.get(username=uid)
                wmu_user = models.WmuUser.objects.get(bronconet=uid)

                # Set active fields.
                login_user.active = False
                wmu_user.active = False

                # Save models.
                login_user.save()
                wmu_user.save()

            return None

    def _verify_user_ldap_status(self, uid, ldap_info):
        """
        Checks user's "active" status, according to main campus ldap. Uses several fields to determine.

        For all checks, we force convert and parse as string to avoid accidental Python "string to bool" shenanigans.
        Basically, only empty strings are false. (See https://docs.python.org/3/library/stdtypes.html for more info)

        So if we read in the string "false" from ldap, that would technically evaluate to True.
        Rather than dealing with that, we assume all fields may be strings, and just check for exact string match.

        :param uid: BroncoNet of student to check.
        :param ldap_info: ALL_ATTRIBUTES of user's main campus ldap info.
        :return: Tuple of (User is enrolled/active, User is within retention policy)
        """
        try:
            # Get wmuEnrolled field.
            try:
                # Handle for missing field.
                field_to_check = str(ldap_info['wmuEnrolled'][0]).strip().lower()
            except (KeyError, IndexError):
                field_to_check = None

            # Check wmuEnrolled field.
            if field_to_check == 'true':
                # User is currently enrolled.
                return (True, True)

            else:
                # User is not actively enrolled. We still want to check employee status, etc.

                # Get iNetUserStatus field.
                try:
                    # Handle for missing field.
                    field_to_check = str(ldap_info['inetUserStatus'][0]).strip().lower()
                except (KeyError, IndexError):
                    field_to_check = None

                # Check iNetUserStatus field.
                if field_to_check != 'active':
                    # Not enrolled and not active. Can set user to inactive in Django.
                    return (False, False)
                else:
                    # User is not enrolled but is active.

                    # Get wmuEmployeeExpiration.
                    try:
                        employee_expiration = datetime.datetime.strptime(
                            str(ldap_info['wmuEmployeeExpiration'][0]),
                            '%Y%m%d%H%M%S%z',
                        )

                        # Check if falls within valid employment period.
                        if employee_expiration is not None and employee_expiration >= timezone.now():
                            # Not enrolled, but still employed.
                            return (True, True)
                    except (KeyError, IndexError):
                        # Failed to get employee_expiration. Set to None.
                        employee_expiration = None

                    # Get wmuStudentExpiration.
                    try:
                        student_expiration = datetime.datetime.strptime(
                            str(ldap_info['wmuStudentExpiration'][0]),
                            '%Y%m%d%H%M%S%z',
                        )
                    except (KeyError, IndexError):
                        # Failed to get student_expiration. Set to None.
                        student_expiration = None

                    # Check if both are out of retention policy (12 months).
                    one_year_ago = (timezone.now() - timezone.timedelta(days=365))
                    if (student_expiration is not None and student_expiration >= one_year_ago) or \
                        (employee_expiration is not None and employee_expiration >= one_year_ago):

                        # Not enrolled, but within either student or employee retention period.
                        return (False, True)

                    # Not enrolled and not within retention periods.
                    return (False, False)

        except KeyError as err:
            # One or more relevant fields do not exist. Assuming we can set user to inactive in Django.
            logger.auth_error('{0}: Failed to find LDAP key for user during enrollment check. {1}'.format(uid, err))
            return (False, False)

    #endregion User Ldap Status Functions

    #region Ldap Get Attr Functions

    def _get_all_user_info_from_bronconet(self, bronco_net):
        """
        Attempts to get all student info from given BroncoNet.
        :param bronco_net: Student BroncoNet to attempt with.
        :return: All of student's LDAP info | None on failure.
        """
        # Bind to server.
        self.ldap_lib.bind_server(get_info=self.get_info)

        # Attempt to get full student info from LDAP.
        ldap_info = self.ldap_lib.search(search_filter='(uid={0})'.format(bronco_net), attributes='ALL_ATTRIBUTES')

        # Check that info was returned.
        if ldap_info is None:
            # Nothing returned. Try again, but filter by "wmuUID" field. This should work if the "uid" field fails.
            ldap_info = self.ldap_lib.search(search_filter='(wmuUID={0})'.format(bronco_net), attributes='ALL_ATTRIBUTES')

        # Unbind and return values.
        self.ldap_lib.unbind_server()
        return ldap_info

    def _get_all_user_info_from_winno(self, winno):
        """
        Attempts to get all student info from given Winno.
        :param winno: Student Winno to attempt with.
        :return: All of student's LDAP info | None on failure.
        """
        # Bind to server.
        self.ldap_lib.bind_server(get_info=self.get_info)

        # Attempt to get full student info from LDAP.
        ldap_info = self.ldap_lib.search(search_filter='(wmuBannerID={0})'.format(winno), attributes='ALL_ATTRIBUTES')

        # Unbind and return values.
        self.ldap_lib.unbind_server()
        return ldap_info

    def _parse_user_ldap_field(self, user_ldap_info, field_name):
        """
        Gets given field from passed LDAP info.
        :param user_ldap_info: User's LDAP info.
        :return: Parsed field | None on parse error.
        """
        # Check that args are populated.
        field_name = str(field_name).strip()
        if user_ldap_info is None or field_name == '':
            return None

        # Attempt to get field values.
        try:
            ldap_field = user_ldap_info[field_name]
            # Check how many values field has.
            if len(ldap_field) == 0:
                # Has no values.
                return None
            elif len(ldap_field) == 1:
                # Only has one value. Return value.
                return ldap_field[0]
            else:
                # Has more than 1 value. Return full tuple/list.
                return ldap_field
        except (KeyError, IndexError):
            # Failed to parse.
            return None

    def get_winno_from_bronconet(self, bronco_net):
        """
        Attempts to get Winno from student BroncoNet.
        :param bronco_net: Student BroncoNet to attempt with.
        :return: Student Winno | None on failure.
        """
        # Bind to server.
        self.ldap_lib.bind_server(get_info=self.get_info)

        # Get value from server.
        winno = self.ldap_lib.search(search_filter='(uid={0})'.format(bronco_net), attributes=['wmuBannerID'])

        # Fallback if first attempt fails.
        if winno is None:
            winno = self.ldap_lib.search(search_filter='(wmuUID={0})'.format(bronco_net), attributes=['wmuBannerID'])

        # Format value.
        if winno is not None:
            winno = winno['wmuBannerID'][0]

        # Unbind and return value.
        self.ldap_lib.unbind_server()
        return winno

    def get_bronconet_from_winno(self, winno):
        """
        Attempts to get BroncoNet from student Winno.
        :param winno: Student Winno to attempt with.
        :return: Student BroncoNet | None on failure.
        """
        # Bind to server.
        self.ldap_lib.bind_server(get_info=self.get_info)

        # Get value from server.
        bronco_net = self.ldap_lib.search(search_filter='(wmuBannerId={0})'.format(winno), attributes=['wmuUID'])

        # Format value.
        if bronco_net is not None:
            bronco_net = bronco_net['wmuUID'][0]

        # Check if bad bronco_net. Occurs in some older accounts.
        if bronco_net is not None and len(bronco_net) > 8:
            bronco_net = self.ldap_lib.search(search_filter='(wmuBannerId={0})'.format(winno), attributes=['uid'])

            # Format value.
            if bronco_net is not None:
                bronco_net = bronco_net['uid'][0]

        # Unbind and return value.
        self.ldap_lib.unbind_server()
        return bronco_net

    def get_backup_ldap_name(self, uid, user_ldap_info, first_name=False, last_name=False):
        """
        Function to get a "backup name" in case either first or last name fails to return from Wmu Ldap response.
        (First/last name values are required for Django WmuUser models).

        Attempts values in this order: givenName/sn, displayName, gecos, cn, bronconet_id.
        :param uid: User ID to search names for.
        :param user_ldap_info: User's LDAP info.
        :param first_name: Boolean indicating if is first name.
        :param last_name: Boolean indicating if is last name.
        :return: Name to use, or "Unknown" if all attempts failed.
        """
        # Attempt to get "givenName" or "sn" values. These seem to user first/last name values directly.
        if first_name:
            backup_name = self._format_backup_name(self._parse_user_ldap_field(user_ldap_info, 'givenName'))
        elif last_name:
            backup_name = self._format_backup_name(self._parse_user_ldap_field(user_ldap_info, 'sn'))
        else:
            backup_name = None

        # Attempt to get "displayName" value. Attempts to be full user's name, in proper "display" format?
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self._parse_user_ldap_field(user_ldap_info, 'displayName'))

        # Attempt to get "gecos" value. Seems to be an alternative to "givenName"?
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self._parse_user_ldap_field(user_ldap_info, 'gecos'))

        # Attempt to get "cn" value as last fallback attempt. Seems to be array of multiple possible versions of the
        # user's full name.
        if backup_name is None or backup_name == '':
            backup_name = self._format_backup_name(self._parse_user_ldap_field(user_ldap_info, 'cn'))

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

    #endregion Ldap Get Attr Functions

