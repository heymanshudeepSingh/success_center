"""
Seeder command that initializes user models.
"""

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from faker import Faker
from random import randint

from cae_home import models


class Command(BaseCommand):
    help = 'Seed database models with randomized data.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'model_count',
            type=int,
            nargs='?',
            default=100,
            help='Number of randomized models to create. Defaults to 100. Cannot exceed 10,000.',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        model_count = kwargs['model_count']
        if model_count < 1:
            model_count = 100
        elif model_count > 10000:
            model_count = 100
        print('Initializing seeder with {0} randomized models.\n'.format(model_count))

        print('CAE_HOME: Seed command has been called.')
        print('SEEDING User Model Group.')
        self.create_groups()
        self.create_users()
        self.create_addresses(model_count)
        self.create_phone_numbers(model_count)

        print('SEEDING WMU Model Group.')
        self.create_room_types()
        self.create_departments(model_count)
        self.create_rooms(model_count)
        self.create_majors()
        self.create_semester_dates()
        self.create_wmu_users(model_count)

        print('SEEDING CAE Model Group.')
        self.create_assets(model_count)

        print('CAE_HOME: Seeding complete. Attempting to call imported apps.')
        self.call_imported_app_seeders(model_count)

        print('\nSeeding complete.')


    #region User Model Seeding

    def create_groups(self):
        """
        Creates django "auth_group" models and allocates proper permissions.
        """
        # Create base groups.
        attendant_group = Group.objects.get_or_create(name='CAE Attendant')
        admin_group = Group.objects.get_or_create(name='CAE Admin')
        programmer_group = Group.objects.get_or_create(name='CAE Programmer')

        # Set programmer permissions. Want all, unconditionally.
        programmer_group = programmer_group[0]
        programmer_group.permissions.set(Permission.objects.all())

        # Set admin permissions. Want only the ones related to this app.
        admin_group = admin_group[0]
        app_permissions = self.get_app_specific_permissions()
        admin_group.permissions.set(app_permissions)

        # Set attendant permissions. Want only add privileges, minus user account adding.
        attendant_group = attendant_group[0]
        filtered_permissions = []
        for permission in app_permissions:
            if 'Can add' in permission.name and not 'user' in permission.name:
                filtered_permissions.append(permission)
        attendant_group.permissions.set(filtered_permissions)

        print('Populated group models.')

    def get_app_specific_permissions(self):
        """
        Finds all permission models specific to the current app.
        :return: A list of all permission models for current app.
        """
        # First find all content types with the app's name.
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

        return app_permisson_list

    def create_users(self):
        """
        Creates base user models.
        """
        models.User.get_or_create_superuser('brodriguez8774', '', 'temppass2') # Brandon
        models.User.get_or_create_superuser('ngf9321', '', 'temppass2')    # Nick
        models.User.get_or_create_superuser('skd6970', '', 'temppass2')    # Steven (Senior Design)
        models.User.get_or_create_superuser('jbn6294', '', 'temppass2')    # Josh (Senior Design)

        print('Populated user models.')

    def create_addresses(self, model_count):
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

    def create_phone_numbers(self, model_count):
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

    #endregion User Model Seeding


    #region WMU Model Seeding

    def create_room_types(self):
        """
        Create Room Type models.
        """
        models.RoomType.objects.get_or_create(name="Classroom")
        models.RoomType.objects.get_or_create(name="Computer Classroom")
        models.RoomType.objects.get_or_create(name="Breakout Room")
        models.RoomType.objects.get_or_create(name="Special Room")

        print('Populated room type models.')

    def create_departments(self, model_count):
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

    def create_rooms(self, model_count):
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


    def create_majors(self):
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


    def create_semester_dates(self):
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


    def create_wmu_users(self, model_count):
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

    #endregion WMU Model Seeding


    #region CAE Model Seeding

    def create_assets(self, model_count):
        """
        Create Asset models.
        """
        # Create random data generator.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.Asset.objects.all())

        # Get all related models.
        rooms = models.Room.objects.all()

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            # Get Room.
            index = randint(0, len(rooms) - 1)
            room = rooms[index]

            # Generate Ip address. 50/50 chance of being ipv4 or ipv6
            if randint(0, 1) == 1:
                ip_address = faker_factory.ipv4()
            else:
                ip_address = faker_factory.ipv6()

            models.Asset.objects.create(
                room=room,
                serial_number=faker_factory.isbn13(),
                asset_tag=faker_factory.ean8(),
                brand_name=faker_factory.domain_word(),
                mac_address=faker_factory.mac_address(),
                ip_address=ip_address,
                device_name=faker_factory.last_name(),
                description=faker_factory.sentence(),
            )
        print('Populated asset models.')

    #endregion CAE Model Seeding


    def call_imported_app_seeders(self, model_count):
        """
        Attempts to locate and call seeders from imported apps.
        On failure to call, simply skips, under the assumption that seeder does not exist.

        Called seeders should be in the format of "<app_name>_seed.py".
        For example, a "super_awesome_app" would have a seeder name of "super_awesome_app_seed.py".
        """
        for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
            for app in project_settings['related_apps']:
                try:
                    command = '{0}_seed'.format(app)
                    call_command(command, model_count)
                except CommandError:
                    # Could not find seeder in app. Skipping.
                    pass
