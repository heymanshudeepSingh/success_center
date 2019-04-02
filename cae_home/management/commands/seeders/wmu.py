"""
Seeder for "WMU" related Core Models.
"""

from django.core.exceptions import ValidationError
from django.core.management import call_command
from faker import Faker
from random import randint
from sys import stdout

from cae_home import models


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING WMU Model Group.\n'))
    create_room_types(style)
    create_departments(style)
    create_rooms(style)
    create_majors(style)
    create_semester_dates(style)
    create_wmu_users(style, model_count)


def create_room_types(style):
    """
    Create Room Type models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/room_types')

    stdout.write('Populated ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style):
    """
    Create Department models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/departments')

    stdout.write('Populated ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style):
    """
    Create Room models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/rooms')

    stdout.write('Populated ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style):
    """
    Create Major models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/majors')

    stdout.write('Populated ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semester_dates(style):
    """
    Create Semester Date models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/semester_dates')

    stdout.write('Populated ' + style.SQL_FIELD('Semester Date') + ' models.\n')


def create_wmu_users(style, model_count):
    """
    Create WMU User models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/wmu_users')

    # Set associated profile data for fixtures.
    # (This is generated automatically. We can't really fixture this.
    cae_center_number = models.PhoneNumber.objects.get(phone_number='2692763283')
    cae_center_profile = models.Profile.get_profile('ceas_cae')
    cae_center_profile.phone_number = cae_center_number
    cae_center_profile.save()

    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.WmuUser.objects.all())

    # Get all related models.
    departments = models.Department.objects.all()
    majors = models.Major.objects.all()

    # Generate models equal to model count.
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of bronco_net and unique requirement.
        while try_create_model:
            # Get Department.
            index = randint(0, len(departments) - 1)
            department = departments[index]

            # Get Major.
            index = randint(0, len(majors) - 1)
            major = majors[index]

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

            # Determine if active. 70% change of being true.
            if randint(0, 9) < 7:
                active = True
            else:
                active = False

            # Attempt to create model seed.
            try:
                models.WmuUser.objects.create(
                    department=department,
                    major=major,
                    bronco_net=bronco_net,
                    winno=winno,
                    first_name=faker_factory.first_name(),
                    last_name=faker_factory.last_name(),
                    user_type=user_type,
                    active=active,
                )
                try_create_model = False
            except ValidationError:
                # Seed generation failed. Nothing can be done about this without removing the random generation aspect.
                # If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    stdout.write('Failed to generate wmu user seed instance.')

    stdout.write('Populated ' + style.SQL_FIELD('Wmu User') + ' models.\n')
