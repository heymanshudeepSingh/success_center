"""
Command that creates Student Models. from a passed list of bronconet id's.
These models do not have associated Uer models created.
"""

# System Imports.
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# User Class Imports.
from cae_home.models import WmuUser
from settings.ldap_backends import wmu_auth
from settings import extra_settings


logger = extra_settings.logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates student models from a list of bronconet id\'s or winno\'s.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'file_name',
            type=str,
            nargs='?',
            default='student_list.txt',
            help='File to attempt to read for list of student values. Defaults to "student_list.txt".',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Check if in development or production mode.
        if settings.DEBUG:
            # Development. Continue on, this is fine.
            self.create_students(*args, **kwargs)
        else:
            # Production. User probably doesn't want this. Show warning first.
            self.stdout.write(self.style.WARNING('\nWARNING: Attempting to create students when in production mode.'))
            user_input = input('Are you sure you wish to continue? ' + self.style.MIGRATE_HEADING('[ Yes | No ]\n'))

            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                self.create_students(*args, **kwargs)
            else:
                self.stdout.write('')
                self.stdout.write('Seeding cancelled. Exiting.')

    def create_students(self, *args, **kwargs):
        """
        Creates model seeds.
        """
        self.stdout.write(self.style.HTTP_INFO('\nCreate Student command has been called.'))

        # Initialize LDAP backend connector.
        wmu_ldap = wmu_auth.WmuAuthBackend()

        # Open file.
        file_name = kwargs['file_name']
        self.stdout.write(self.style.HTTP_INFO('Attempting to read file "{0}"...'.format(file_name)))
        file = open(file_name)

        # Process each user (should be one bronco_net/winno per line).
        for line in file:
            orig_id = line

            # Validate that line is uid. Must be a string comprised of only letters or numbers.
            if not isinstance(orig_id, str):
                raise ValidationError('Each line should be a string of a single user\'s bronconet or winno.')
            elif orig_id.strip() == '':
                pass    # Empty line. Skip processing.
            elif not re.match(r'[a-zA-Z0-9]+$', orig_id):
                raise ValidationError('Bronconet/winno must be comprised of only standard numbers or letters.')
            else:
                uid = orig_id.strip().lower()

                # Attempt to get user model from Django. Only proceed if does not already exist.
                try:
                    WmuUser.objects.get(winno='{0}'.format(uid))

                    self.stdout.write('WmuUser {0} already exists. Skipping Ldap import.\n\n'.format(uid))
                except WmuUser.DoesNotExist:
                    self.stdout.write('WmuUser {0} does not exist. Importing from Ldap.'.format(uid))

                    # Attempt to get bronconet value. If fails, then assume the passed uid is a bronconet instead.
                    bronco_attempt = wmu_ldap.get_bronconet_from_winno(uid)
                    if bronco_attempt is not None:
                        winno = uid
                        uid = bronco_attempt
                    else:
                        winno = None

                    # Set user info from main campus LDAP.
                    self.stdout.write(
                        self.style.HTTP_INFO('Importing main campus user info for user {0}...'.format(uid))
                    )

                    # Set related WMU User model info.
                    try:
                        wmu_ldap.update_or_create_wmu_user_model(uid, winno)
                    except ValidationError:
                        error_file = open('student_import_error_list.txt', 'a')
                        error_file.write('Student ID: {0}\n'.format(orig_id))
                        error_file.close()

                    self.stdout.write(self.style.HTTP_INFO('Main campus import complete. Starting next user...\n'))

        # Close file.
        file.close()
        self.stdout.write(self.style.HTTP_INFO('\nUser creation complete.'))
