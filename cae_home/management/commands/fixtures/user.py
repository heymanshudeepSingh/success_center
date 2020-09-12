"""
Fixture imports for "User" related Core Models.
"""

# System Imports.
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from sys import stdout


def import_model_fixtures(style):
    """
    Calls individual fixture methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('IMPORTING FIXTURES for User Model Group.\n'))
    create_site_themes(style, display_output=True)
    create_groups(style, display_output=True)
    create_wmu_users(style, display_output=True)
    create_addresses(style, display_output=True)


def create_site_themes(style, display_output=False):
    """
    Imports fixtures for profile theme models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/site_themes')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Site Theme') + ' models.\n')


#region Group and Permission Fixtures
# Technically these aren't fixtures, but they're pretty integral to the site running, and not randomized.

def create_groups(style=None, display_output=False):
    """
    Creates django "auth_group" models and allocates proper permissions.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # Create base groups.
    group_dict = create_permission_groups(as_dict=True)

    general_permissions = get_general_wmu_permissions()

    set_cae_group_permissions(group_dict)
    set_wmu_group_permissions(group_dict, general_permissions)
    set_step_group_permissions(group_dict, general_permissions)

    if display_output and style is not None:
        stdout.write('Populated ' + style.SQL_FIELD('Group') + ' models.\n')


def create_permission_groups(as_dict=False):
    """
    Create main permission groups.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    :param as_dict: Bool indicating if return value should be list or dict.
    :return: Array or dict of permission groups.
    """
    # Create CAE Center permission groups.
    director_group = Group.objects.get_or_create(name='CAE Director')[0]
    building_coordinator_group = Group.objects.get_or_create(name='CAE Building Coordinator')[0]
    admin_ga_group = Group.objects.get_or_create(name='CAE Admin GA')[0]
    programmer_ga_group = Group.objects.get_or_create(name='CAE Programmer GA')[0]
    admin_group = Group.objects.get_or_create(name='CAE Admin')[0]
    programmer_group = Group.objects.get_or_create(name='CAE Programmer')[0]
    attendant_group = Group.objects.get_or_create(name='CAE Attendant')[0]

    # Create general WMU permission groups.
    wmu_faculty_group = Group.objects.get_or_create(name='WMU Faculty')[0]
    wmu_teacher_group = Group.objects.get_or_create(name='WMU Teacher')[0]
    wmu_student_group = Group.objects.get_or_create(name='WMU Student')[0]

    # Create Success Center permission groups.
    step_admin_group = Group.objects.get_or_create(name='STEP Admin')[0]
    step_employee_group = Group.objects.get_or_create(name='STEP Employee')[0]

    # Check if return value should be list or dict format.
    if as_dict:
        # Create and add to dict.
        group_dict = {
            'cae_director': director_group,
            'building_coordinator': building_coordinator_group,
            'cae_admin_ga': admin_ga_group,
            'cae_programmer_ga': programmer_ga_group,
            'cae_admin': admin_group,
            'cae_programmer': programmer_group,
            'cae_attendant': attendant_group,
            'wmu_faculty': wmu_faculty_group,
            'wmu_teacher': wmu_teacher_group,
            'wmu_student': wmu_student_group,
            'step_admin': step_admin_group,
            'step_employee': step_employee_group,
        }
        return group_dict
    else:
        # Create and add to array. Used in testing.
        group_array = [                     # Index Num:
            director_group,                 # 0
            building_coordinator_group,     # 1
            admin_ga_group,                 # 2
            programmer_ga_group,            # 3
            admin_group,                    # 4
            programmer_group,               # 5
            attendant_group,                # 6
            wmu_faculty_group,              # 7
            wmu_teacher_group,              # 8
            wmu_student_group,              # 9
            step_admin_group,               # 10
            step_employee_group,            # 11
        ]
        return group_array


#region Set Permission Functions

def set_cae_group_permissions(group_dict):
    """
    Sets all permissions related to CAE Center groups.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # Get all permissions.
    all_permissions = Permission.objects.all()

    # Set CAE Director permissions. Want all, unconditionally.
    group_dict['cae_director'].permissions.set(all_permissions)

    # Set Building Coordinator permissions. Want all, unconditionally.
    group_dict['building_coordinator'].permissions.set(all_permissions)

    # Set CAE Programmer GA permissions. Want all, unconditionally.
    group_dict['cae_programmer_ga'].permissions.set(all_permissions)

    # Set CAE Programmer permissions. Want all, unconditionally.
    group_dict['cae_programmer'].permissions.set(all_permissions)

    # Set CAE Admin GA permissions. Want all, unconditionally.
    group_dict['cae_admin_ga'].permissions.set(all_permissions)

    # Set CAE Admin permissions. Want only the ones directly related to the CAE Center.
    cae_center_permissions = get_cae_center_permissions()
    group_dict['cae_admin'].permissions.set(cae_center_permissions)

    # Set CAE Attendant permissions. Want only CAE Center add privileges.
    filtered_permissions = []
    for permission in cae_center_permissions:
        if 'Can add' in permission.name or 'Can change user' in permission.name:
            filtered_permissions.append(permission)
    group_dict['cae_attendant'].permissions.set(filtered_permissions)


def set_wmu_group_permissions(group_dict, general_permissions):
    """
    Sets all permissions related to general WMU groups.

    Note that for now, faculty and teacher are placeholders in case we ever need them in the future.
    Effectively, they currently work the same as the "student" group.

    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # Set WMU Faculty permissions.
    group_dict['wmu_faculty'].permissions.set(general_permissions)

    # Set WMU Teacher permissions.
    group_dict['wmu_teacher'].permissions.set(general_permissions)

    # Set WMU Student permissions.
    group_dict['wmu_student'].permissions.set(general_permissions)


def set_step_group_permissions(group_dict, general_permissions):
    """
    Sets all permissions related to STEP Program (Success Center) groups.

    Note that for now, the Employee group is a placeholder in case we ever need them it in the future.
    Effectively, it currently works the same as the "admin" group.

    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # Set STEP Admin permissions.
    success_center_permissions = get_step_permissions() + general_permissions

    # Set STEP Admin permissions.
    group_dict['step_admin'].permissions.set(success_center_permissions)

    # Set STEP Employee permissions.
    group_dict['step_employee'].permissions.set(success_center_permissions)

#endregion Set Permission Functions


#region Get Permission Functions

def get_general_wmu_permissions():
    """
    Finds all permission models specific to general WMU things. Such as viewing majors, rooms, etc.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # First find all content types for the CAE Home app.
    app_content_types = ContentType.objects.filter(app_label__contains='cae_home')

    # Get all id's of found content types.
    app_content_ids = []
    for content_type in app_content_types:
        app_content_ids.append(content_type.id)

    # Use id's to filter permissions objects.
    genneral_permission_list = []
    for content_id in app_content_ids:
        query_set = Permission.objects.filter(content_type_id=content_id)
        for item in query_set:
            if 'view' in item.name:
                genneral_permission_list.append(item)

    return genneral_permission_list


def get_cae_center_permissions():
    """
    Finds all permission models specific to the CAE Center.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    :return: A list of all permission models for the CAE Center.
    """
    # First find all content types with "cae" in the name.
    app_content_types = ContentType.objects.filter(app_label__contains='cae')

    # Get all id's of found content types.
    app_content_ids = []
    for content_type in app_content_types:
        app_content_ids.append(content_type.id)

    # Use id's to filter permissions objects.
    app_permisson_list = []
    for content_id in app_content_ids:
        query_set = Permission.objects.filter(content_type_id=content_id)
        for item in query_set:
            app_permisson_list.append(item)

    # Remove permissions specific to creating or deleting users. These match because of "cae_home" namespace.
    for permission in app_permisson_list:
        if 'Can add user' in permission.name or \
           'Can delete user' in permission.name or\
           'Can add Profile' in permission.name or\
           'Can delete Profile' in permission.name:
            app_permisson_list.remove(permission)

    return app_permisson_list


def get_step_permissions():
    """
    Finds all permission models specific to the STEP program (success center).
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    :return: A list of all permission models for the STEP program.
    """
    # First find all content types with "cae" in the name.
    app_content_types = ContentType.objects.filter(app_label__contains='success_center')

    # Get all id's of found content types.
    app_content_ids = []
    for content_type in app_content_types:
        app_content_ids.append(content_type.id)

    # Use id's to filter permissions objects.
    app_permisson_list = []
    for content_id in app_content_ids:
        query_set = Permission.objects.filter(content_type_id=content_id)
        for item in query_set:
            app_permisson_list.append(item)

    return app_permisson_list

#endregion Get Permission Functions

#endregion Group and Permission Fixtures


def create_wmu_users(style, display_output=False):
    """
    Imports fixtures for WMU User models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/wmu_users')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Wmu User') + ' models.\n')


def create_addresses(style, display_output=False):
    """
    Imports fixtures for Address models.
    """
    # Nothing here yet.
    pass
