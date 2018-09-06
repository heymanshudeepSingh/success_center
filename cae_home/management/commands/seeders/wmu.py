"""
Seeder for "WMU" related Core Models.
"""

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
    create_departments(model_count)
    create_rooms(model_count)
    create_majors()
    create_semester_dates()
    create_wmu_users(model_count)


def create_room_types():
    """
    Create Room Type models.
    """
    models.RoomType.objects.get_or_create(name="Classroom")
    models.RoomType.objects.get_or_create(name="Computer Classroom")
    models.RoomType.objects.get_or_create(name="Breakout Room")
    models.RoomType.objects.get_or_create(name="Special Room")

    print('Populated room type models.')

def create_departments(model_count):
    """
    Create Department models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Department.objects.all())

    # Generate models equal to model count.
    for i in range(model_count - pre_initialized_count):
        models.Department.objects.create(name=faker_factory.job())

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
    # Create random data generator.
    faker_factory = Faker()

    models.Major.objects.get_or_create(code='UND', name='Undecided')
    models.Major.objects.get_or_create(code='UNK', name='Unknown (New or Prospective Student)')
    models.Major.objects.get_or_create(code='AERJ', name='Aeronautical Engineering')
    models.Major.objects.get_or_create(code='CEGJ', name='Computer Engineering')
    models.Major.objects.get_or_create(code='CENJ', name='Construction Engineering')
    models.Major.objects.get_or_create(code='CHGJ', name='Chemical Engineering')
    models.Major.objects.get_or_create(code='CIVJ', name='Civil Engineering')
    models.Major.objects.get_or_create(code='CSGJ', name='Computer Science - General')
    models.Major.objects.get_or_create(code='CSTJ', name='Computer Science Theory and Analysis')
    models.Major.objects.get_or_create(code='EDTJ', name='Engineering Design Technology')
    models.Major.objects.get_or_create(code='EENJ', name='Electrical Engineering')
    models.Major.objects.get_or_create(code='IDNJ', name='Industrial Design')
    models.Major.objects.get_or_create(code='IENJ', name='Industrial Engineering')
    models.Major.objects.get_or_create(code='IMGJ', name='Imaging/Graphic and Printing Science')
    models.Major.objects.get_or_create(code='MEGJ', name='Mechanical Engineering')
    models.Major.objects.get_or_create(code='MFNJ', name='Manufacturing Engineering')
    models.Major.objects.get_or_create(code='PENJ', name='Paper Engineering')
    models.Major.objects.get_or_create(code='PREJ', name='Pre-Engineering Undecided')
    models.Major.objects.get_or_create(code='PSCJ', name='Paper Science')
    models.Major.objects.get_or_create(code='UEMJ', name='Engineering Management Technology')

    print('Populated major models.')


def create_semester_dates():
    """
    Create Semester Date models.
    """
    # Create random data generator.
    faker_factory = Faker()

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2013, 1, 7), end_date=timezone.datetime(2013, 4, 27))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2013, 5, 6), end_date=timezone.datetime(2013, 6, 26))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2013, 6, 27), end_date=timezone.datetime(2013, 8, 16))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2013, 9, 3), end_date=timezone.datetime(2013, 12, 14))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2014, 1, 6), end_date=timezone.datetime(2014, 4, 26))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2014, 5, 5), end_date=timezone.datetime(2014, 6, 25))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2014, 6, 26), end_date=timezone.datetime(2014, 8, 15))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2014, 9, 2), end_date=timezone.datetime(2014, 12, 13))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2015, 1, 1), end_date=timezone.datetime(2015, 4, 30))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2015, 5, 11), end_date=timezone.datetime(2015, 7, 1))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2015, 7, 6), end_date=timezone.datetime(2015, 8, 21))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2015, 9, 8), end_date=timezone.datetime(2015, 12, 19))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2016, 1, 11), end_date=timezone.datetime(2016, 4, 30))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2016, 5, 9), end_date=timezone.datetime(2016, 6, 29))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2016, 6, 30), end_date=timezone.datetime(2016, 8, 19))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2016, 9, 6), end_date=timezone.datetime(2016, 12, 17))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2017, 1, 9), end_date=timezone.datetime(2017, 4, 29))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2017, 5, 8), end_date=timezone.datetime(2017, 6, 28))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2017, 6, 29), end_date=timezone.datetime(2017, 8, 18))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2017, 9, 5), end_date=timezone.datetime(2017, 12, 16))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2018, 1, 8), end_date=timezone.datetime(2018, 4, 28))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2018, 5, 7), end_date=timezone.datetime(2018, 6, 27))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2018, 6, 28), end_date=timezone.datetime(2018, 8, 17))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2018, 8, 29), end_date=timezone.datetime(2018, 12, 15))

    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2019, 1, 7), end_date=timezone.datetime(2019, 4, 27))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2019, 5, 6), end_date=timezone.datetime(2019, 6, 26))
    models.SemesterDate.objects.get_or_create(start_date=timezone.datetime(2019, 6, 27), end_date=timezone.datetime(2019, 8, 16))

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
