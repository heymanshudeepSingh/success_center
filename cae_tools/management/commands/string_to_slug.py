"""
Seeder command that initializes project models.

Also attempts to hook into SubProjects within "apps" folder and seed those as well.
"""

# System Imports.
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# User  Imports.


class Command(BaseCommand):
    help = 'Convert provided string to slug format.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'passed_string',
            type=str,
            help='String to convert.',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Get user input.
        passed_string = kwargs['passed_string']

        # Convert to string and return.
        return slugify(passed_string)
