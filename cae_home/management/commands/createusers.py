"""
Command that creates users from a passed list of bronconet id's.
For security, these users always default to inactive, and must be manually activated.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates users from a list of bronconet id\'s.'

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
        file_name = kwargs['file_name']
        self.stdout.write(self.style.HTTP_INFO('Attempting to read file "{0}"...'.format(file_name)))
        file = open(file_name)

        for line in file:
            get_user_model().get_or_create_user(line, '{0}@wmich.edu'.format(line), 'temppass2', inactive=True)
            self.stdout.write(self.style.HTTP_INFO('Created user "{0}"'.format(line.strip())))

        file.close()
        self.stdout.write(self.style.HTTP_INFO('\nUser creation complete.'))

