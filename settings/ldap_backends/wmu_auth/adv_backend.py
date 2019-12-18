"""
Specific logic for custom authentication backends.

Note that, to work, these need the simple_ldap_lib git submodule imported, and the correct env settings set.
"""

# System Imports.
from django.conf import settings
from django.utils.text import slugify

# User Class Imports.
from cae_home import models
from settings import extra_settings
from settings.ldap_backends.base_auth import AbstractLDAPBackend


# Import logger.
logger = extra_settings.logging.getLogger(__name__)


class AdvisingAuthBackend(AbstractLDAPBackend):
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

    def create_or_update_user_model(self, *args, **kwargs):
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