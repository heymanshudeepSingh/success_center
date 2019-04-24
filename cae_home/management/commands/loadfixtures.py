"""
Fixture loader command that initializes project models.
Should import relevant calls directly from seeder command.
"""

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from .seeders import user as user_seeder
from .seeders import wmu as wmu_seeder


class Command(BaseCommand):
    help = 'Seed database models with fixtures data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Check if in development or production mode.
        if settings.DEBUG:
            # Development. Continue on, this is fine.
            self.load_fixtures(*args, **kwargs)
        else:
            # Production. User probably doesn't want this. Show warning first.
            self.stdout.write(self.style.WARNING('\nWARNING: Attempting to seed when site is in production mode.'))
            self.stdout.write('Proceeding may overwrite some models (fixtures).')
            user_input = input('Are you sure you wish to continue? ' + self.style.MIGRATE_HEADING('[ Yes | No ]\n'))

            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                self.load_fixtures(*args, **kwargs)
            else:
                self.stdout.write('')
                self.stdout.write('Seeding cancelled. Exiting.')

    def load_fixtures(self, *args, **kwargs):
        """
        Loads model fixtures..
        """
        # Unconditionally seeds models in cae_home app, as that's always installed.
        # Generates in order of "user models", "wmu models", "cae models".
        self.stdout.write(self.style.HTTP_INFO('\nCAE_HOME: Load Fixture command has been called.'))
        user_seeder.create_site_themes(self.style)
        user_seeder.create_groups(self.style)
        wmu_seeder.create_room_types(self.style)
        wmu_seeder.create_departments(self.style)
        wmu_seeder.create_rooms(self.style)
        wmu_seeder.create_majors(self.style)
        wmu_seeder.create_semester_dates(self.style)

        # Attempts to load fixtures for any additional apps it can find.
        self.stdout.write(self.style.HTTP_INFO('CAE_HOME: Fixture loading complete. Attempting to call imported apps.\n'))
        self.call_imported_app_fixtures()

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))

    def call_imported_app_fixtures(self):
        """
        Attempts to locate and call fixture loaders from imported apps.
        On failure to call, simply skips, under the assumption that fixture loader does not exist.

        Called fixture loaders should be in the format of "<app_name>_loadfixtures.py".
        For example, a "super_awesome_app" would have a fixture loader of name of "super_awesome_app_loadfixtures.py".
        """
        for project, project_settings in settings.INSTALLED_CAE_PROJECTS.items():
            for app in project_settings['related_apps']:
                try:
                    command = '{0}_loadfixtures'.format(app)
                    call_command(command)
                except CommandError as err:
                    if str(err) == "Unknown command: {0!r}".format(command):
                        # Could not find seeder in app. Skipping.
                        self.stdout.write(self.style.WARNING("Fixture loader {0!r} not found.".format(command)))
                    else:
                        raise
