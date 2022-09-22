"""
Command that creates Major Models from a passed list of major codes.
"""

# System Imports.
import logging, re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# User Imports.
from cae_home.models import Major
from workspace.ldap_backends.wmu_auth import adv_backend


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates Majors models from a list of major names.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'file_name',
            type=str,
            nargs='?',
            default='major_list.txt',
            help='File to attempt to read for list of major values. Defaults to "major_list.txt".',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Check if in development or production mode.
        if settings.DEBUG:
            # Development. Continue on, this is fine.
            self.create_majors(*args, **kwargs)
        else:
            # Production. User probably doesn't want this. Show warning first.
            self.stdout.write(self.style.WARNING('\nWARNING: Attempting to create majors when in production mode.'))
            user_input = input('Are you sure you wish to continue? ' + self.style.MIGRATE_HEADING('[ Yes | No ]\n'))

            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                self.create_majors(*args, **kwargs)
            else:
                self.stdout.write('')
                self.stdout.write('Seeding cancelled. Exiting.')

    def create_majors(self, *args, **kwargs):
        """
        Import major model data.
        """
        self.stdout.write(self.style.HTTP_INFO('\nCreate Student command has been called.'))

        # Initialize LDAP backend connector.
        adv_ldap = adv_backend.AdvisingAuthBackend()

        # Open file.
        file_name = kwargs['file_name']
        self.stdout.write(self.style.HTTP_INFO('Attempting to read file "{0}"...'.format(file_name)))
        file = open(file_name)

        # Process each user (should be one bronco_net/winno per line).
        for line in file:
            orig_id = line

            # Validate that line is uid. Must be a string comprised of only letters or numbers.
            if not isinstance(orig_id, str):
                raise ValidationError('Each line should be a string of major code.')
            elif orig_id.strip() == '':
                pass    # Empty line. Skip processing.
            elif not re.match(r'[a-zA-Z0-9]+$', orig_id):
                raise ValidationError('Bronconet/winno must be comprised of only standard numbers or letters.')
            else:
                major_code = orig_id.strip().upper()

                # Attempt to get major model from Django. Only proceed if does not already exist.
                try:
                    Major.objects.get(student_code=major_code)

                    self.stdout.write('Major {0} already exists. Skipping Ldap import.\n\n'.format(major_code))
                except Major.DoesNotExist:
                    self.stdout.write('Major {0} does not exist. Importing from Ldap.'.format(major_code))

                    # Import by code, aka "StudentCode" according to most of our internal logic.
                    # Aka wmuStudentMajor according to main campus.
                    adv_ldap.import_major_model(major_code)
