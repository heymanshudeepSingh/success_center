"""
CAE Home app management Utility Functions and Classes.
"""

# System Imports.
from abc import ABC
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand


class ExpandedCommand(BaseCommand, ABC):
    """
    Expanded "BaseCommand" class with additional helper functions.
    """
    def display_fixture_output(self, model_name):
        """
        Displays output for after fixture finishes importing.
        """
        self.stdout.write('Imported fixtures for ' + self.style.SQL_FIELD('{0}'.format(model_name)) + ' models.\n')

    def display_seed_output(self, model_name, model_count, fail_count):
        """
        Displays output for after seeder finishes generating.
        """
        # Output if model instances failed to generate.
        if fail_count > 0:
            # Handle for all models failing to seed.
            if fail_count == model_count:
                raise ValidationError('Failed to generate any {0} seed instances.'.format(model_name))

            if fail_count >= (model_count / 2):
                # Handle for a majority of models failing to seed (at least half).
                self.stdout.write(self.style.ERROR(
                    'Failed to generate {0}/{1} {2} seed instances.'.format(fail_count, model_count, model_name)
                ))
            else:
                # Handle for some models failing to seed (less than half, more than 0).
                self.stdout.write(self.style.WARNING(
                    'Failed to generate {0}/{1} {2} seed instances.'.format(fail_count, model_count, model_name)
                ))

        self.stdout.write('Populated ' + self.style.SQL_FIELD('{0}'.format(model_name)) + ' models.\n')
