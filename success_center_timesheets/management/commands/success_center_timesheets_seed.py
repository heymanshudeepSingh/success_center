"""
Seeder command that initializes Success Center Timesheets app models.
"""

# System Imports.
import random

import pytz
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from faker import Faker
from random import randint

# User Class Imports.
from cae_home.management.utils import ExpandedCommand
from apps.Success_Center.success_center_timesheets import models
from apps.Success_Center.success_center_timesheets.views import populate_pay_periods
from . import success_center_timesheets_loadfixtures

timesheets_fixtures = success_center_timesheets_loadfixtures.Command()


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
        model_count = kwargs['model_count']
        if model_count < 1:
            model_count = 100

        self.stdout.write(self.style.HTTP_INFO('Success_center_timesheets: Seed command has been called.'))

        self.create_pay_periods()
        self.create_timesheets(model_count)

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_SHIFTS: Seeding complete.\n'))

    def create_pay_periods(self):
        """
        Create Pay Period models.
        Uses "auto population" method in views. Should create from 5-25-2015 up to a pay period after current date.
        """
        populate_pay_periods()
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Pay Period') + ' models.')

    def create_timesheets(self, model_count):
        """
        Create Employee Shift models.
        """
        # Load preset fixtures.
        timesheets_fixtures.create_shifts()

        # Create random data generator.
        faker_factory = Faker()

        # initialize local time zone
        local_timezone = pytz.timezone('America/Detroit')

        # Count number of models already created.
        pre_initialized_count = len(models.TimesheetShift.objects.all())

        # Get all related models.
        date_holder = timezone.localdate()
        # complex_query = (
        #     (
        #         Q(groups__name='STEP Employee') | Q(groups__name='STEP Admin')
        #     )
        #     & Q(is_active=True)
        # )
        users = get_user_model().objects.filter(groups__name='STEP Employee')
        pay_periods = models.PayPeriod.objects.filter(date_start__lte=date_holder)[:model_count / 20]
        if len(pay_periods) < 3:
            pay_periods = models.PayPeriod.objects.filter(date_start__lte=date_holder)[:3]

        # Generate models equal to model count.
        total_fail_count = 0
        for i in range(model_count - pre_initialized_count):
            fail_count = 0
            try_create_model = True

            # Loop attempt until 3 fails or model is created.
            # Model creation may fail due to randomness of shift values and overlapping shifts per user being invalid.
            while try_create_model:
                # Get User.
                index = randint(0, len(users) - 1)
                user = users[index]

                # Get pay period.
                index = randint(0, len(pay_periods) - 1)
                pay_period = pay_periods[index]

                # Calculate clock in/clock out times.
                clock_in = pay_period.get_start_as_datetime() + timezone.timedelta(
                    days=randint(0, 13),
                    hours=randint(7, 20),
                    # minutes=random.choice([0, 30]),
                    minutes=0,
                    seconds=0
                )
                clock_in_hours = int(clock_in.hour)
                clock_out = clock_in + timezone.timedelta(hours=1, minutes=0)
                if clock_in_hours <= 11:
                    clock_out = clock_in + timezone.timedelta(hours=randint(1, (12 - clock_in_hours)), minutes=0)
                elif clock_in_hours <= 16:
                    clock_out = clock_in + timezone.timedelta(hours=randint(1, (17 - clock_in_hours)), minutes=0)
                elif clock_in_hours <= 23:
                    clock_out = clock_in + timezone.timedelta(hours=randint(1, (24 - clock_in_hours)), minutes=0)

                # If random clock_out time happened to go past pay period, then set to period end.
                if clock_out > pay_period.get_end_as_datetime():
                    clock_out = pay_period.get_end_as_datetime()

                try:
                    if len(models.TimesheetShift.objects.filter(employee=user, clock_in__gte=clock_in, clock_out__lte=clock_out)) > 1:
                        pass
                    else:
                        shifts = models.TimesheetShift.objects.get(employee=user, clock_in__gte=clock_in, clock_out__lte=clock_out)
                except models.TimesheetShift.DoesNotExist:
                    shifts = None

                if not shifts:
                    # Attempt to create model seed.
                    try:
                        models.TimesheetShift.objects.create(
                            employee=user,
                            pay_period=pay_period,
                            clock_in=clock_in,
                            clock_out=clock_out,
                        )
                        try_create_model = False
                    except (ValidationError, IntegrityError):
                        # Seed generation failed. Nothing can be done about this without removing the random generation
                        # aspect. If we want that, we should use fixtures instead.
                        fail_count += 1

                        # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                        if fail_count > 2:
                            try_create_model = False
                            total_fail_count += 1

        # Output model generation info.
        self.display_seed_output('Timesheet', model_count, total_fail_count)
