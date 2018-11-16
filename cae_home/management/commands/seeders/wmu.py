"""
Seeder for "WMU" related Core Models.
"""

from django.core.management import call_command
from django.utils import timezone
from faker import Faker
from random import randint

from cae_home import models


def generate_model_seeds(model_count):
    """
    Calls individual seeder methods.
    """
    print('SEEDING WMU Model Group.')
    create_room_types()
    create_departments()
    create_rooms(model_count)
    create_majors()
    create_semester_dates()
    create_wmu_users(model_count)


def create_room_types():
    """
    Create Room Type models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/room_types')

    print('Populated room type models.')

def create_departments():
    """
    Create Department models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/departments')

    print('Populated department models.')

def create_rooms(model_count):
    """
    Create Room models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Room.objects.all())

    # Get all related models.
    room_types = models.RoomType.objects.all()
    departments = models.Department.objects.all()

    # Generate models equal to model count.
    for i in range(model_count - pre_initialized_count):
        # Get Room Type.
        index = randint(0, len(room_types) - 1)
        room_type = room_types[index]

        # Get Department.
        index = randint(0, len(departments) - 1)
        department = departments[index]

        # Generate room name.
        name = '{0}-{1}'.format(chr(randint(65, 90)), randint(100, 299))

        models.Room.objects.create(
            name=name,
            capacity=randint(15, 200),
            room_type=room_type,
            department=department,
        )
    print('Populated room models.')


def create_majors():
    """
    Create Major models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/majors')

    print('Populated major models.')


def create_semester_dates():
    """
    Create Semester Date models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/semester_dates')

    print('Populated semester date models.')


def create_wmu_users(model_count):
    """
    Create WMU User models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.WmuUser.objects.all())

    # Get all related models.
    departments = models.Department.objects.all()
    majors = models.Major.objects.all()
    phone_numbers = models.PhoneNumber.objects.all()

    # Generate models equal to model count.
    for i in range(model_count - pre_initialized_count):
        # Get Department.
        index = randint(0, len(departments) - 1)
        department = departments[index]

        # Get Major.
        index = randint(0, len(majors) - 1)
        major = majors[index]

        # Get Phone Number.
        index = randint(0, len(phone_numbers) - 1)
        phone_number = phone_numbers[index]

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

        models.WmuUser.objects.create(
            department=department,
            major=major,
            phone_number=phone_number,
            bronco_net=bronco_net,
            winno=winno,
            first_name=faker_factory.first_name(),
            last_name=faker_factory.last_name(),
            user_type=user_type,
            active=active,

        )
    print('Populated wmu user models.')
