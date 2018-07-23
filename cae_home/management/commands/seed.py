"""
Seeder command that initializes user models.
"""

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
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
        Group.objects.create(name='CAE Attendant')
        Group.objects.create(name='CAE Admin')
        Group.objects.create(name='CAE Programmer')

        # Set programmer permissions. Want all, unconditionally.
        programmer_group = Group.objects.get(name='CAE Programmer')
        programmer_group.permissions.set(Permission.objects.all())

        # Set admin permissions. Want only the ones related to this app.
        admin_group = Group.objects.get(name='CAE Admin')
        app_permissions = self.get_app_specific_permissions()
        admin_group.permissions.set(app_permissions)

        # Set attendant permissions. Want only add privileges, minus user account adding.
        attendant_group = Group.objects.get(name='CAE Attendant')
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
        models.User.objects.create_superuser('brodriguez8774', '', 'temppass2')
        models.User.objects.create_superuser('skd6970', '', 'temppass2')
        models.User.objects.create_superuser('jbn6294', '', 'temppass2')
        print('Populated user models.')

    def create_addresses(self, model_count):
        """
        Creates address models.
        """
        faker_factory = Faker()

        for index in range(model_count):
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
        # Generate random data.
        faker_factory = Faker()

        for i in range(model_count):
            phone_number = faker_factory.msisdn()
            models.PhoneNumber.objects.create(phone_number=phone_number)

        print('Populated phone number models.')

    #endregion User Model Seeding


    #region WMU Model Seeding

    def create_room_types(self):
        """
        Create Room Type models.
        """
        models.RoomType.objects.create(name="Classroom")
        models.RoomType.objects.create(name="Computer Classroom")
        models.RoomType.objects.create(name="Breakout Room")
        models.RoomType.objects.create(name="Special Room")
        print('Populated room type models.')

    def create_departments(self, model_count):
        """
        Create Department models.
        """
        # Generate random data.
        faker_factory = Faker()

        for i in range(model_count):
            models.Department.objects.create(name=faker_factory.job())
        print('Populated department models.')

    def create_rooms(self, model_count):
        """
        Create Room models.
        """
        # Generate random data.
        faker_factory = Faker()

        room_types = models.RoomType.objects.all()
        departments = models.Department.objects.all()

        for i in range(model_count):
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

    #endregion WMU Model Seeding


    #region CAE Model Seeding

    def create_assets(self, model_count):
        """
        Create Asset models.
        """
        # Generate random data.
        faker_factory = Faker()

        rooms = models.Room.objects.all()

        for i in range(model_count):
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
