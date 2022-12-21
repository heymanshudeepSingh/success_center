"""
Fixture loader command that initializes GradApps app models.
"""

# System Imports.
from django.core.management import call_command

# User Class Imports.
from cae_home.management.utils import ExpandedCommand


class Command(ExpandedCommand):
    help = 'Seed database models with fixture data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('SUCCESS_CENTER: Load Fixtures command has been called.'))

        call_command('loaddata', 'production_models/locations')

        self.stdout.write(self.style.HTTP_INFO('SUCCESS_CENTER: Fixture loading complete.\n'))
