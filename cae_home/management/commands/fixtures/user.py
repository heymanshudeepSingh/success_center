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
    create_site_themes(style)
    create_groups(style)
    create_wmu_users(style)
    create_addresses(style)


def create_site_themes(style):
    """
    Imports fixtures for profile theme models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/site_themes')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Site Theme') + ' models.\n')


def create_groups(style=None):
    """
    Creates django "auth_group" models and allocates proper permissions.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    """
    # Create base groups.
    group_array = create_permission_groups()

    # Get all permissions.
    all_permissions = Permission.objects.all()

    # Set director permissions. Want all, unconditionally.
    group_array[0].permissions.set(all_permissions)

    # Set building coordinator permissions. Want all, unconditionally.
    group_array[1].permissions.set(all_permissions)

    # Set programmer GA permissions. Want all, unconditionally.
    group_array[3].permissions.set(all_permissions)

    # Set programmer permissions. Want all, unconditionally.
    group_array[5].permissions.set(all_permissions)

    # Set admin GA permissions. Want all, unconditionally.
    group_array[2].permissions.set(all_permissions)

    # Set admin permissions. Want only the ones directly related to the CAE Center.
    cae_center_permissions = get_cae_center_permissions()
    group_array[4].permissions.set(cae_center_permissions)

    # Set attendant permissions. Want only CAE Center add privileges.
    filtered_permissions = []
    for permission in cae_center_permissions:
        if 'Can add' in permission.name or 'Can change user' in permission.name:
            filtered_permissions.append(permission)
    group_array[6].permissions.set(filtered_permissions)

    if style is not None:
        stdout.write('Populated ' + style.SQL_FIELD('Group') + ' models.\n')


def create_permission_groups():
    """
    Create main permission groups.
    Technically not a fixture, but still pretty integral to site running, and has no random data.
    :return: Array of permission groups.
    """
    # Create permission groups.
    director_group = Group.objects.get_or_create(name='CAE Director')[0]
    building_coordinator_group = Group.objects.get_or_create(name='CAE Building Coordinator')[0]
    admin_ga_group = Group.objects.get_or_create(name='CAE Admin GA')[0]
    programmer_ga_group = Group.objects.get_or_create(name='CAE Programmer GA')[0]
    admin_group = Group.objects.get_or_create(name='CAE Admin')[0]
    programmer_group = Group.objects.get_or_create(name='CAE Programmer')[0]
    attendant_group = Group.objects.get_or_create(name='CAE Attendant')[0]

    # Create and add to array. Used in testing.
    group_array = []                                # Index Num:
    group_array.append(director_group)              # 0
    group_array.append(building_coordinator_group)  # 1
    group_array.append(admin_ga_group)              # 2
    group_array.append(programmer_ga_group)         # 3
    group_array.append(admin_group)                 # 4
    group_array.append(programmer_group)            # 5
    group_array.append(attendant_group)             # 6
    return group_array


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

    # Remove permissions specific to creating or deleting users.
    for permission in app_permisson_list:
        if 'Can add user' in permission.name or \
           'Can delete user' in permission.name or\
           'Can add Profile' in permission.name or\
           'Can delete Profile' in permission.name:
            app_permisson_list.remove(permission)

    return app_permisson_list


def create_wmu_users(style):
    """
    Imports fixtures for WMU User models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/wmu_users')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Wmu User') + ' models.\n')


def create_addresses(style):
    """
    Imports fixtures for Address models.
    """
    # Nothing here yet.
    pass
