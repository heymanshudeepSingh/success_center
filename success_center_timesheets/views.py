"""
Views for SuccessCenterTimeSheets App.
"""

# System Imports.
import copy, datetime, pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mass_mail
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils import timezone

# User Imports.
from . import forms
from . import models
from cae_home import models as cae_home_models
from cae_home.decorators import group_required
from workspace.settings.reusable_settings import SUCCESS_CENTER_GROUPS


# region Standard Methods

def populate_pay_periods():
    """
    Handles creation of pay periods. Should be called any time a pay period is accessed in a view, prior to view logic.

    This checks if a valid (pay_period + 1) is present for the current date.
        If so, it does nothing.
        If not, then it populates new pay periods from last one found, to one pay period past present date.

        On the chance that no pay periods are found, then populates starting from 05-25-2015 (the first known valid pay
        period in production data, as of writing this).

    Note: Checks for (pay_period + 1) to guarantee no errors, even on the unlikely case of a user loading a view just as
    the pay period changes over.
    """
    pay_period_found = True
    current_date = timezone.localdate()
    plus_1_date = current_date + datetime.timedelta(days=14)

    # Check for current pay period.
    try:
        models.PayPeriod.objects.get(date_start__lte=current_date, date_end__gte=current_date)

        # Check for current pay period + 1.
        try:
            models.PayPeriod.objects.get(date_start__lte=plus_1_date, date_end__gte=plus_1_date)
        except ObjectDoesNotExist:
            pay_period_found = False
    except ObjectDoesNotExist:
        pay_period_found = False

    # If both pay periods were not found, create new pay periods.
    if not pay_period_found:
        try:
            last_pay_period = models.PayPeriod.objects.latest('date_start')
        except models.PayPeriod.DoesNotExist:
            last_pay_period = None

        # If no pay periods found, manually create first one at 5-25-2015.
        if last_pay_period is None:
            last_pay_period = models.PayPeriod.objects.create(date_start=datetime.date(2015, 5, 25))

        # Continue until pay_period + 1 is created.
        while last_pay_period.date_start < plus_1_date and last_pay_period.date_end < plus_1_date:
            next_start = last_pay_period.date_start + datetime.timedelta(days=14)
            last_pay_period = models.PayPeriod.objects.create(date_start=next_start)


# endregion Standard Methods


@login_required
@group_required(SUCCESS_CENTER_GROUPS)
def index(request):
    """
    Index view for TimeSheets logic.
    """
    # Attempt to populate pay periods.
    populate_pay_periods()

    # check if user is Admin
    step_admin = cae_home_models.User.objects.filter(groups__name='STEP Admin', is_active=True)
    step_employee = cae_home_models.User.objects.filter(groups__name='STEP Employee', is_active=True)

    if request.user in step_admin:
        # Redirect to student model creation page.
        return redirect('success_center_timesheets:admin_view')

    elif request.user in step_employee:
        # Pull models from database.
        pay_period = models.PayPeriod.get_payperiod()
        shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=request.user)

        total = 0
        for shift in shifts:

            clock_out_localtime = timezone.localtime(shift.clock_out, pytz.timezone('America/Detroit'))
            clock_in_localtime = timezone.localtime(shift.clock_in, pytz.timezone('America/Detroit'))

            clock_out_int = shift.get_preset_time_int_from_str(clock_out_localtime.strftime('%-I:%M %p').lower())
            clock_in_int = shift.get_preset_time_int_from_str(clock_in_localtime.strftime('%-I:%M %p').lower())

            total_hours = clock_out_int - clock_in_int
            shift.total = total_hours / 2
            shift.local_clock_in = clock_in_localtime
            shift.local_clock_out = clock_out_localtime
            total += shift.total
            shift.date = shift.clock_in.date()

        # Send to template for user display.
        return TemplateResponse(request, 'success_center_timesheets/index.html', {
            'pay_period': pay_period,
            'shifts': shifts,
            'total': total,
        })
    else:
        raise PermissionError('You do not have permission to access this page.')


@login_required
@group_required('STEP Admin')
def admin_view_index(request):
    """
    View to edit and update TimeSheet data for all users.
    """
    # Attempt to populate pay periods.
    populate_pay_periods()

    # Set cookies.
    request.session['success_center_timesheets_index'] = 'admin_view_index'

    # Pull models from database.
    pay_period = models.PayPeriod.get_payperiod()

    # get shifts in current pay period - to check which employees have not yet submitted their hours
    employee_shifts = models.TimesheetShift.objects.filter(
        pay_period=pay_period,
    ).values_list(
        'employee__username',
        flat=True,
    )

    # get all Step employees
    step_employees = cae_home_models.User.objects.filter(groups__name='STEP Employee', is_active=True)
    for employee in step_employees:
        # check if username exists in employee shifts tuple
        if employee.username in employee_shifts:
            employee.submitted = True
        else:
            employee.submitted = False

    # Send to template for user display.
    return TemplateResponse(request, 'success_center_timesheets/admin_index.html', {
        'step_employees': step_employees,
    })


@login_required
@group_required('STEP Admin')
def search_timesheets(request):
    # Attempt to populate pay periods.
    populate_pay_periods()
    # initialize the form
    form = forms.SearchTimesheet(request.POST)
    # initialize shifts
    shifts = None

    current_date = timezone.localdate()
    date = timezone.localdate()
    if request.method == 'POST':
        if form.is_valid():
            date = form.cleaned_data['date']
            if date is None:
                date = current_date
            # get associated pay period for that date
            pay_period = models.PayPeriod.objects.get(date_start__lte=date, date_end__gte=date)
            # update date to the start of the pay period
            date = pay_period.date_start

            # get shifts for that payperiod
            shifts = models.TimesheetShift.objects.filter(
                pay_period=pay_period,
            ).values_list(
                'employee__username',
                'employee_id',
            ).distinct()
            if not shifts:
                messages.info(request, 'No shifts found for {0}'.format(date))

    elif request.method == 'GET':
        pass

    # validate everything and then redirect to template
    return TemplateResponse(request, 'success_center_timesheets/search_timesheet.html', {
        'form': form,
        'shifts': shifts,
        'date': date
    })


@login_required
@group_required('STEP Admin')
def display_past_step_employees(request):
    """
    Outputs all the employees who ever worked for Success Center
    """
    past_step_employees = cae_home_models.User.objects.filter(
        groups__name__contains='STEP Employee',
        is_active=False,
    ).values(
        'username',
        'groups__groupmembership__date_left',
        'groups__name',
        'pk',
        'first_name',
        'last_name',
    ).distinct()

    return TemplateResponse(request, 'success_center_timesheets/past_step_employees.html', {
        'past_step_employees': past_step_employees,
    })


@login_required
@group_required('STEP Admin')
def restore_inactive_step_employee(request, pk):
    """
    Step admin's past employee restore functionality
    """
    # check inactive user's pk
    if pk:
        try:
            # Set User to active
            cae_home_models.User.objects.filter(pk=pk).update(
                is_active=True,
                is_staff=True
            )
            models.CurrentStepEmployees.objects.filter(pk=pk)
            messages.success(
                request,
                'Successfully restored {0}'.format(models.cae_home_models.User.objects.get(pk=pk).username),
            )
        except ObjectDoesNotExist:
            messages.error(request, 'User not found!')

    return redirect('success_center_timesheets:admin_view')


@login_required
@group_required('STEP Admin')
def remove_step_employee(request, pk):
    """
    Step admin's past employee restore functionality
    """
    # check user's pk to delete
    if pk:
        try:
            user = cae_home_models.User.objects.filter(pk=pk)
            user.update(
                is_active=False,
                is_staff=False,
            )

            models.CurrentStepEmployees.objects.filter(employee=user[0]).delete()
            messages.warning(
                request,
                'Successfully removed {0}'.format(models.cae_home_models.User.objects.get(pk=pk).username),
            )
        except ObjectDoesNotExist:
            messages.error(request, 'User not found!')

    return redirect('success_center_timesheets:admin_view')


@login_required
@group_required('STEP Admin')
def admin_email(request):
    """
    This allows admin to send emails to STEP Employees
    """
    # Attempt to populate pay periods.
    populate_pay_periods()

    # Pull models from database.
    pay_period = models.PayPeriod.get_payperiod()
    step_employees = cae_home_models.User.objects.filter(groups__name='STEP Employee', is_active=True)
    employee_shifts = models.TimesheetShift.objects.filter(pay_period=pay_period).values_list('employee__username')
    employees_un_submitted_shifts = step_employees.exclude(username__in=employee_shifts)

    from cae_tools import utils

    # mass_mail accepts list format for email recipients
    email_recipients = []

    user = request.user
    wmu_user = user.userintermediary.wmu_user

    if request.method == 'POST':
        form = forms.EmailStepEmployees(request.POST)
        success_bool = False
        if form.is_valid():
            email_to = form.cleaned_data.get('email_to')
            email_subject = form.cleaned_data.get('email_subject')
            email_message = form.cleaned_data.get('email_message')
            email_from = wmu_user.official_email

            # CASE: ALL
            if email_to == '1':
                # populating email recipients
                for employees in step_employees:
                    email_recipients.append(str(employees.email))
                message1 = (str(email_subject), str(email_message), None, email_recipients)

                try:
                    # Attempt to send email.
                    utils.send_single_email(
                        email_from=email_from,
                        email_to=email_recipients,
                        email_subject=email_subject,
                        email_message=email_message,

                    )
                    # send_mass_mail((message1,), fail_silently=True)
                    success_bool = True
                    messages.success(request, 'Successfully send emails to all STEP Employees!')

                except ConnectionRefusedError:
                    messages.error(request, 'FAILED To Send Email!')

            # CASE: Un-submitted timesheet users
            elif email_to == '2':
                # populating email recipients
                for employees in employees_un_submitted_shifts:
                    email_recipients.append(str(employees.email))
                message1 = (str(email_subject), str(email_message), None, email_recipients)
                try:
                    send_mass_mail((message1,), fail_silently=True)
                    success_bool = True
                    messages.success(request, 'Successfully send emails to all Employees with un-submitted timesheets!')

                except ConnectionRefusedError:
                    messages.error(request, 'FAILED To Send Email!')

            if success_bool:
                return redirect('success_center_timesheets:admin_view')

    else:
        form = forms.EmailStepEmployees()
        return render(request, 'success_center_timesheets/email.html', {
            'form': form,
        })


@login_required
@group_required('STEP Admin')
def current_employees(request):
    """
    Handle current employees - job code, fund and cost center, etc.
    """

    # Initialize formset
    current_step_employees_formset = modelformset_factory(
        model=models.CurrentStepEmployees,
        form=forms.CurrentStepEmployeesForm,
        can_delete=True,
    )

    formset = current_step_employees_formset()
    # check for duplicates
    existing_employees = []
    dup_exist = False

    if request.method == 'POST':
        formset = current_step_employees_formset(request.POST)
        deleted_employees = []
        # initialize formset
        if formset.is_valid():
            for form in formset:
                cleaned_employee = form.cleaned_data.get('employee')
                del_checked = form.cleaned_data.get('DELETE')
                if not del_checked:
                    if cleaned_employee in existing_employees:
                        messages.error(request, 'Employee already exists!')
                        dup_exist = True
                else:
                    deleted_employees.append(cleaned_employee)

                existing_employees.append(cleaned_employee)
            if not dup_exist:
                formset.save()

            # dup_exists prevents redundant Employee already exists! error
            if deleted_employees and not dup_exist:
                messages.warning(request, f'Deleted Employee: {deleted_employees}')

        # print errors
        else:
            for form in formset:
                for error in form.errors:
                    messages.error(request, f'* Please check {error}')
        return HttpResponseRedirect('current_employees')

    return render(request, 'success_center_timesheets/current_employees.html', {
        'formset': formset,
    })


@login_required
@group_required(SUCCESS_CENTER_GROUPS)
def edit_timesheets(request, pk=None, date=None):
    """
    View to update TimeSheet data for current employee.
    """
    # Attempt to populate pay periods.
    populate_pay_periods()
    existing_signature = None

    # employee is Step Employee
    is_admin = False

    # Check if employee is admin
    user_groups = request.user.groups.all()
    if user_groups.filter(name__contains='STEP Admin'):
        is_admin = True

    if pk is not None:
        if not is_admin:
            raise PermissionError('You do not have permission to access this page.')

    success_url = reverse_lazy('success_center_timesheets:index')

    # initialize payperiod
    pay_period = models.PayPeriod.get_payperiod()

    # initialize employee data, which will later have job code, etc
    employee_data = None

    if pk:
        employee = models.cae_home_models.User.objects.get(pk=pk)
        if date:
            # Pull models from database.
            pay_period = models.PayPeriod.objects.get(date_start__lte=date, date_end__gte=date)
        shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

    else:
        employee = request.user
        shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

    # # Get Signature model
    # signature_queryset = shifts.values_list('signature', flat=True)
    # for s in signature_queryset:
    #     existing_signature = s

    # Calculate data structures of shifts for given employee and pay period.
    form_data = calculate_form_shift_data(pay_period, shifts)
    form_initial_data = {}

    for day_data in form_data:
        # updating form_initial_data, so it has data for all the forms.
        form_initial_data.update(day_data['form_data'])

    # changing from tuple to dictionary format
    form_initial_data = dict(form_initial_data.items())
    # a list to hold all the forms
    forms_in_pay_period = []

    start_date = pay_period.date_start
    end_date = pay_period.date_end

    # Loop through all dates in PayPeriod range, starting with start of pay period.
    each_date_in_payperiod = start_date

    # Initialize forms.
    if request.method == 'POST':
        # Handle for employee data submission.
        # Note: Because we use disabled fields, and Django is dumb in how it handles them, we need to add any disabled
        # fields back into our POST data before proceeding.
        if pk:
            employee = models.cae_home_models.User.objects.get(pk=pk)
            if date:
                # Pull models from database.
                pay_period = models.PayPeriod.objects.get(date_start__lte=date, date_end__gte=date)
            shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

        else:
            employee = request.user
            shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

        # Get Signature model
        signature_queryset = shifts.values_list('signature', flat=True)
        for s in signature_queryset:
            existing_signature = s

        # First, make a copy of the POST dict, so we can edit it.
        post_data = copy.deepcopy(request.POST)
        increment_2 = 0

        # in previous commits we were passing in initial data dict
        # which resulted in forms never being updated upon post
        form_data_per_day = {}

        # looping through each day in payperiod
        while each_date_in_payperiod <= end_date:

            # Next, check each individual field. Add back in if missing.
            if 'morning_begin_{0}'.format(increment_2) not in post_data.keys():
                post_data['morning_begin_{0}'.format(increment_2)] = form_initial_data[
                    'morning_begin_{0}'.format(increment_2)]
            if 'morning_end_{0}'.format(increment_2) not in post_data.keys():
                post_data['morning_end_{0}'.format(increment_2)] = form_initial_data[
                    'morning_end_{0}'.format(increment_2)]
            if 'afternoon_begin_{0}'.format(increment_2) not in post_data.keys():
                post_data['afternoon_begin_{0}'.format(increment_2)] = form_initial_data[
                    'afternoon_begin_{0}'.format(increment_2)]
            if 'afternoon_end_{0}'.format(increment_2) not in post_data.keys():
                post_data['afternoon_end_{0}'.format(increment_2)] = form_initial_data[
                    'afternoon_end_{0}'.format(increment_2)]
            if 'evening_begin_{0}'.format(increment_2) not in post_data.keys():
                post_data['evening_begin_{0}'.format(increment_2)] = form_initial_data[
                    'evening_begin_{0}'.format(increment_2)]
            if 'evening_end_{0}'.format(increment_2) not in post_data.keys():
                post_data['evening_end_{0}'.format(increment_2)] = form_initial_data[
                    'evening_end_{0}'.format(increment_2)]

            # append single day data to form_data_per_day
            form_data_per_day.update(
                {'morning_begin_{0}'.format(increment_2): post_data['morning_begin_{0}'.format(increment_2)]},
            )
            form_data_per_day.update(
                {'morning_end_{0}'.format(increment_2): post_data['morning_end_{0}'.format(increment_2)]},
            )
            form_data_per_day.update(
                {'afternoon_begin_{0}'.format(increment_2): post_data['afternoon_begin_{0}'.format(increment_2)]},
            )
            form_data_per_day.update(
                {'afternoon_end_{0}'.format(increment_2): post_data['afternoon_end_{0}'.format(increment_2)]},
            )
            form_data_per_day.update(
                {'evening_begin_{0}'.format(increment_2): post_data['evening_begin_{0}'.format(increment_2)]},
            )
            form_data_per_day.update(
                {'evening_end_{0}'.format(increment_2): post_data['evening_end_{0}'.format(increment_2)]},
            )

            # Initialize form with updated POST data.
            form = forms.TimeSheetDayForm(form_data_per_day)

            # make fields unique
            renaming_for_uniqueness(form, increment_2)

            # finally append the each form to list
            forms_in_pay_period.append(form)
            # reset dictionary to hold data for next form
            # this prevents redundancy- forms will only have data for the given day
            form_data_per_day = {}
            increment_2 += 1
            # Increment current date to next day.
            each_date_in_payperiod = each_date_in_payperiod + timezone.timedelta(days=1)

    elif request.method == 'GET':
        if pk:
            employee = models.cae_home_models.User.objects.get(pk=pk)
            if date:
                # Pull models from database.
                pay_period = models.PayPeriod.objects.get(date_start__lte=date, date_end__gte=date)
            shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

        else:
            employee = request.user
            shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)
        # Get Signature model
        signature_queryset = shifts.values_list('signature', flat=True)
        # employee data like job code etc. for printing purposes
        employee_data = models.CurrentStepEmployees.objects.filter(
            employee=employee,
        ).values(
            'fund_and_cost_center',
            'job_code',
        )
        for s in signature_queryset:
            existing_signature = s
        id_integer = 0
        start_date = pay_period.date_start
        # Loop through all dates in PayPeriod range, starting with start of pay period.
        loop_day_in_pay_period = start_date

        for day_data in form_data:
            if day_data['date'] == loop_day_in_pay_period:
                form_initial_data = day_data['form_data']
            form = forms.TimeSheetDayForm(data=form_initial_data)
            renaming_for_uniqueness(form, id_integer)
            form.date = loop_day_in_pay_period
            form.number = id_integer
            forms_in_pay_period.append(form)
            loop_day_in_pay_period = loop_day_in_pay_period + timezone.timedelta(days=1)
            id_integer += 1

    name_increment = 0
    shifts_exist = False
    morning_validation = True
    afternoon_validation = True
    evening_validation = True
    all_fields_valid = False

    for f in forms_in_pay_period:
        # Get dictionary of all form errors. Contains keys of field names, and corresponding values of error messages.
        # We can use this to check the error keys in the below statements, and avoid doing any extra logic if the
        # corresponding fields have errors.
        form_error_dict = f.errors.as_data()
        all_fields_valid = False
        # Set any form fields to disabled, if populated with an actual data.
        # This means the pair of fields do not have an error, and the pair of fields are both non-null.
        if (
            'morning_begin_{0}'.format(name_increment) not in form_error_dict.keys()
            and int(f.data['morning_begin_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
            and int(f.data['morning_end_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
        ):
            shifts_exist = True
            if (
                int(f.data['morning_begin_{0}'.format(name_increment)])
                < int(f.data['morning_end_{0}'.format(name_increment)])
            ):
                # Morning values are populated. Set to disabled.
                f.fields['morning_begin_{0}'.format(name_increment)].initial = f.data[
                    'morning_begin_{0}'.format(name_increment)]
                f.initial['morning_begin_{0}'.format(name_increment)] = f.data[
                    'morning_begin_{0}'.format(name_increment)]

                f.fields['morning_end_{0}'.format(name_increment)].initial = f.data[
                    'morning_end_{0}'.format(name_increment)]
                f.initial['morning_end_{0}'.format(name_increment)] = f.data['morning_end_{0}'.format(name_increment)]
            else:
                morning_validation = False

        if (
            'afternoon_begin_{0}'.format(name_increment) not in form_error_dict.keys()
            and int(f.data['afternoon_begin_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
            and int(f.data['afternoon_end_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
        ):
            shifts_exist = True
            if (
                int(f.data['afternoon_begin_{0}'.format(name_increment)])
                < int(f.data['afternoon_end_{0}'.format(name_increment)])
            ):
                # Afternoon values are populated. Set to disable.
                f.fields['afternoon_begin_{0}'.format(name_increment)].initial = f.data[
                    'afternoon_begin_{0}'.format(name_increment)]
                f.initial['afternoon_begin_{0}'.format(name_increment)] = f.data[
                    'afternoon_begin_{0}'.format(name_increment)]

                f.fields['afternoon_end_{0}'.format(name_increment)].initial = f.data[
                    'afternoon_end_{0}'.format(name_increment)]
                f.initial['afternoon_end_{0}'.format(name_increment)] = f.data[
                    'afternoon_end_{0}'.format(name_increment)]
            else:
                afternoon_validation = False

        if (
            'evening_begin_{0}'.format(name_increment) not in form_error_dict.keys()
            and int(f.data['evening_begin_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
            and int(f.data['evening_end_{0}'.format(name_increment)]) != forms.TimesheetShift.INT_NULL_TIME
        ):
            shifts_exist = True
            if (
                int(f.data['evening_begin_{0}'.format(name_increment)])
                < int(f.data['evening_end_{0}'.format(name_increment)])
            ):
                # Evening values are populated. Set to disabled.
                f.fields['evening_begin_{0}'.format(name_increment)].initial = f.data[
                    'evening_begin_{0}'.format(name_increment)]
                f.initial['evening_begin_{0}'.format(name_increment)] = f.data[
                    'evening_begin_{0}'.format(name_increment)]

                f.fields['evening_end_{0}'.format(name_increment)].initial = f.data[
                    'evening_end_{0}'.format(name_increment)]
                f.initial['evening_end_{0}'.format(name_increment)] = f.data['evening_end_{0}'.format(name_increment)]
            else:
                evening_validation = False
        if not is_admin:
            if morning_validation and afternoon_validation and evening_validation and shifts_exist and f.is_valid():
                # if morning_validation or afternoon_validation or evening_validation:
                # Morning values are populated. Set to disabled.
                f.fields['morning_begin_{0}'.format(name_increment)].disabled = True
                f.fields['morning_end_{0}'.format(name_increment)].disabled = True

                # Afternoon values are populated. Set to disabled.
                f.fields['afternoon_begin_{0}'.format(name_increment)].disabled = True
                f.fields['afternoon_end_{0}'.format(name_increment)].disabled = True

                # Evening values are populated. Set to disabled.
                f.fields['evening_begin_{0}'.format(name_increment)].disabled = True
                f.fields['evening_end_{0}'.format(name_increment)].disabled = True
                all_fields_valid = True

        name_increment += 1

    start_date = pay_period.date_start
    # Loop through all dates in PayPeriod range, starting with start of pay period.
    another_naming_increment = 0

    for form in forms_in_pay_period:
        form.date = start_date
        form.number = another_naming_increment
        # Check if request is post.
        if request.method == 'POST':
            if pk:
                employee = models.cae_home_models.User.objects.get(pk=pk)
                if date:
                    # Pull models from database.
                    pay_period = models.PayPeriod.objects.get(date_start__lte=date, date_end__gte=date)
                shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)

            else:
                employee = request.user
                shifts = models.TimesheetShift.objects.filter(pay_period=pay_period, employee=employee)
            # Get Signature model
            signature_queryset = shifts.values_list('signature', flat=True)
            # employee data like job code etc. for printing purposes
            employee_data = models.CurrentStepEmployees.objects.filter(
                employee=employee,
            ).values(
                'fund_and_cost_center',
                'job_code',
            )
            for s in signature_queryset:
                existing_signature = s
            if form.is_valid():
                # Form is valid. Proceed.
                # Get form data values.
                morning_begin = int(form.cleaned_data['morning_begin_{0}'.format(another_naming_increment)])
                morning_end = int(form.cleaned_data['morning_end_{0}'.format(another_naming_increment)])
                afternoon_begin = int(form.cleaned_data['afternoon_begin_{0}'.format(another_naming_increment)])
                afternoon_end = int(form.cleaned_data['afternoon_end_{0}'.format(another_naming_increment)])
                evening_begin = int(form.cleaned_data['evening_begin_{0}'.format(another_naming_increment)])
                evening_end = int(form.cleaned_data['evening_end_{0}'.format(another_naming_increment)])

                # Process values.
                morning_status = save_morning_data(
                    request,
                    form.date,
                    morning_begin,
                    morning_end,
                    employee,
                    existing_signature,
                )
                afternoon_status = save_afternoon_data(
                    request,
                    form.date,
                    afternoon_begin,
                    afternoon_end,
                    employee,
                    existing_signature,
                )
                evening_status = save_evening_data(
                    request,
                    form.date,
                    evening_begin,
                    evening_end,
                    employee,
                    existing_signature,
                )

                if morning_status or afternoon_status or evening_status:
                    messages.info(request, 'Updated shifts.')

        another_naming_increment += 1
        start_date += timezone.timedelta(days=1)
    submit = True
    if all_fields_valid:
        if shifts or is_admin:
            submit = False

    user_group = request.user.groups.all()

    # Handle for non-post request.
    return render(request, 'success_center_timesheets/edit_timesheet.html', {

        'forms_in_pay_period': forms_in_pay_period,
        'success_url': success_url,
        'shifts': shifts,
        'submit': submit,
        'employee': employee,
        'existing_signature': existing_signature,
        'pay_period': pay_period,
        'employee_data': employee_data,
        'user_group': user_group,
    })


#  this function alters HTML 'name' element
#  we are using this to make sure that the data we get from form is unique for each day
def renaming_for_uniqueness(passed_form, id_integer):
    passed_form.fields['morning_begin_{0}'.format(id_integer)] = passed_form.fields['morning_begin']
    del passed_form.fields['morning_begin']
    passed_form.fields['morning_end_{0}'.format(id_integer)] = passed_form.fields['morning_end']
    del passed_form.fields['morning_end']

    passed_form.fields['afternoon_begin_{0}'.format(id_integer)] = passed_form.fields['afternoon_begin']
    del passed_form.fields['afternoon_begin']
    passed_form.fields['afternoon_end_{0}'.format(id_integer)] = passed_form.fields['afternoon_end']
    del passed_form.fields['afternoon_end']

    passed_form.fields['evening_begin_{0}'.format(id_integer)] = passed_form.fields['evening_begin']
    del passed_form.fields['evening_begin']
    passed_form.fields['evening_end_{0}'.format(id_integer)] = passed_form.fields['evening_end']
    del passed_form.fields['evening_end']


def calculate_form_shift_data(pay_period, shifts):
    """
    Creates data structure of all shift data for given shift set. Data is organized by day.

    Note: The "form_data" variable is formatted such that it can be passed into the form directly, to pre-populate form
    fields.
    """
    start_date = pay_period.date_start
    end_date = pay_period.date_end
    form_data = []

    # Loop through all dates in PayPeriod range, starting with start of pay period.
    curr_date = start_date
    index_for_renaming = 0
    while curr_date <= end_date:
        # Get all shifts for current day. Because of presets, we simply check the clock_in value.
        day_shifts = shifts.filter(clock_in__date=curr_date)

        # Format day_shifts if empty. Puts in correct format for data structure, later on.
        if len(day_shifts) == 0:
            day_shifts = None

        # Set default form field values.
        morning_begin = models.TimesheetShift.INT_NULL_TIME
        morning_end = models.TimesheetShift.INT_NULL_TIME
        afternoon_begin = models.TimesheetShift.INT_NULL_TIME
        afternoon_end = models.TimesheetShift.INT_NULL_TIME
        evening_begin = models.TimesheetShift.INT_NULL_TIME
        evening_end = models.TimesheetShift.INT_NULL_TIME

        # Check if any shifts found for day.
        if day_shifts:
            # Shifts were found for day. Format return data accordingly.

            # Start by calculating respective morning/afternoon/evening values.
            local_timezone = pytz.timezone('America/Detroit')
            earliest_morning_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(curr_date, forms.TimeSheetDayForm.MORNING_EARLIEST_STR.upper()),
                '%Y-%m-%d %I:%M %p',
            ))
            latest_morning_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(curr_date, forms.TimeSheetDayForm.MORNING_LATEST_STR),
                '%Y-%m-%d %I:%M %p',
            ))
            earliest_afternoon_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(curr_date, forms.TimeSheetDayForm.AFTERNOON_EARLIEST_STR.upper()),
                '%Y-%m-%d %I:%M %p',
            ))
            latest_afternoon_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(curr_date, forms.TimeSheetDayForm.AFTERNOON_LATEST_STR.upper()),
                '%Y-%m-%d %I:%M %p',
            ))
            earliest_evening_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(curr_date, forms.TimeSheetDayForm.EVENING_EARLIEST_STR.upper()),
                '%Y-%m-%d %I:%M %p',
            ))
            latest_evening_datetime = local_timezone.localize(timezone.datetime.strptime(
                '{0} {1}'.format(
                    curr_date + timezone.timedelta(days=1),
                    forms.TimeSheetDayForm.EVENING_LATEST_STR.upper()
                ),
                '%Y-%m-%d %I:%M %p',
            ))

            # Handle each shift found for current date.
            # Once again, because of presets, we can safely check only clock_in values.
            for shift in day_shifts:
                # Convert shift values to localtime, for easier "to string" logic.
                clock_in = shift.clock_in.astimezone(local_timezone)
                clock_out = shift.clock_out.astimezone(local_timezone)

                # Check if morning shift.
                if earliest_morning_datetime <= clock_in < latest_morning_datetime:
                    # Is morning shift. Update accordingly.
                    morning_begin = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_in.strftime('%-I:%M %p').lower(),
                    )
                    morning_end = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_out.strftime('%-I:%M %p').lower(),
                    )

                # Check if afternoon shift.
                elif earliest_afternoon_datetime <= clock_in < latest_afternoon_datetime:
                    # Is afternoon shift. Update accordingly.
                    afternoon_begin = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_in.strftime('%-I:%M %p').lower(),
                    )
                    afternoon_end = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_out.strftime('%-I:%M %p').lower(),
                    )

                # Check if evening shift.
                elif earliest_evening_datetime <= clock_in < latest_evening_datetime:
                    # Is evening shift. Update accordingly.
                    evening_begin = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_in.strftime('%-I:%M %p').lower(),
                    )
                    evening_end = models.TimesheetShift.get_preset_time_int_from_str(
                        clock_out.strftime('%-I:%M %p').lower(),
                    )

                else:
                    raise ValueError('Unhandled shift time: {0}'.format(shift))
        # # Get Signature model
        # signature_queryset = shifts.values_list('signature', flat=True)
        # for s in signature_queryset:
        #     existing_signature = s
        form_data.append({
            'date': curr_date,
            'shifts': day_shifts,
            'form_data': {
                'morning_begin_{0}'.format(index_for_renaming): morning_begin,
                'morning_end_{0}'.format(index_for_renaming): morning_end,
                'afternoon_begin_{0}'.format(index_for_renaming): afternoon_begin,
                'afternoon_end_{0}'.format(index_for_renaming): afternoon_end,
                'evening_begin_{0}'.format(index_for_renaming): evening_begin,
                'evening_end_{0}'.format(index_for_renaming): evening_end,

            }
        })

        index_for_renaming += 1
        # Increment current date to next day.
        curr_date = curr_date + timezone.timedelta(days=1)

    # Return calculated form data.
    return form_data


def save_morning_data(request, date, morning_begin, morning_end, employee, existing_signature):
    """
    Given a date and shift start/end times, will update the corresponding Shift model, or create if doesn't exist.
    :param request: Page request data.
    :param date: Date of shift.
    :param morning_begin: Start time of shift.
    :param morning_end: End time of shift.
    :param employee: step employee
    :param existing_signature: check if there is an existing signature for the corresponding timesheet
    :return: Bool indicating if model was created or updated. False if not.
    """
    # Check that clock times aren't empty. This occurs when they're set to 0.
    if (
        morning_begin != models.TimesheetShift.INT_NULL_TIME
        and morning_end != models.TimesheetShift.INT_NULL_TIME
    ):
        # Values are populated.

        # Get general morning values.
        local_timezone = pytz.timezone('America/Detroit')
        earliest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, forms.TimeSheetDayForm.MORNING_EARLIEST_STR.upper()),
            '%Y-%m-%d %I:%M %p',
        ))
        latest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, forms.TimeSheetDayForm.MORNING_LATEST_STR.upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process morning_begin value.
        begin_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, models.TimesheetShift.get_preset_time_str_from_int(morning_begin).upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process morning_end value.
        end_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, models.TimesheetShift.get_preset_time_str_from_int(morning_end).upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Get corresponding PayPeriod model.
        pay_period = models.PayPeriod.get_payperiod(date)
        new_signature = request.POST.get('signature')

        # Attempt to get corresponding shift model.
        try:
            shift = models.TimesheetShift.objects.get(
                pay_period=pay_period,
                employee=employee,
                clock_in__gte=earliest_datetime,
                clock_out__lte=latest_datetime,
                signature=existing_signature,
            )

            # Get UTC format for model comparison.
            utc_begin = begin_datetime.astimezone(pytz.utc)
            utc_end = end_datetime.astimezone(pytz.utc)

            # Found corresponding model. Check if matches clock times exactly.
            if shift.clock_in != utc_begin or shift.clock_out != utc_end:
                # Not exact match. Update model with new values.
                shift.clock_in = begin_datetime
                shift.clock_out = end_datetime
                shift.save()

                # Return True.
                return True

        except models.TimesheetShift.DoesNotExist:
            if existing_signature:
                # check if signature already exists
                # Note we try for ANY existing shift models that fall within the morning slot of this date.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=existing_signature,
                )
            elif new_signature:
                # check if new signature exists
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=new_signature,
                )
            else:
                # fallback to default
                # Shift does not yet exist. Create it.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=1 if None else request.POST.get('signature'),
                )
            # Model created. Return True.
            return True

    # Model was not created or updated. Return False.
    return False


def save_afternoon_data(request, date, afternoon_begin, afternoon_end, employee, existing_signature):
    """
    Given a date and shift start/end times, will update the corresponding Shift model, or create if doesn't exist.
    :param request: Page request data.
    :param date: Date of shift.
    :param afternoon_begin: Start time of shift.
    :param afternoon_end: End time of shift.
    :param employee: step employee
    :param existing_signature: check if there is an existing signature for the corresponding timesheet
    :return: Bool indicating if model was created or updated. False if not.
    """
    # Check that clock times aren't empty. This occurs when they're set to 0.
    if afternoon_begin != models.TimesheetShift.INT_NULL_TIME and afternoon_end != models.TimesheetShift.INT_NULL_TIME:
        # Values are populated.

        # Get general afternoon values.
        local_timezone = pytz.timezone('America/Detroit')
        earliest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, forms.TimeSheetDayForm.AFTERNOON_EARLIEST_STR.upper()),
            '%Y-%m-%d %I:%M %p',
        ))
        latest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, forms.TimeSheetDayForm.AFTERNOON_LATEST_STR.upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process afternoon_begin value.
        begin_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, models.TimesheetShift.get_preset_time_str_from_int(afternoon_begin).upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process afternoon_end value.
        end_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, models.TimesheetShift.get_preset_time_str_from_int(afternoon_end).upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Get corresponding PayPeriod model.
        pay_period = models.PayPeriod.get_payperiod(date)
        new_signature = request.POST.get('signature')
        # Attempt to get corresponding shift model.
        try:
            # CHECK IF WE HAVE AN EXISTING SIGNATURE
            # Note we try for ANY existing shift models that fall within the afternoon slot of this date.
            shift = models.TimesheetShift.objects.get(
                pay_period=pay_period,
                employee=employee,
                clock_in__gte=earliest_datetime,
                clock_out__lte=latest_datetime,
                signature=existing_signature,
            )
            # Get UTC format for model comparison.
            utc_begin = begin_datetime.astimezone(pytz.utc)
            utc_end = end_datetime.astimezone(pytz.utc)

            # Found corresponding model. Check if matches clock times exactly.
            if shift.clock_in != utc_begin or shift.clock_out != utc_end:
                # Not exact match. Update model with new values.
                shift.clock_in = begin_datetime
                shift.clock_out = end_datetime
                shift.save()

                # Model Updated. Return True.
                return True

        except models.TimesheetShift.DoesNotExist:
            # Check if signature is available in form data
            if new_signature:
                # Shift does not yet exist. Create it.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=new_signature,
                )
            elif existing_signature:

                # Shift does not yet exist. Create it.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=existing_signature,
                )
            else:
                # fall back to default 1
                # Shift does not yet exist. Create it.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=1 if None else request.POST.get('signature'),
                )

            # Model created. Return True.
            return True

    # Model was not created. Return False.
    return False


def save_evening_data(request, date, evening_begin, evening_end, employee, existing_signature):
    """
    Given a date and shift start/end times, will update the corresponding Shift model, or create if doesn't exist.
    :param request: Page request data.
    :param date: Date of shift.
    :param evening_begin: Start time of shift.
    :param evening_end: End time of shift.
    :param employee :
    :return: Bool indicating if model was created or updated. False if not.
    """
    # Check that clock times aren't empty. This occurs when they're set to 0.
    if evening_begin != models.TimesheetShift.INT_NULL_TIME and evening_end != models.TimesheetShift.INT_NULL_TIME:
        # Values are populated.

        # Get general evening values.
        local_timezone = pytz.timezone('America/Detroit')
        earliest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, forms.TimeSheetDayForm.EVENING_EARLIEST_STR.upper()),
            '%Y-%m-%d %I:%M %p',
        ))
        latest_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(
                date + timezone.timedelta(days=1),
                forms.TimeSheetDayForm.EVENING_LATEST_STR.upper(),
            ),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process evening_begin value.
        begin_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(date, models.TimesheetShift.get_preset_time_str_from_int(evening_begin).upper()),
            '%Y-%m-%d %I:%M %p',
        ))

        # Process evening_end value.
        end_str = models.TimesheetShift.get_preset_time_str_from_int(evening_end).upper()
        if end_str[-2:] == 'AM':
            end_date = date + timezone.timedelta(days=1)
        else:
            end_date = date
        end_datetime = local_timezone.localize(timezone.datetime.strptime(
            '{0} {1}'.format(end_date, end_str),
            '%Y-%m-%d %I:%M %p',
        ))

        # Get corresponding PayPeriod model.
        pay_period = models.PayPeriod.get_payperiod(date)
        new_signature = request.POST.get('signature')

        # Attempt to get corresponding shift model.
        try:
            shift = models.TimesheetShift.objects.get(
                pay_period=pay_period,
                employee=employee,
                clock_in__gte=earliest_datetime,
                clock_out__lte=latest_datetime,
                signature=existing_signature,
            )

            # Get UTC format for model comparison.
            utc_begin = begin_datetime.astimezone(pytz.utc)
            utc_end = end_datetime.astimezone(pytz.utc)

            # Found corresponding model. Check if matches clock times exactly.
            if shift.clock_in != utc_begin or shift.clock_out != utc_end:
                # Not exact match. Update model with new values.
                shift.clock_in = begin_datetime
                shift.clock_out = end_datetime
                shift.save()

                # Model Updated. Return True.
                return True

        except models.TimesheetShift.DoesNotExist:
            # check if signature already exists
            if existing_signature:
                # Note we try for ANY existing shift models that fall within the evening slot of this date.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=existing_signature,
                )
            elif new_signature:
                # check if new signature in form data
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=new_signature,
                )
            else:
                # fall back to default
                # Shift does not yet exist. Create it.
                models.TimesheetShift.objects.create(
                    pay_period=pay_period,
                    employee=employee,
                    clock_in=begin_datetime,
                    clock_out=end_datetime,
                    signature=request.POST.get('signature'),
                )

            # Model created. Return True.
            return True

    # Model was not created. Return False.
    return False
