"""
Seeder command that initializes project models.
"""

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from .seeders import cae as cae_seeder
from .seeders import user as user_seeder
from .seeders import wmu as wmu_seeder


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
        # Check if in development or production mode.
        if settings.DEBUG:
            # Development. Continue on, this is fine.
            self.create_seeds(*args, **kwargs)
        else:
            # Production. User probably doesn't want this. Show warning first.
            self.stdout.write(self.style.WARNING('\nWARNING: Attempting to seed when site is in production mode.'))
            self.stdout.write('Proceeding may overwrite some models (fixtures) or create garbage data (random seeders).')
            user_input = input('Are you sure you wish to continue? ' + self.style.MIGRATE_HEADING('[ Yes | No ]\n'))

            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                self.create_seeds(*args, **kwargs)
            else:
                self.stdout.write('')
                self.stdout.write('Seeding cancelled. Exiting.')

    def create_seeds(self, *args, **kwargs):
        """
        Creates model seeds.
        """
        model_count = kwargs['model_count']
        if model_count < 1:
            model_count = 100
        self.stdout.write(self.style.HTTP_NOT_MODIFIED(
            'Initializing seeder with {0} randomized models.'.format(model_count)
        ))
        if model_count > 500:
            self.stdout.write(self.style.WARNING(
                'WARNING: Depending on your hardware, seeding with more than 500 models may take a while!'
            ))

        # Unconditionally seeds models in cae_home app, as that's always installed.
        # Generates in order of "user models", "wmu models", "cae models".
        self.stdout.write(self.style.HTTP_INFO('\nCAE_HOME: Seed command has been called.'))
        user_seeder.generate_model_seeds(self.style, model_count)
        wmu_seeder.generate_model_seeds(self.style, model_count)
        cae_seeder.generate_model_seeds(self.style, model_count)

        # Attempts to seed any additional apps it can find.
        self.stdout.write(self.style.HTTP_INFO('CAE_HOME: Seeding complete. Attempting to call imported apps.\n'))
        self.call_imported_app_seeders(model_count)

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))

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
                except CommandError as err:
                    if str(err) == "Unknown command: {0!r}".format(command):
                        # Could not find seeder in app. Skipping.
                        self.stdout.write(self.style.WARNING("Seeder {0!r} not found.".format(command)))
                    else:
                        raise
