"""
Seeder command that initializes user models.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from faker import Faker

from cae_home import models


class Command(BaseCommand):
    help = 'Seed database models with randomized data.'

    def handle(self, *args, **kwargs):
        print('Seed command has been called.')
        self.create_groups()
        self.create_users()
        self.create_addresses()
        self.create_phone_numbers()

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

        # Set attendant permissions. Want only add privileges.
        attendant_group = Group.objects.get(name='CAE Attendant')
        filtered_permissions = []
        for permission in app_permissions:
            if 'Can add' in permission.name:
                filtered_permissions.append(permission)
        attendant_group.permissions.set(filtered_permissions)

        print('Populated group models.')

    def get_app_specific_permissions(self):
        """
        Finds all permission models specific to the current app.
        :return: A list of all permission models for current app.
        """
        # First find all content types with the app's name.
        app_content_types = ContentType.objects.filter(app_label__contains='cae_home')

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

    def create_addresses(self):
        """
        Creates address models.
        """
        faker_factory = Faker()

        for index in range(100):
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

    def create_phone_numbers(self):
        """
        Creates phone number models.
        """
        # Generate random data.
        faker_factory = Faker()

        for i in range(100):
            phone_number = faker_factory.msisdn()
            models.PhoneNumber.objects.create(phone_number=phone_number)

        print('Populated phone number models.')
