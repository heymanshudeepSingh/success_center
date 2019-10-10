"""
Command that creates User models from a passed list of bronconet id's.
For security, these users always default to inactive, and must be manually activated.

For User model creation that is dynamically set to active or inactive (based on LDAP), please use Django's standard
website login logic.
"""

# System Imports.
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# User Class Imports.
from cae_home.models import User
from settings.ldap_backends import wmu_auth
from settings import extra_settings


logger = extra_settings.logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates user models from a list of bronconet id\'s.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'file_name',
            type=str,
            nargs='?',
            default='user_list.txt',
            help='File to attempt to read for list of bronco nets. Defaults to "user_list.txt".',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Check if in development or production mode.
        if settings.DEBUG:
            # Development. Continue on, this is fine.
            self.create_users(*args, **kwargs)
        else:
            # Production. User probably doesn't want this. Show warning first.
            self.stdout.write(self.style.WARNING('\nWARNING: Attempting to create users when in production mode.'))
            user_input = input('Are you sure you wish to continue? ' + self.style.MIGRATE_HEADING('[ Yes | No ]\n'))

            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                self.create_users(*args, **kwargs)
            else:
                self.stdout.write('')
                self.stdout.write('Seeding cancelled. Exiting.')

    def create_users(self, *args, **kwargs):
        """
        Creates model seeds.
        """
        self.stdout.write(self.style.HTTP_INFO('\nCreate User command has been called.'))

        # Initialize LDAP backend connectors.
        cae_ldap = wmu_auth.CaeAuthBackend()
        wmu_ldap = wmu_auth.WmuAuthBackend()

        # Open file.
        file_name = kwargs['file_name']
        self.stdout.write(self.style.HTTP_INFO('Attempting to read file "{0}"...'.format(file_name)))
        file = open(file_name)

        # Process each user (should be one bronco_net per line).
        for line in file:
            uid = line

            # Validate that line is uid. Must be a string comprised of only letters or numbers.
            if not isinstance(uid, str):
                raise ValidationError('Each line should be a string of a single user\'s bronconet.')
            elif uid.strip() == '':
                pass    # Empty line. Skip processing.
            elif not re.match(r'[a-zA-Z0-9]+$', uid):
                raise ValidationError('Bronconet must be comprised of only standard numbers or letters.')
            else:
                uid = uid.strip().lower()

                # Attempt to get user model from Django. Only proceed if does not already exist.
                try:
                    User.objects.get(username='{0}'.format(uid))

                    self.stdout.write('User {0} already exists. Skipping Ldap import.\n\n'.format(uid))

                except User.DoesNotExist:
                    self.stdout.write('User {0} does not exist. Importing from Ldap.'.format(uid))

                    # First create user with the "dummy password". Defaults to inactive to prevent security holes.
                    login_user = get_user_model().get_or_create_user(
                        uid,
                        '{0}@wmich.edu'.format(uid),
                        'temppass2',
                        inactive=True,
                    )

                    # Get CAE Center name info as a backup, in case fields are missing in Main Campus Ldap.
                    ldap_user_info = cae_ldap.get_ldap_user_info(uid, attributes=['uid', 'givenName', 'sn', ])
                    if ldap_user_info is not None:
                        login_user.first_name = ldap_user_info['givenName'][0].strip()
                        login_user.last_name = ldap_user_info['sn'][0].strip()
                    else:
                        print('User is not in CAE LDAP.')
                    login_user.save()
                    self.stdout.write(self.style.HTTP_INFO('Created user "{0}".'.format(uid.strip())))

                    # Check if user is part of any CAE Center groups.
                    self.stdout.write(self.style.HTTP_INFO('Checking for membership of CAE Center groups...'))
                    user_cae_groups = cae_ldap.get_ldap_user_groups(uid)

                    if user_cae_groups['director']:
                        login_user.groups.add(Group.objects.get(name='CAE Director'))
                        self.stdout.write(self.style.HTTP_INFO('Set director group.'))
                    if user_cae_groups['attendant']:
                        login_user.groups.add(Group.objects.get(name='CAE Attendant'))
                        self.stdout.write(self.style.HTTP_INFO('Set attendant group.'))
                    if user_cae_groups['admin']:
                        login_user.groups.add(Group.objects.get(name='CAE Admin'))
                        self.stdout.write(self.style.HTTP_INFO('Set admin group.'))
                    if user_cae_groups['programmer']:
                        login_user.groups.add(Group.objects.get(name='CAE Programmer'))
                        login_user.is_staff = True
                        self.stdout.write(self.style.HTTP_INFO('Set programmer group.'))

                    login_user.save()
                    self.stdout.write(self.style.HTTP_INFO('CAE Center group membership set.'))

                    # Set user info from main campus LDAP.
                    self.stdout.write(self.style.HTTP_INFO('Importing main campus user info...'))

                    # Set related WMU User model info.
                    wmu_ldap.create_or_update_wmu_user_model(uid, skip_update=True)

                    self.stdout.write(self.style.HTTP_INFO('Main campus import complete. Starting next user...\n'))

        # Close file.
        file.close()
        self.stdout.write(self.style.HTTP_INFO('\nUser creation complete.'))
