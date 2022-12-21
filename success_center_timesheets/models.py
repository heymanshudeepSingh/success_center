"""
Models for SuccessCenterTimesheets app.
"""
# System Imports.
import datetime, math, pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ObjectDoesNotExist
from django.utils import timezone

# User Imports.
from cae_home import models as cae_home_models


class PayPeriod(models.Model):
    """
    An instance of a two week pay period.

    See CaeWeb EmployeeShift models for similar logic.
    """
    # Model fields.
    date_start = models.DateField(unique=True)
    date_end = models.DateField(blank=True, unique=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pay Period'
        verbose_name_plural = 'Pay Periods'
        ordering = ('-date_start',)

    def __str__(self):
        return '{0} - {1}'.format(self.date_start, self.date_end)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        if self.date_end is None:
            end_datetime = self.get_start_as_datetime() + datetime.timedelta(days=13)
            end_date = end_datetime.date()
            self.date_end = end_date

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(PayPeriod, self).save(*args, **kwargs)

    def get_start_as_datetime(self):
        """
        Returns start date at exact midnight, local time.
        """
        midnight = datetime.time(0, 0, 0, 0)
        start_datetime = pytz.timezone('America/Detroit').localize(datetime.datetime.combine(self.date_start, midnight))
        return start_datetime

    def get_end_as_datetime(self):
        """
        Returns end date just before midnight of next day, local time.
        """
        day_end = datetime.time(23, 59, 59)
        end_datetime = pytz.timezone('America/Detroit').localize(datetime.datetime.combine(self.date_end, day_end))
        return end_datetime

    @staticmethod
    def get_payperiod(period_date=None):
        """
        Returns the PayPeriod model that matches the provided date.
        :param period_date: Desired date for PayPeriod. If none is provided, defaults to current date.
        :return: PayPeriod that date falls into.
        """
        # Validate provided date.
        if period_date is None:
            # Handle for None. Defaults to current date.
            period_date = timezone.localdate()

        elif isinstance(period_date, datetime.datetime) or isinstance(period_date, timezone.datetime):
            # Datetime provided. Trim to be just date.
            period_date = period_date.date()

        elif isinstance(period_date, datetime.date):
            # Date provided. This is what we want.
            pass

        else:
            # All other values are invalid.
            raise ValidationError(
                'Expected date value. Instead, got {0} value of {1}.'.format(type(period_date), period_date)
            )

        # Get PayPeriod object that date corresponds to.
        return PayPeriod.objects.get(date_start__lte=period_date, date_end__gte=period_date)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        date_start = datetime.datetime.strptime('2019 01 01', '%Y %m %d')
        date_end = datetime.datetime.strptime('2019 01 14', '%Y %m %d')
        try:
            return PayPeriod.objects.get(
                date_start=date_start,
                date_end=date_end,
            )
        except ObjectDoesNotExist:
            return PayPeriod.objects.create(
                date_start=date_start,
                date_end=date_end,
            )


class TimesheetShift(models.Model):
    """
    An instance of an employee clocking in and out for a shift.

    Due to client request, clock in times are currently limited to preset values.
    But for future-proofing, we save as datetime stamps, to allow expanding/changing of these values in the future,
    if desired.

    See CaeWeb EmployeeShift models for similar logic.
    """
    # Preset field choices.
    INT_NULL_TIME = 0
    INT_6_00_AM = 1
    INT_6_30_AM = 2
    INT_7_00_AM = 3
    INT_7_30_AM = 4
    INT_8_00_AM = 5
    INT_8_30_AM = 6
    INT_9_00_AM = 7
    INT_9_30_AM = 8
    INT_10_00_AM = 9
    INT_10_30_AM = 10
    INT_11_00_AM = 11
    INT_11_30_AM = 12
    INT_12_00_PM = 13
    INT_12_30_PM = 14
    INT_1_00_PM = 15
    INT_1_30_PM = 16
    INT_2_00_PM = 17
    INT_2_30_PM = 18
    INT_3_00_PM = 19
    INT_3_30_PM = 20
    INT_4_00_PM = 21
    INT_4_30_PM = 22
    INT_5_00_PM = 23
    INT_5_30_PM = 24
    INT_6_00_PM = 25
    INT_6_30_PM = 26
    INT_7_00_PM = 27
    INT_7_30_PM = 28
    INT_8_00_PM = 29
    INT_8_30_PM = 30
    INT_9_00_PM = 31
    INT_9_30_PM = 32
    INT_10_00_PM = 33
    INT_10_30_PM = 34
    INT_11_00_PM = 35
    INT_11_30_PM = 36
    INT_12_00_AM = 37
    INT_12_30_AM = 38
    INT_1_00_AM = 39

    # Relationship keys.
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pay_period = models.ForeignKey('PayPeriod', on_delete=models.CASCADE)

    # Model fields.
    clock_in = models.DateTimeField(blank=True, null=True)
    clock_out = models.DateTimeField(blank=True, null=True)
    signature = models.TextField(default='1')

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Timesheet Shift'
        verbose_name_plural = 'Timesheet Shifts'
        # ordering = ('morning_clock_in_1', 'morning_clock_out_1',)
        # unique_together = (
        #     ('employee', 'clock_in',),
        #     ('employee', 'clock_out',),
        # )

    def __str__(self):
        return '{0}: {1} to {2}'.format(self.employee, self.clock_in, self.clock_out)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check that clock_out time is after clock_in time.
        if self.clock_in is not None and self.clock_out is not None:
            if (self.clock_out == self.clock_in) or (self.clock_out < self.clock_in):
                raise ValidationError('Clock out time must be after clock in time.')

        # Check that clock times do not overlap previous shifts for user.
        # Check clock in is not inside other shift.
        if self.clock_in is not None:
            previous_shifts = TimesheetShift.objects.filter(
                employee=self.employee,
                clock_in__lt=self.clock_in,
                clock_out__gt=self.clock_in
            ).exclude(id=self.id)
            if len(previous_shifts) != 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        if self.clock_out is not None:
            # Check clock out is not inside other shift.
            previous_shifts = TimesheetShift.objects.filter(
                employee=self.employee,
                clock_in__lt=self.clock_out,
                clock_out__gt=self.clock_out
            ).exclude(id=self.id)
            if len(previous_shifts) != 0:
                raise ValidationError('Users cannot have overlapping shift times.')

            # Check old shift is not entirely inside new shift.
            previous_shifts = TimesheetShift.objects.filter(
                employee=self.employee,
                clock_in__gt=self.clock_in,
                clock_out__lt=self.clock_out
            ).exclude(id=self.id)
            if len(previous_shifts) != 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        # Check that clock times are inside provided pay period.
        # Check clock in times. Shift just started so there's no data to lose. Raise validation error.

        try:
            if (
                (self.clock_in < self.pay_period.get_start_as_datetime()) or
                (self.clock_in > self.pay_period.get_end_as_datetime())
            ):
                raise ValidationError(
                    'Shift must be between pay period dates. Double check that you\'re using the correct pay period.'
                )
        except TimesheetShift.pay_period.RelatedObjectDoesNotExist:
            # Does not have pay period. Can occur when using add shift form.
            pass
        try:
            if not self.signature:
                raise ValidationError(
                    'Signature is required!'
                )
        except TimesheetShift.signature.RelatedObjectDoesNotExist:
            # Does not have pay period. Can occur when using add shift form.
            pass

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    def get_time_worked_as_hms(self, total_seconds=None):
        """
        Gets hours worked, in h/m/s format.
        :param total_seconds: Total time worked in seconds. Defaults
        :return: Tuple of hours, minutes, and seconds worked.
        """
        # Populate seconds if none was provided.
        if total_seconds is None:
            total_seconds = self.clock_out - self.clock_in

        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60
        hours = math.trunc(total_hours)
        minutes = math.trunc(total_minutes - (hours * 60))
        seconds = math.trunc(total_seconds - (minutes * 60) - (hours * 60 * 60))

        return (hours, minutes, seconds)

    @staticmethod
    def get_preset_time_str_from_int(time_int):
        """
        Converts a given time string to the corresponding preset integer.
        :param time_int: Time integer to convert.
        :return: Corresponding str for integer.
        """
        if time_int == TimesheetShift.INT_NULL_TIME:
            return '-'
        elif time_int == TimesheetShift.INT_6_00_AM:
            return '6:00 am'
        elif time_int == TimesheetShift.INT_6_30_AM:
            return '6:30 am'
        elif time_int == TimesheetShift.INT_7_00_AM:
            return '7:00 am'
        elif time_int == TimesheetShift.INT_7_30_AM:
            return '7:30 am'
        elif time_int == TimesheetShift.INT_8_00_AM:
            return '8:00 am'
        elif time_int == TimesheetShift.INT_8_30_AM:
            return '8:30 am'
        elif time_int == TimesheetShift.INT_9_00_AM:
            return '9:00 am'
        elif time_int == TimesheetShift.INT_9_30_AM:
            return '9:30 am'
        elif time_int == TimesheetShift.INT_10_00_AM:
            return '10:00 am'
        elif time_int == TimesheetShift.INT_10_30_AM:
            return '10:30 am'
        elif time_int == TimesheetShift.INT_11_00_AM:
            return '11:00 am'
        elif time_int == TimesheetShift.INT_11_30_AM:
            return '11:30 am'
        elif time_int == TimesheetShift.INT_12_00_PM:
            return '12:00 pm'
        elif time_int == TimesheetShift.INT_12_30_PM:
            return '12:30 pm'
        elif time_int == TimesheetShift.INT_1_00_PM:
            return '1:00 pm'
        elif time_int == TimesheetShift.INT_1_30_PM:
            return '1:30 pm'
        elif time_int == TimesheetShift.INT_2_00_PM:
            return '2:00 pm'
        elif time_int == TimesheetShift.INT_2_30_PM:
            return '2:30 pm'
        elif time_int == TimesheetShift.INT_3_00_PM:
            return '3:00 pm'
        elif time_int == TimesheetShift.INT_3_30_PM:
            return '3:30 pm'
        elif time_int == TimesheetShift.INT_4_00_PM:
            return '4:00 pm'
        elif time_int == TimesheetShift.INT_4_30_PM:
            return '4:30 pm'
        elif time_int == TimesheetShift.INT_5_00_PM:
            return '5:00 pm'
        elif time_int == TimesheetShift.INT_5_30_PM:
            return '5:30 pm'
        elif time_int == TimesheetShift.INT_6_00_PM:
            return '6:00 pm'
        elif time_int == TimesheetShift.INT_6_30_PM:
            return '6:30 pm'
        elif time_int == TimesheetShift.INT_7_00_PM:
            return '7:00 pm'
        elif time_int == TimesheetShift.INT_7_30_PM:
            return '7:30 pm'
        elif time_int == TimesheetShift.INT_8_00_PM:
            return '8:00 pm'
        elif time_int == TimesheetShift.INT_8_30_PM:
            return '8:30 pm'
        elif time_int == TimesheetShift.INT_9_00_PM:
            return '9:00 pm'
        elif time_int == TimesheetShift.INT_9_30_PM:
            return '9:30 pm'
        elif time_int == TimesheetShift.INT_10_00_PM:
            return '10:00 pm'
        elif time_int == TimesheetShift.INT_10_30_PM:
            return '10:30 pm'
        elif time_int == TimesheetShift.INT_11_00_PM:
            return '11:00 pm'
        elif time_int == TimesheetShift.INT_11_30_PM:
            return '11:30 pm'
        elif time_int == TimesheetShift.INT_12_00_AM:
            return '12:00 am'
        elif time_int == TimesheetShift.INT_12_30_AM:
            return '12:30 am'
        elif time_int == TimesheetShift.INT_1_00_AM:
            return '1:00 am'
        else:
            raise ValueError('Unhandled value of "{0}".'.format(time_int))

    @staticmethod
    def get_preset_time_int_from_str(time_str):
        """
        Converts a given time integer to the corresponding preset string.
        :param time_str: Time string to convert.
        :return: Corresponding int for string.
        """
        if time_str == '-':
            return TimesheetShift.INT_NULL_TIME
        elif time_str == '6:00 am' or time_str == '06:00 AM':
            return TimesheetShift.INT_6_00_AM
        elif time_str == '6:30 am' or time_str == '06:30 AM':
            return TimesheetShift.INT_6_30_AM
        elif time_str == '7:00 am' or time_str == '07:00 AM':
            return TimesheetShift.INT_7_00_AM
        elif time_str == '7:30 am' or time_str == '07:30 AM':
            return TimesheetShift.INT_7_30_AM
        elif time_str == '8:00 am' or time_str == '08:00 AM':
            return TimesheetShift.INT_8_00_AM
        elif time_str == '8:30 am' or time_str == '08:30 AM':
            return TimesheetShift.INT_8_30_AM
        elif time_str == '9:00 am' or time_str == '09:00 AM':
            return TimesheetShift.INT_9_00_AM
        elif time_str == '9:30 am' or time_str == '09:30 AM':
            return TimesheetShift.INT_9_30_AM
        elif time_str == '10:00 am' or time_str == '10:00 AM':
            return TimesheetShift.INT_10_00_AM
        elif time_str == '10:30 am' or time_str == '10:30 AM':
            return TimesheetShift.INT_10_30_AM
        elif time_str == '11:00 am' or time_str == '11:00 AM':
            return TimesheetShift.INT_11_00_AM
        elif time_str == '11:30 am' or time_str == '11:30 AM':
            return TimesheetShift.INT_11_30_AM
        elif time_str == '12:00 pm' or time_str == '12:00 PM':
            return TimesheetShift.INT_12_00_PM
        elif time_str == '12:30 pm' or time_str == '12:30 PM':
            return TimesheetShift.INT_12_30_PM
        elif time_str == '1:00 pm' or time_str == '01:00 PM':
            return TimesheetShift.INT_1_00_PM
        elif time_str == '1:30 pm' or time_str == '01:30 PM':
            return TimesheetShift.INT_1_30_PM
        elif time_str == '2:00 pm' or time_str == '02:00 PM':
            return TimesheetShift.INT_2_00_PM
        elif time_str == '2:30 pm' or time_str == '02:30 PM':
            return TimesheetShift.INT_2_30_PM
        elif time_str == '3:00 pm' or time_str == '03:00 PM':
            return TimesheetShift.INT_3_00_PM
        elif time_str == '3:30 pm' or time_str == '03:30 PM':
            return TimesheetShift.INT_3_30_PM
        elif time_str == '4:00 pm' or time_str == '04:00 PM':
            return TimesheetShift.INT_4_00_PM
        elif time_str == '4:30 pm' or time_str == '04:30 PM':
            return TimesheetShift.INT_4_30_PM
        elif time_str == '5:00 pm' or time_str == '05:00 PM':
            return TimesheetShift.INT_5_00_PM
        elif time_str == '5:30 pm' or time_str == '05:30 PM':
            return TimesheetShift.INT_5_30_PM
        elif time_str == '6:00 pm' or time_str == '06:00 PM':
            return TimesheetShift.INT_6_00_PM
        elif time_str == '6:30 pm' or time_str == '06:30 PM':
            return TimesheetShift.INT_6_30_PM
        elif time_str == '7:00 pm' or time_str == '07:00 PM':
            return TimesheetShift.INT_7_00_PM
        elif time_str == '7:30 pm' or time_str == '07:30 PM':
            return TimesheetShift.INT_7_30_PM
        elif time_str == '8:00 pm' or time_str == '08:00 PM':
            return TimesheetShift.INT_8_00_PM
        elif time_str == '8:30 pm' or time_str == '08:30 PM':
            return TimesheetShift.INT_8_30_PM
        elif time_str == '9:00 pm' or time_str == '09:00 PM':
            return TimesheetShift.INT_9_00_PM
        elif time_str == '9:30 pm' or time_str == '09:30 PM':
            return TimesheetShift.INT_9_30_PM
        elif time_str == '10:00 pm':
            return TimesheetShift.INT_10_00_PM
        elif time_str == '10:30 pm':
            return TimesheetShift.INT_10_30_PM
        elif time_str == '11:00 pm':
            return TimesheetShift.INT_11_00_PM
        elif time_str == '11:30 pm':
            return TimesheetShift.INT_11_30_PM
        elif time_str == '12:00 am':
            return TimesheetShift.INT_12_00_AM
        elif time_str == '12:30 am':
            return TimesheetShift.INT_12_30_AM
        elif time_str == '1:00 am' or time_str == '01:00 AM':
            return TimesheetShift.INT_1_00_AM
        else:
            raise ValueError('Unhandled value of "{0}".'.format(time_str))

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        employee = cae_home_models.User.create_dummy_model()
        pay_period = PayPeriod.create_dummy_model()
        pay_period_start = pay_period.get_start_as_datetime()
        clock_in = pay_period_start + timezone.timedelta(hours=12)
        clock_out = clock_in + timezone.timedelta(hours=4)
        signature = '1'
        try:
            return TimesheetShift.objects.get(
                employee=employee,
                pay_period=pay_period,
                clock_in=clock_in,
                clock_out=clock_out,
                signature=signature,
            )
        except ObjectDoesNotExist:
            return TimesheetShift.objects.create(
                employee=employee,
                pay_period=pay_period,
                clock_in=clock_in,
                clock_out=clock_out,
                signature=signature,
            )


class CurrentStepEmployees(models.Model):
    """
    Step Employee data required for printing timesheets.
    """
    # Relationship keys.
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    # employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    fund_and_cost_center = models.CharField(blank=True, null=True, max_length=10)
    job_code = models.CharField(blank=True, null=True, max_length=25)
    hours_per_pay_period = models.DecimalField(decimal_places=1, max_digits=4)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Current Step Employee'
        verbose_name_plural = 'Current Step Employees'

    def __str__(self):
        return '{0}'.format(self.employee)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(CurrentStepEmployees, self).save(*args, **kwargs)

    def create_dummy_model(self):
        """
        Create Dummy Data for Testing Purposes
        """
        employee = cae_home_models.User.create_dummy_model()
        fund_and_cost_center = '11-0024680'
        job_code = 'Stu-Federal Tutor SEQ'
        hours_per_pay_period = 10
        try:
            return TimesheetShift.objects.get(
                employee=employee,
                fund_and_cost_center=fund_and_cost_center,
                job_code=job_code,
                hours_per_pay_period=hours_per_pay_period,
            )
        except ObjectDoesNotExist:
            return TimesheetShift.objects.create(
                employee=employee,
                fund_and_cost_center=fund_and_cost_center,
                job_code=job_code,
                hours_per_pay_period=hours_per_pay_period,
            )
