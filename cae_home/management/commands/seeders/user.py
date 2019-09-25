"""
Seeder for "User" related Core Models.
"""

# System Imports.
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from faker import Faker
from faker_e164.providers import E164Provider
from phonenumber_field.phonenumber import PhoneNumber
from random import randint
from sys import stdout

# User Class Imports.
from cae_home import models


default_password = settings.USER_SEED_PASSWORD


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING User Model Group.\n'))
    create_site_themes(style)
    create_groups(style)
    create_users(style)
    create_addresses(style, model_count)
    create_wmu_users(style, model_count)


def create_site_themes(style):
    """
    Creates profile theme models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/site_themes')

    stdout.write('Populated ' + style.SQL_FIELD('Site Theme') + ' models.\n')


def create_groups(style=None):
    """
    Creates django "auth_group" models and allocates proper permissions.
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


def create_users(style):
    """
    Creates base user models.
    """
    # Create extra superusers for developers.
    models.User.get_or_create_superuser('brodriguez8774', '', default_password)  # Brandon
    models.User.get_or_create_superuser('skd6970', '', default_password)  # Steven (Senior Design)
    models.User.get_or_create_superuser('jbn6294', '', default_password)  # Josh (Senior Design)

    create_permission_group_users(password=default_password)

    stdout.write('Populated ' + style.SQL_FIELD('User') + ' models.\n')


def create_permission_group_users(password=default_password, with_names=True):
    """
    Create specific users for each main group permission.
    :param password: Password to seed users with.
    :return: Array of users.
    """
    # Create normal users for every main permission group.
    cae_director = models.User.get_or_create_user('cae_director', '', password)
    cae_building_coordinator = models.User.get_or_create_user('cae_building_coordinator', '', password)
    cae_admin_ga = models.User.get_or_create_user('cae_admin_ga', '', password)
    cae_programmer_ga = models.User.get_or_create_user('cae_programmer_ga', '', password)
    cae_admin = models.User.get_or_create_user('cae_admin', '', password)
    cae_programmer = models.User.get_or_create_user('cae_programmer', '', password)
    cae_attendant = models.User.get_or_create_user('cae_attendant', '', password)

    # Set their names.
    if with_names:
        cae_admin.first_name = "Gumball"
        cae_admin.last_name = "Watterson"
        cae_admin.save()
        cae_admin_ga.first_name = "Homer"
        cae_admin_ga.last_name = "Simpson"
        cae_admin_ga.save()
        cae_attendant.first_name = "Darwin"
        cae_attendant.last_name = "Watterson"
        cae_attendant.save()
        cae_programmer.first_name = "Phillip"
        cae_programmer.last_name = "Fry"
        cae_programmer.save()
        cae_programmer_ga.first_name = "Chosen"
        cae_programmer_ga.last_name = "One"
        cae_programmer_ga.save()

    # Add permission groups to users.
    cae_director.groups.add(Group.objects.get(name='CAE Director'))
    cae_building_coordinator.groups.add(Group.objects.get(name='CAE Building Coordinator'))
    cae_admin_ga.groups.add(Group.objects.get(name='CAE Admin GA'), Group.objects.get(name='CAE Admin'))
    cae_programmer_ga.groups.add(Group.objects.get(name='CAE Programmer GA'), Group.objects.get(name='CAE Programmer'))
    cae_admin.groups.add(Group.objects.get(name='CAE Admin'))
    cae_programmer.groups.add(Group.objects.get(name='CAE Programmer'))
    cae_attendant.groups.add(Group.objects.get(name='CAE Attendant'))

    # Create and add to array. Used in testing.
    user_array = []                                 # Index Num:
    user_array.append(cae_director)                 # 0
    user_array.append(cae_building_coordinator)     # 1
    user_array.append(cae_admin_ga)                 # 2
    user_array.append(cae_programmer_ga)            # 3
    user_array.append(cae_admin)                    # 4
    user_array.append(cae_programmer)               # 5
    user_array.append(cae_attendant)                # 6
    return user_array


def create_wmu_users(style, model_count):
    """
    Create WMU User models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/wmu_users')

    # Set associated profile data for fixtures.
    # (This is generated automatically. We can't really fixture this.
    cae_center_number = PhoneNumber.from_string('+12692763283')
    cae_center_profile = models.Profile.get_profile('ceas_cae')
    cae_center_profile.phone_number = cae_center_number
    cae_center_profile.save()

    # Create random data generator.
    faker_factory = Faker()
    faker_factory.add_provider(E164Provider)

    # Count number of models already created.
    pre_initialized_count = len(models.WmuUser.objects.all())

    # Get all related models.
    majors = models.Major.objects.all()
    addresses = models.Address.objects.all()

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of bronco_net and unique requirement.
        while try_create_model:
            # Generate bronco net.
            bronco_net = '{0}{1}{2}{3}'.format(
                chr(randint(97, 122)),
                chr(randint(97, 122)),
                chr(randint(97, 122)),
                randint(1000, 9999)
            )

            # Generate win number.
            winno = '{0}{1}'.format(randint(1000, 9999), randint(10000, 99999))

            # Generate user type.
            user_type = randint(0, (len(models.WmuUser.USER_TYPE_CHOICES) - 1))

            # Get address.
            index = randint(0, len(addresses) - 1)
            address = addresses[index]

            # Generate phone number.
            phone_number = faker_factory.safe_e164(region_code="US")

            # Determine if active. 70% change of being true.
            if randint(0, 9) < 7:
                active = True
            else:
                active = False

            # Attempt to create model seed.
            try:
                with transaction.atomic():
                    wmu_user = models.WmuUser.objects.create(
                        bronco_net=bronco_net,
                        winno=winno,
                        first_name=faker_factory.first_name(),
                        last_name=faker_factory.last_name(),
                        user_type=user_type,
                        active=active,
                    )

                    # Add between one and three majors to student.
                    major_count = randint(1, 3)
                    for x in range(major_count):
                        # Get Major.
                        index = randint(0, len(majors) - 1)
                        major = majors[index]
                        models.WmuUserMajorRelationship.objects.create(
                            wmu_user=wmu_user,
                            major=major,
                            active=active,
                        )
                    user_profile = models.Profile.get_profile(bronco_net)
                    user_profile.address = address
                    user_profile.phone_number = phone_number
                    user_profile.save()

                    try_create_model = False
            except (ValidationError, IntegrityError):
                # Seed generation failed. Nothing can be done about this without removing the random generation aspect.
                # If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    total_fail_count += 1

    # Output if model instances failed to generate.
    if total_fail_count > 0:
        # Handle for all models failing to seed.
        if total_fail_count == model_count:
            raise ValidationError('Failed to generate any Wmu User seed instances.')

        if total_fail_count >= (model_count / 2):
            # Handle for a majority of models failing to seed (at least half).
            stdout.write(style.ERROR(
                'Failed to generate {0}/{1} Wmu User seed instances.\n'.format(total_fail_count, model_count)
            ))
        else:
            # Handle for some models failing to seed (less than half, more than 0).
            stdout.write(style.WARNING(
                'Failed to generate {0}/{1} Wmu User seed instances.\n'.format(total_fail_count, model_count)
            ))


    stdout.write('Populated ' + style.SQL_FIELD('Wmu User') + ' models.\n')


def create_addresses(style, model_count):
    """
    Creates address models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Address.objects.all())

    # Generate models equal to model count.
    total_fail_count = 0
    for index in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of address info and unique requirement.
        while try_create_model:
            # Generate address info.
            street = faker_factory.building_number() + ' ' + faker_factory.street_address()
            city = faker_factory.city()
            state = randint(0, 49)
            zip = faker_factory.postalcode()
            if faker_factory.boolean():
                optional_street = faker_factory.secondary_address()
            else:
                optional_street = None

            # Attempt to create model seed.
            try:
                models.Address.objects.create(
                    street=street,
                    optional_street=optional_street,
                    city=city,
                    state=state,
                    zip=zip
                )
                try_create_model = False
            except (ValidationError, IntegrityError):
                # Seed generation failed. Nothing can be done about this without removing the random generation aspect.
                # If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    total_fail_count += 1

    # Output if model instances failed to generate.
    if total_fail_count > 0:
        # Handle for all models failing to seed.
        if total_fail_count == model_count:
            raise ValidationError('Failed to generate any Address seed instances.')

        if total_fail_count >= (model_count / 2):
            # Handle for a majority of models failing to seed (at least half).
            stdout.write(style.ERROR(
                'Failed to generate {0}/{1} Address seed instances.\n'.format(total_fail_count, model_count)
            ))
        else:
            # Handle for some models failing to seed (less than half, more than 0).
            stdout.write(style.WARNING(
                'Failed to generate {0}/{1} Address seed instances.\n'.format(total_fail_count, model_count)
            ))

    stdout.write('Populated ' + style.SQL_FIELD('Address') + ' models.\n')
