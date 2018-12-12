"""
Seeder for "User" related Core Models.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from faker import Faker
from random import randint

from cae_home import models


def generate_model_seeds(model_count):
    """
    Calls individual seeder methods.
    """
    print('SEEDING User Model Group.')
    create_groups()
    create_users()
    create_addresses(model_count)
    create_phone_numbers(model_count)


def create_groups():
    """
    Creates django "auth_group" models and allocates proper permissions.
    """
    # Create base groups.
    director_group = Group.objects.get_or_create(name='CAE Director')[0]
    building_coordinator_group = Group.objects.get_or_create(name='CAE Building Coordinator')[0]
    admin_ga_group = Group.objects.get_or_create(name='CAE Admin GA')[0]
    programmer_ga_group = Group.objects.get_or_create(name='CAE Programmer GA')[0]
    attendant_group = Group.objects.get_or_create(name='CAE Attendant')[0]
    admin_group = Group.objects.get_or_create(name='CAE Admin')[0]
    programmer_group = Group.objects.get_or_create(name='CAE Programmer')[0]

    # Set director permissions. Want all, unconditionally.
    director_group.permissions.set(Permission.objects.all())

    # Set building coordinator permissions. Want all, unconditionally.
    building_coordinator_group.permissions.set(Permission.objects.all())

    # Set programmer permissions. Want all, unconditionally.
    programmer_group.permissions.set(Permission.objects.all())

    # Set programmer GA permissions. Want all, unconditionally.
    programmer_ga_group.permissions.set(Permission.objects.all())

    # Set admin GA permissions. Want all, unconditionally.
    admin_ga_group.permissions.set(Permission.objects.all())

    # Set admin permissions. Want only the ones directly related to the CAE Center.
    cae_center_permissions = get_cae_center_permissions()
    admin_group.permissions.set(cae_center_permissions)

    # Set attendant permissions. Want only CAE Center add privileges.
    filtered_permissions = []
    for permission in cae_center_permissions:
        if 'Can add' in permission.name or 'Can change user' in permission.name:
            filtered_permissions.append(permission)
    attendant_group.permissions.set(filtered_permissions)

    print('Populated group models.')


def get_cae_center_permissions():
    """
    Finds all permission models specific to the CAE Center.
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


def create_users():
    """
    Creates base user models.
    """
    default_password = 'temppass2'

    # Create superusers for every developer.
    models.User.get_or_create_superuser('brodriguez8774', '', default_password)  # Brandon
    models.User.get_or_create_superuser('ngf9321', '', default_password)  # Nick
    models.User.get_or_create_superuser('jdc4014', '', default_password)  # Jessie
    models.User.get_or_create_superuser('skd6970', '', default_password)  # Steven (Senior Design)
    models.User.get_or_create_superuser('jbn6294', '', default_password)  # Josh (Senior Design)

    # Create normal users for every main permission group.
    cae_director = models.User.get_or_create_user('cae_director', '', default_password)
    cae_building_coordinator = models.User.get_or_create_user('cae_building_coordinator', '', default_password)
    cae_admin_ga = models.User.get_or_create_user('cae_admin_ga', '', default_password)
    cae_programmer_ga = models.User.get_or_create_user('cae_programmer_ga', '', default_password)
    cae_admin = models.User.get_or_create_user('cae_admin', '', default_password)
    cae_programmer = models.User.get_or_create_user('cae_programmer', '', default_password)

    # Add permission groups to users.
    cae_director.groups.add(Group.objects.get(name='CAE Director'))
    cae_building_coordinator.groups.add(Group.objects.get(name='CAE Building Coordinator'))
    cae_admin_ga.groups.add(Group.objects.get(name='CAE Admin GA'))
    cae_programmer_ga.groups.add(Group.objects.get(name='CAE Programmer GA'))
    cae_admin.groups.add(Group.objects.get(name='CAE Admin'))
    cae_programmer.groups.add(Group.objects.get(name='CAE Programmer'))

    print('Populated user models.')


def create_addresses(model_count):
    """
    Creates address models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Address.objects.all())

    # Generate models equal to model count.
    for index in range(model_count - pre_initialized_count):
        street = faker_factory.building_number() + ' ' + faker_factory.street_address()
        city = faker_factory.city()
        state = faker_factory.state()
        zip = faker_factory.postalcode()
        if faker_factory.boolean():
            optional_street = faker_factory.secondary_address()
        else:
            optional_street = None

        models.Address.objects.create(street=street, optional_street=optional_street, city=city, state=state, zip=zip)

    print('Populated address models.')


def create_phone_numbers(model_count):
    """
    Creates phone number models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.PhoneNumber.objects.all())

    # Generate models equal to model count.
    for i in range(model_count - pre_initialized_count):
        phone_number = faker_factory.msisdn()
        models.PhoneNumber.objects.create(phone_number=phone_number)

    print('Populated phone number models.')
