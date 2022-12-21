"""
Form views for SuccessCtrTimesheets app.
"""

# System Imports.
from django import forms
from django.utils import timezone as tz


# User Class Imports.
from .models import TimesheetShift, CurrentStepEmployees
from cae_home import forms as cae_home_forms
from cae_home import models as cae_home_models


class TimeSheetDayForm(forms.Form):
    """
    Form representing a single day in a given PayPeriod.

    As per client's request, each day is divided into:
        * Morning Start/End
        * Afternoon Start/End
        * Evening Start/End
    with each respective grouping having limited preset times that can be selected.
    """
    # Default Preset Choices.
    MORNING_TIME_0 = TimesheetShift.INT_NULL_TIME
    AFTERNOON_TIME_0 = TimesheetShift.INT_NULL_TIME
    EVENING_TIME_0 = TimesheetShift.INT_NULL_TIME

    # Morning Preset Choices.
    MORNING_TIME_1 = TimesheetShift.INT_7_00_AM
    MORNING_TIME_2 = TimesheetShift.INT_7_30_AM
    MORNING_TIME_3 = TimesheetShift.INT_8_00_AM
    MORNING_TIME_4 = TimesheetShift.INT_8_30_AM
    MORNING_TIME_5 = TimesheetShift.INT_9_00_AM
    MORNING_TIME_6 = TimesheetShift.INT_9_30_AM
    MORNING_TIME_7 = TimesheetShift.INT_10_00_AM
    MORNING_TIME_8 = TimesheetShift.INT_10_30_AM
    MORNING_TIME_9 = TimesheetShift.INT_11_00_AM
    MORNING_TIME_10 = TimesheetShift.INT_11_30_AM
    MORNING_TIME_11 = TimesheetShift.INT_12_00_PM

    MORNING_CHOICES = (
        (MORNING_TIME_0, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_0)),  # - (Default)
        (MORNING_TIME_1, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_1)),  # 7:00 am
        (MORNING_TIME_2, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_2)),  # 7:30 am
        (MORNING_TIME_3, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_3)),  # 8:00 am
        (MORNING_TIME_4, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_4)),  # 8:30 am
        (MORNING_TIME_5, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_5)),  # 9:00 am
        (MORNING_TIME_6, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_6)),  # 9:30 am
        (MORNING_TIME_7, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_7)),  # 10:00 am
        (MORNING_TIME_8, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_8)),  # 10:30 am
        (MORNING_TIME_9, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_9)),  # 11:00 am
        (MORNING_TIME_10, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_10)),  # 11:30 am
        (MORNING_TIME_11, TimesheetShift.get_preset_time_str_from_int(MORNING_TIME_11)),  # 12:00 pm
    )

    # Afternoon Preset Choices.
    AFTERNOON_TIME_1 = TimesheetShift.INT_12_00_PM
    AFTERNOON_TIME_2 = TimesheetShift.INT_12_30_PM
    AFTERNOON_TIME_3 = TimesheetShift.INT_1_00_PM
    AFTERNOON_TIME_4 = TimesheetShift.INT_1_30_PM
    AFTERNOON_TIME_5 = TimesheetShift.INT_2_00_PM
    AFTERNOON_TIME_6 = TimesheetShift.INT_2_30_PM
    AFTERNOON_TIME_7 = TimesheetShift.INT_3_00_PM
    AFTERNOON_TIME_8 = TimesheetShift.INT_3_30_PM
    AFTERNOON_TIME_9 = TimesheetShift.INT_4_00_PM
    AFTERNOON_TIME_10 = TimesheetShift.INT_4_30_PM
    AFTERNOON_TIME_11 = TimesheetShift.INT_5_00_PM

    AFTERNOON_CHOICES = (
        (AFTERNOON_TIME_0, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_0)),  # - (Default)
        (AFTERNOON_TIME_1, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_1)),  # 12:00 pm
        (AFTERNOON_TIME_2, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_2)),  # 12:30 pm
        (AFTERNOON_TIME_3, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_3)),  # 1:00 pm
        (AFTERNOON_TIME_4, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_4)),  # 1:30 pm
        (AFTERNOON_TIME_5, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_5)),  # 2:00 pm
        (AFTERNOON_TIME_6, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_6)),  # 2:30 pm
        (AFTERNOON_TIME_7, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_7)),  # 3:00 pm
        (AFTERNOON_TIME_8, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_8)),  # 3:30 pm
        (AFTERNOON_TIME_9, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_9)),  # 4:00 pm
        (AFTERNOON_TIME_10, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_10)),  # 4:30 pm
        (AFTERNOON_TIME_11, TimesheetShift.get_preset_time_str_from_int(AFTERNOON_TIME_11)),  # 5:00 pm
    )

    # Evening Preset Choices.
    EVENING_TIME_1 = TimesheetShift.INT_5_00_PM
    EVENING_TIME_2 = TimesheetShift.INT_5_30_PM
    EVENING_TIME_3 = TimesheetShift.INT_6_00_PM
    EVENING_TIME_4 = TimesheetShift.INT_6_30_PM
    EVENING_TIME_5 = TimesheetShift.INT_7_00_PM
    EVENING_TIME_6 = TimesheetShift.INT_7_30_PM
    EVENING_TIME_7 = TimesheetShift.INT_8_00_PM
    EVENING_TIME_8 = TimesheetShift.INT_8_30_PM
    EVENING_TIME_9 = TimesheetShift.INT_9_00_PM
    EVENING_TIME_10 = TimesheetShift.INT_9_30_PM
    EVENING_TIME_11 = TimesheetShift.INT_10_00_PM
    EVENING_TIME_12 = TimesheetShift.INT_10_30_PM
    EVENING_TIME_13 = TimesheetShift.INT_11_00_PM
    EVENING_TIME_14 = TimesheetShift.INT_11_30_PM
    EVENING_TIME_15 = TimesheetShift.INT_12_00_AM
    EVENING_TIME_16 = TimesheetShift.INT_12_30_AM
    EVENING_TIME_17 = TimesheetShift.INT_1_00_AM

    EVENING_CHOICES = (
        (EVENING_TIME_0, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_0)),  # - (Default)
        (EVENING_TIME_1, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_1)),  # 5:00 pm
        (EVENING_TIME_2, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_2)),  # 5:30 pm
        (EVENING_TIME_3, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_3)),  # 6:00 pm
        (EVENING_TIME_4, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_4)),  # 6:30 pm
        (EVENING_TIME_5, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_5)),  # 7:00 pm
        (EVENING_TIME_6, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_6)),  # 7:30 pm
        (EVENING_TIME_7, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_7)),  # 8:00 pm
        (EVENING_TIME_8, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_8)),  # 8:30 pm
        (EVENING_TIME_9, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_9)),  # 9:00 pm
        (EVENING_TIME_10, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_10)),  # 9:30 pm
        (EVENING_TIME_11, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_11)),  # 10:00 pm
        (EVENING_TIME_12, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_12)),  # 10:30 pm
        (EVENING_TIME_13, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_13)),  # 11:00 pm
        (EVENING_TIME_14, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_14)),  # 11:30 pm
        (EVENING_TIME_15, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_15)),  # 12:00 am
        (EVENING_TIME_16, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_16)),  # 12:30 am
        (EVENING_TIME_17, TimesheetShift.get_preset_time_str_from_int(EVENING_TIME_17)),  # 1:00 am
    )

    # Utility variables to make view logic easier.
    MORNING_EARLIEST_INT = MORNING_TIME_1
    MORNING_LATEST_INT = MORNING_TIME_11
    AFTERNOON_EARLIEST_INT = AFTERNOON_TIME_1
    AFTERNOON_LATEST_INT = AFTERNOON_TIME_11
    EVENING_EARLIEST_INT = EVENING_TIME_1
    EVENING_LATEST_INT = EVENING_TIME_17
    MORNING_EARLIEST_STR = TimesheetShift.get_preset_time_str_from_int(MORNING_EARLIEST_INT)
    MORNING_LATEST_STR = TimesheetShift.get_preset_time_str_from_int(MORNING_LATEST_INT)
    AFTERNOON_EARLIEST_STR = TimesheetShift.get_preset_time_str_from_int(AFTERNOON_EARLIEST_INT)
    AFTERNOON_LATEST_STR = TimesheetShift.get_preset_time_str_from_int(AFTERNOON_LATEST_INT)
    EVENING_EARLIEST_STR = TimesheetShift.get_preset_time_str_from_int(EVENING_EARLIEST_INT)
    EVENING_LATEST_STR = TimesheetShift.get_preset_time_str_from_int(EVENING_LATEST_INT)

    # Define form fields.
    morning_begin = forms.ChoiceField(choices=MORNING_CHOICES)
    morning_end = forms.ChoiceField(choices=MORNING_CHOICES)
    afternoon_begin = forms.ChoiceField(choices=AFTERNOON_CHOICES)
    afternoon_end = forms.ChoiceField(choices=AFTERNOON_CHOICES)
    evening_begin = forms.ChoiceField(choices=EVENING_CHOICES)
    evening_end = forms.ChoiceField(choices=EVENING_CHOICES)

    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

        # Set default choice values.
        self.initial['morning_begin'] = self.MORNING_TIME_0
        self.initial['morning_end'] = self.MORNING_TIME_0
        self.initial['afternoon_begin'] = self.AFTERNOON_TIME_0
        self.initial['afternoon_end'] = self.AFTERNOON_TIME_0
        self.initial['evening_begin'] = self.EVENING_TIME_0
        self.initial['evening_end'] = self.EVENING_TIME_0

    def clean(self):
        """
        Extra validation for combined form values.
        """
        # Get cleaned form data.
        cleaned_data = super().clean()
        # index = 0
        for index in range(0, 13):
            morning_begin = cleaned_data.get('morning_begin_{0}'.format(index))
            morning_end = cleaned_data.get('morning_end_{0}'.format(index))
            afternoon_begin = cleaned_data.get('afternoon_begin_{0}'.format(index))
            afternoon_end = cleaned_data.get('afternoon_end_{0}'.format(index))
            evening_begin = cleaned_data.get('evening_begin_{0}'.format(index))
            evening_end = cleaned_data.get('evening_end_{0}'.format(index))

            if morning_begin is not None:
                morning_begin = int(cleaned_data.get('morning_begin_{0}'.format(index)))
            if morning_end is not None:
                morning_end = int(cleaned_data.get('morning_end_{0}'.format(index)))
            if afternoon_begin is not None:
                afternoon_begin = int(cleaned_data.get('afternoon_begin_{0}'.format(index)))
            if afternoon_end is not None:
                afternoon_end = int(cleaned_data.get('afternoon_end_{0}'.format(index)))
            if evening_begin is not None:
                evening_begin = int(cleaned_data.get('evening_begin_{0}'.format(index)))
            if evening_end is not None:
                evening_end = int(cleaned_data.get('evening_end_{0}'.format(index)))

            if morning_begin is not None and morning_end is not None:
                # Validate combined morning fields.
                if morning_begin != TimesheetShift.INT_NULL_TIME and morning_end != TimesheetShift.INT_NULL_TIME:
                    # Both morning begin and end is set. Verify end is after start.
                    if morning_end <= morning_begin:
                        self.add_error('morning_begin_{0}'.format(index), 'Morning end must be after morning start.')
                elif not (morning_begin == TimesheetShift.INT_NULL_TIME and morning_end == TimesheetShift.INT_NULL_TIME):
                    # If we got this far, then one is set while the other is empty. Invalid combination.
                    self.add_error('morning_begin_{0}'.format(index), 'Both morning shift times must either be set or empty.')

            if afternoon_begin is not None and afternoon_end is not None:
                # Validate combined afternoon fields.
                if afternoon_begin != TimesheetShift.INT_NULL_TIME and afternoon_end != TimesheetShift.INT_NULL_TIME:
                    # Both afternoon begin and end is set. Verify end is after start.
                    if afternoon_end <= afternoon_begin:
                        self.add_error('afternoon_begin_{0}'.format(index), 'Afternoon end must be after afternoon start.')
                elif not (afternoon_begin == TimesheetShift.INT_NULL_TIME and afternoon_end == TimesheetShift.INT_NULL_TIME):
                    # If we got this far, then one is set while the other is empty. Invalid combination.
                    self.add_error('afternoon_begin_{0}'.format(index), 'Both afternoon shift times must either be set or empty.')

            if evening_begin is not None and evening_end is not None:
                # Validate combined evening fields.
                if evening_begin != TimesheetShift.INT_NULL_TIME and evening_end != TimesheetShift.INT_NULL_TIME:
                    # Both evening begin and end is set. Verify end is after start.
                    if evening_end <= evening_begin:
                        self.add_error('evening_begin_{0}'.format(index), 'Evening end must be after evening start.')
                elif not (evening_begin == TimesheetShift.INT_NULL_TIME and evening_end == TimesheetShift.INT_NULL_TIME):
                    # If we got this far, then one is set while the other is empty. Invalid combination.
                    self.add_error('evening_begin_{0}'.format(index), 'Both evening shift times must either be set or empty.')
                # for efficiency, break when you reach the correct form number
                if morning_begin is not None:
                    break
            else:
                pass

class EmailStepEmployees(forms.Form):
    email_to_choices = ((1, 'all'), (2, 'Un-submitted'),)
    email_to = forms.ChoiceField(choices=email_to_choices, initial=1, label='To')
    email_subject = forms.CharField(required=True, label='Subject')
    email_message = forms.CharField(widget=forms.Textarea, required=True, label='Message')

    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)


class SearchTimesheet(forms.Form):
    """
    Step Admin Search Past timesheets form.
    """
    date = forms.DateField(widget=cae_home_forms.DatePickerWidget(attrs={'value': tz.localdate()}), required=False)

    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Extra validation for combined form values.
        """
        # Get cleaned form data.
        cleaned_data = super().clean()
        current_date = tz.localdate()
        date_data = cleaned_data.get('date')

        # if no date is supplied set to current date
        if date_data is None:
            date_data = current_date

        # Check if date supplied is future date
        if date_data > current_date:
            self.add_error('date', 'Incorrect data received, did u select a future date?')


class CurrentStepEmployeesForm(forms.ModelForm):
    class Meta:
        model = CurrentStepEmployees
        fields = [
            'employee',
            'fund_and_cost_center',
            'job_code',
            'hours_per_pay_period'
        ]

        widgets = {'hours_per_pay_period': forms.TextInput(attrs={'min': 0, 'type': 'number', 'step': 0.5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # filter out STEP employees
        self.fields['employee'].queryset = cae_home_models.User.objects.filter(groups__name='STEP Employee', is_active=True)

    def clean(self):
        """
        Extra validation for combined form values.
        """
        # Get cleaned form data.
        super().clean()

