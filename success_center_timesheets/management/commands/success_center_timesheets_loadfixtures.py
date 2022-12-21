"""
Fixture loader command that initializes Success Center Timesheets app models.
"""

# System Imports.

# User Class Imports.
from cae_home.management.utils import ExpandedCommand
from apps.Success_Center.success_center_timesheets.views import populate_pay_periods


class Command(ExpandedCommand):
    help = 'Seed database models with fixture data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('Success_Center_Timesheets: Load Fixture command has been called.'))

        self.create_pay_periods(display_output=True)
        self.create_shifts(display_output=True)

        self.stdout.write(self.style.HTTP_INFO('Success_Center_Timesheets: Fixture Loading complete.\n'))

    def create_pay_periods(self, display_output=False):
        """
        Create Pay Period models.
        Uses "auto population" method in views. Should create from 5-25-2015 up to a pay period after current date.
        """
        populate_pay_periods()

        if display_output:
            self.display_fixture_output('Pay Period')

    def create_shifts(self, display_output=False):
        """
        Imports fixtures for Shift models.
        """
        # Nothing here yet.
        pass
