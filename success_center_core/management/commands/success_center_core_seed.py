"""
Seeder command that initializes Success Center Timesheets app models.
"""

# User Class Imports.
from cae_home.management.utils import ExpandedCommand
from . import success_center_core_loadfixtures

core_fixtures = success_center_core_loadfixtures.Command()


class Command(ExpandedCommand):
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
        core_fixtures.handle(args, kwargs)
