"""
Views for Success Center Core app.
"""

# System Imports.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, UpdateView

# User Imports.
from . import forms, models
from .filter import StudentUsageFilter
from cae_home import models as cae_home_models
from cae_home.decorators import group_required
from cae_home.utils import get_or_create_wmu_user_model, get_or_create_login_user_model
from workspace import logging as init_logging

# Initialize logger.
logger = init_logging.get_logger(__name__)

# Set of STEP location groups
#
# This is to prevent one locations admins from editing another locations data
# IF ANY OF THESE CHANGE THE 'cae_home/fixtures/production_models/auth_groups.json'
# file may need to change
#
# TODO:
# This should be a relation in the TutorLocations table, the problem with adding
# a table is that a user only has the `Group` connected, location is not part of
# that model so it remains imperfect (if I'm STEP SSC am I location Floyd or Eldridge?)
STEP_GROUP = [
    'STEP Bronco Study Zone',
    'STEP Statistics Tutoring',
    'STEP SSC - Floyd',
    'STEP SSC - Eldridge',
    'STEP SSC - Event',
]

STEP_GROUP_MAP = {
    'STEP Bronco Study Zone': ['Bronco Study Zone'],
    'STEP Statistics Tutoring': ['Statistics Tutoring'],
    'STEP SSC - Eldridge': ['SSC - Eldridge', 'STEP - Event'],
    'STEP SSC - Floyd': ['SSC - Floyd', 'STEP - Event'],
    'STEP SSC - Event': ['STEP - Event', 'SSC - Floyd', 'SSC - Eldridge'],
}

STEP_LOCATION_MAP = {
    'Bronco Study Zone': ['STEP Bronco Study Zone'],
    'Statistics Tutoring': ['STEP Statistics Tutoring'],
    'SSC - Eldridge': ['STEP SSC - Eldridge'],
    'SSC - Floyd': ['STEP SSC - Floyd'],
    'STEP - Event': ['STEP SSC - Event'],
}


def filter_students_by_location(request):
    # Check for existing usage for current student.
    loc_groups = request.user.groups.filter(name__in=STEP_GROUP)
    tut_locs = models.TutorLocations.objects.all()

    is_admin = request.user.groups.filter(name='STEP All Locations').exists()

    student_filter = None
    if len(loc_groups) > 0 and len(tut_locs) > 0 and not is_admin:
        # Any time we show student logs we want all SSC places to show
        STEP_GROUP_MAP['STEP SSC - Eldridge'].append('SSC - Floyd')
        STEP_GROUP_MAP['STEP SSC - Floyd'].append('SSC - Eldridge')

        student_filter = models.StudentUsageLog.objects.filter(
            check_out=None,
            location__in=models.TutorLocations.objects.filter(
                location_name__in=STEP_GROUP_MAP[loc_groups[0].name]
            ),
        )

        # Now remove them because we want it to track the actual location everywhere else
        # and not the both sites as one
        STEP_GROUP_MAP['STEP SSC - Eldridge'].remove('SSC - Floyd')
        STEP_GROUP_MAP['STEP SSC - Floyd'].remove('SSC - Eldridge')
    else:
        student_filter = models.StudentUsageLog.objects.filter(check_out=None)
    return student_filter

@method_decorator(group_required('STEP Admin', 'STEP Employee'), name='dispatch')
class Index(LoginRequiredMixin, FormView):
    """
    Index for success center.

    Displays all currently-checked-in students, as well as allows entering new student id's for checking in students.
    """
    template_name = 'success_center_core/index.html'
    context = {}
    form_class = forms.StudentLookupForm
    success_url = reverse_lazy('success_center_core:index')

    def dispatch(self, request, *args, **kwargs):
        """
        Before our main class logic, we check if student values were provided and the associated student exists.

        If it exists, we redirect to the "LogStudent" view, to either check the student in or out.
        If it does not exist, we call the original dispatch that proceeds to call the rest of the class logic.
        """
        # Check if we have a bronconet or winno in our session values.
        student_identifier = request.session.pop('cae_success_ctr__student_id', None)

        # Check if there was any identifier at all.
        if student_identifier is None:
            # No identifier. Check if this is a POST request from the LogStudent view.
            if 'check_in' in self.request.POST or 'check_out' in self.request.POST:
                return LogStudent.as_view()(self.request, student=self.request.POST['bronco_net'])
            # No POST value from LogStudent view. Proceed to the rest of this view.
            return super().dispatch(request, *args, **kwargs)
        else:
            # An identifier was present. Attempt to get student info from Django models or LDAP.
            student_model = get_or_create_wmu_user_model(self.request, student_identifier)

            # Check return value.
            if isinstance(student_model, TemplateResponse):
                # Associated Django model did not exist, and LDAP is not set up in local environment.
                messages.warning(
                    self.request,
                    'Failed to find student "{0}" and LDAP connection is not set up for local server.'.format(
                        student_identifier,
                    ),
                )
            elif student_model is not None:
                # Student model found. Redirect to detail view.
                # From https://stackoverflow.com/a/14957571
                return LogStudent.as_view()(self.request, student=student_model.bronco_net)

            # If we made it this far, then could not find student value, even after ldap request.
            messages.info(
                self.request,
                'Failed to find student "{0}". Did you type it correctly?'.format(student_identifier),
            )
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add additional context (variables) for template to display.
        """
        context = super().get_context_data(**kwargs)

        # Check for existing usage for current student.
        student_list = filter_students_by_location(self.request)

        # Get SuccessCtrProfile data.
        user_profile = self.request.user.userintermediary.profile
        try:
            success_ctr_profile = models.SuccessCtrProfile.objects.get(profile=user_profile)
        except models.SuccessCtrProfile.DoesNotExist:
            success_ctr_profile = models.SuccessCtrProfile.objects.create(profile=user_profile)

        checkin_location: str
        try:
            checkin_location = STEP_GROUP_MAP[
                self.request.user.groups.filter(name__in=STEP_GROUP).first().name
            ][0]
        except:
            checkin_location = success_ctr_profile.default_tutor_location

        # Display warning message if no checkin location is set for user.
        if checkin_location is None:
            messages.warning(
                self.request,
                'Tutor location not set. Please set in User Management (dropdown on top right of page).'
            )

        # Update template context.
        context.update({
            'student_list': student_list,
            'checkin_location': checkin_location,
        })

        return context

    def form_valid(self, form):
        student_identifier = form.cleaned_data['student_id']
        if len(student_identifier) > 10:
            student_identifier = student_identifier[1:10]
        # Attempt to get associated student model from provided form data.
        student_model = get_or_create_wmu_user_model(self.request, student_identifier)

        # Check return value.
        if isinstance(student_model, TemplateResponse):
            # Associated Django model did not exist, and LDAP is not set up in local environment.
            messages.warning(
                self.request,
                'Failed to find student "{0}" and LDAP connection is not set up for local server.'.format(
                    student_identifier,
                ),
            )
        elif student_model is not None:
            # Student model found.  Redirect to detail view.
            self.request.session['cae_success_ctr__student_id'] = student_model.bronco_net
            return redirect(reverse_lazy('success_center_core:index'))

        # If we made it this far, then could not find student value, even after ldap request.
        messages.info(
            self.request,
            'Failed to find student "{0}". Did you type it correctly?'.format(student_identifier),
        )
        return redirect(reverse_lazy('success_center_core:index'))


def student_checkout(request, bronco_net):
    """
    Check out student button
    """
    # Check for existing usage for current student.
    student = models.StudentUsageLog.objects.get(student__bronco_net=bronco_net, check_out=None)
    student.check_out = timezone.now()
    student.save()
    messages.success(request, f'Checked Out {student.student}')
    return HttpResponseRedirect('/success_center')


@method_decorator(group_required('STEP Admin', 'STEP Employee'), name='dispatch')
class LogStudent(LoginRequiredMixin, UpdateView):
    """
    Detail view for a specific student. Allows checking them in/out.

    When `cae_success_ctr__student_id` session variable is populated with the student's BroncoNet, then view will
    display check in/check out detail page.

    Otherwise, view expects a POST request. POST data should have student data, plus either "check_in" or "check_out"
    variable populated.
        * If "check_in" is in POST data, then view will attempt to check in the associated student model.
            * If student is already checked in, then will instead redirect to check in/check out detail view.
        * If "check_out" is in POST data, then view will attempt to check out the associated student model.
            * If student is not yet checked in, then will instead redirect to check in/check out detail view.
    """
    model = cae_home_models.WmuUser
    template_name = 'success_center_core/log_student_form.html'
    form_class = forms.StudentLogForm
    context_object_name = 'student'
    success_url = reverse_lazy('success_center_core:index')

    def get_object(self, queryset=None):
        """
        Get "main" model for our detail view.
        """
        self.student_id = self.kwargs['student']
        self.student = cae_home_models.WmuUser.objects.get(bronco_net=self.kwargs['student'])
        return self.student

    def get_context_data(self, **kwargs):
        """
        Add additional context (variables) for template to display.
        """
        context = super().get_context_data(**kwargs)

        # Check for existing usage for current student.
        try:
            student_usage = models.StudentUsageLog.objects.get(student=self.student, check_out=None)
        except models.StudentUsageLog.DoesNotExist:
            # Handle for provided student value not existing.
            student_usage = None
        except models.StudentUsageLog.MultipleObjectsReturned:
            # Handle for multiple instances returned for the same student value.
            student_usage_list = models.StudentUsageLog.objects.filter(
                student=self.student, check_out=None).order_by('check_in')

            # Loop through all entries in list and correct.
            old_usage_model = None
            for student_usage_model in student_usage_list:
                # Compare datetime value. If within a 10 min window, delete the more recent model.
                if old_usage_model is not None:
                    modified_usage_time = student_usage_model.check_in - timezone.timedelta(minutes=10)
                    if modified_usage_time <= old_usage_model.check_in:
                        # Within 10 minutes of each other. Delete newer one.
                        student_usage_model.delete()

                else:
                    # Save model for comparison in next loop.
                    old_usage_model = student_usage_model

            # Try to get student usage one more time. Should succeed now.
            student_usage = models.StudentUsageLog.objects.get(student=self.student, check_out=None)

        # Get full list of all students that are checked in.
        student_list = filter_students_by_location(self.request)

        context.update({
            'student_usage': student_usage,
            'student_list': student_list,
        })
        return context

    def form_valid(self, form):
        """
        We don't actually want to update our WmuUser (student) object.
        Instead, we take the student data and create a StudentUsageLog with it.
        """
        # Examine the POST request to see if check in or check out button was clicked.
        if 'check_in' in self.request.POST:
            # Check in button was clicked. Create new usage with now as the checkin time.

            # First verify that student did not already have an active usage, first.
            student_usage_list = models.StudentUsageLog.objects.filter(student=self.student, check_out=None)
            if len(student_usage_list) > 0:
                # Student had existing usage. Notify instead and redirect to checkout view.
                messages.warning(self.request, 'Student "{0}" is already checked in.'.format(self.student.bronco_net))
                self.request.session['cae_success_ctr__student_id'] = str(self.student.bronco_net)
                return redirect(reverse_lazy('success_center_core:index'))
            else:
                try:
                    loc = models.TutorLocations.objects.get(
                        location_name=STEP_GROUP_MAP[
                            self.request.user.groups.filter(name__in=STEP_GROUP)[0].name
                        ][0]
                    )
                    # Student did not already have existing usage. Create new one.
                    models.StudentUsageLog.objects.create(
                        student=self.student,
                        check_in=timezone.now(),
                        location=loc,
                    )
                except Exception:
                    messages.warning(
                        self.request,
                        'Failed to associate location with user',
                    )
        elif 'check_out' in self.request.POST:
            # Check out button was clicked. Update existing usage with now as checkout time.
            try:
                student_usage = models.StudentUsageLog.objects.get(
                    student=self.student, check_out=None
                )
                student_usage.check_out = timezone.now()
                student_usage.save()
            except models.StudentUsageLog.DoesNotExist:
                # Unable to find associated usage. Must have already been logged out.
                messages.warning(
                    self.request,
                    'Student "{0}" is already checked out.'.format(
                        self.student.bronco_net
                    ),
                )
                self.request.session['cae_success_ctr__student_id'] = str(
                    self.student.bronco_net
                )
                return redirect(reverse_lazy('success_center_core:index'))
        else:
            logger.error(
                'Student Success Center form view used, but could not determine button click type. '
                'POST data is: {0}'.format(self.request.POST)
            )

        # Return to original index view.
        return redirect(reverse_lazy('success_center_core:index'))


@login_required
@group_required('STEP Admin', 'STEP Employee')
def student_redirect(request, bronco_net):
    """
    Redirect view that adds a single session value.
    Used to allow direct links to student usage logs.
    """

    # Add student bronconet to local session.
    request.session['cae_success_ctr__student_id'] = str(bronco_net)

    # Instantly redirect to index. It will handle the logic from here.
    return redirect(reverse_lazy('success_center_core:index'))


@login_required
@group_required('STEP Admin')
def admin_index(request):
    """
    Landing page for admins - user admin, location admin
    """
    return TemplateResponse(request, 'success_center_core/admin_index.html', {})


# Admin panel for user admin
@login_required
@group_required('STEP Admin')
def user_admin_panel(request):
    """
    Student Success Center Admin Panel
    """
    # Check if employee is admin
    user_groups = request.user.groups.all()
    if not user_groups.filter(name__contains='STEP Admin').exists():
        raise PermissionError('You do not have permission to access this page.')

    # Filter out Admins and pk - for editing user | username/first_name for displaying purposes
    step_admins = cae_home_models.User.objects.filter(groups__name='STEP Admin', is_active=True).values(
        'pk',
        'first_name',
        'username'
    )

    step_employees = cae_home_models.User.objects.filter(groups__name='STEP Employee', is_active=True).values(
        'pk',
        'first_name',
        'username'
    )

    return TemplateResponse(request, 'success_center_core/user_admin_panel.html', {
        'step_admins': step_admins,
        'step_employees': step_employees,
    })


@login_required
@group_required('STEP Admin')
def user_admin_edit(request, pk=None):
    """
    Student_Success_Center Admin user edit view
    :param request: Just a general Django request
    :param pk: Pass in the admin user pk for editing

    """

    user_groups = request.user.groups.all()
    # employee is Step Employee and check if admin
    is_admin = user_groups.filter(name__contains='STEP Admin').exists()

    # This shouldn't be able to happen not sure why Simar had something like this???
    # (shouldn't happen because of @group_required decorator)
    if not is_admin:
        raise PermissionError('You do not have permission to access this page.')

    if pk:
        user = cae_home_models.User.objects.get(pk=pk)
        form = forms.EditUserForm(request.POST)
        form.initial['username'] = user.username
        form.initial['first_name'] = user.first_name
        form.initial['last_name'] = user.last_name
        form.initial['email'] = user.email

        # If a person is step_admin, they should have access to everything.
        if request.method == 'POST':
            if form.is_valid:
                form.save()

        delete_url = reverse('success_center_core:remove_from_step', args=(pk,))

        return TemplateResponse(request, 'success_center_core/user_admin_edit.html', {
            'user': user,
            'form': form,
            'user_group': user_groups,
            'delete_url': delete_url,

        })
    else:
        messages.error(request, 'Admin Pk not found!')
        return redirect('success_center_core:user_admin_panel')


# For adding new step_admin users
@login_required
@group_required('STEP Admin')
def add_new_student(request):
    # fetch all groups associated to a user
    user_groups = request.user.groups.all()

    # check if user is a STEP Admin
    if not user_groups.filter(name__contains='STEP Admin').exists():
        raise PermissionError('You do not have permission to access this page.')

    # initialize the form
    form = forms.AddNewStudent(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            bronco_net = form.cleaned_data.get('user')
            active = form.cleaned_data.get('is_active')
            # check/create new WMU user
            new_wmu_user = get_or_create_wmu_user_model(request, bronco_net)
            user = None
            if new_wmu_user:
                try:
                    # create Login User
                    user = get_or_create_login_user_model(request, bronco_net)
                except user.DoesNotExist:
                    messages.error(request, f'Unable to create new Log in user with Bronco net: {bronco_net}.')
                if user:
                    try:
                        # Add this new user to STEP Employee group
                        step_employee_group = Group.objects.get(name='STEP Employee')
                        step_employee_group.user_set.add(user)

                        user.is_active = active
                        user.save()

                        messages.success(request, f'Successfully created new STEP User {new_wmu_user}')
                    except UserWarning:
                        messages.error(request, f'Unable to create new STEP Employee {bronco_net}.')

            else:
                messages.error(request, f'Unable to create new STEP Employee {bronco_net}.')

    return TemplateResponse(request, 'success_center_core/add_new_employee.html', {
        'form': form,
    })


@login_required
@group_required('STEP Admin')
def change_step_employee_to_admin(request, pk):

    # Check if employee is admin
    user_groups = request.user.groups.all()
    is_admin = user_groups.filter(name__contains='STEP Admin').exists()

    if pk is not None:
        if not is_admin:
            raise PermissionError('You do not have permission to access this page.')

    # step admin "ADD new step admin" functionality
    try:
        # Check if user with the provided pk exists
        step_employee = cae_home_models.User.objects.get(pk=pk)
    except ModuleNotFoundError:
        raise 'Employee Not found.'

    # pull STEP admin group and add user to it
    step_admin_group = Group.objects.get(name='STEP Admin')
    step_admin_group.user_set.add(step_employee)

    # remove user from Step Employee group
    step_employee_group = Group.objects.get(name='STEP Employee')
    step_employee_group.user_set.remove(step_employee)
    messages.success(request, f'Changed {step_employee} to STEP Admin.')

    # redirect to user admin panel page
    return redirect('success_center_core:user_admin_panel')


@login_required
@group_required('STEP Admin')
def change_step_admin_to_employee(request, pk):
    # Changes user from Step Admin to Step Employee
    # User Admin Panel -> Edit Functionality
    try:
        # Check if user with the provided pk exists
        step_user = cae_home_models.User.objects.get(pk=pk)
    except ModuleNotFoundError:
        raise 'Employee Not found.'

    # pull STEP admin group and add user to it
    step_admin_group = Group.objects.get(name='STEP Admin')
    step_admin_group.user_set.remove(step_user)

    # remove user from Step Employee group
    step_employee_group = Group.objects.get(name='STEP Employee')
    step_employee_group.user_set.add(step_user)

    messages.success(request, f'Changed {step_user} to STEP Employee.')

    # redirect to user admin panel page
    return redirect('success_center_core:user_admin_panel')


@login_required
@group_required('STEP Admin')
def change_step_employee_location(request, pk):
    # Changes Admin/Employee location
    try:
        # Check if user with the provided pk exists
        step_employee = cae_home_models.User.objects.get(pk=pk)
        pass
    except ModuleNotFoundError:
        raise 'Employee Not found.'

    if 'location' in request.POST:
        try:
            # Remove this employee from all previous STEP groups
            # otherwise they collect
            for group in Group.objects.filter(name__in=STEP_GROUP):
                group.user_set.remove(step_employee)

            location = models.TutorLocations.objects.get(id=request.POST['location'])
            step_admin_group = Group.objects.get(
                name__in=STEP_LOCATION_MAP[location.location_name]
            )

            step_admin_group.user_set.add(step_employee)

            messages.success(
                request, f'Changed {step_employee} to {location} STEP Location.'
            )
        except Exception:
            messages.success(
                request, f'Failed to change {step_employee} to {location} STEP Location.'
            )
    # redirect to user admin panel page
    return redirect('success_center_core:user_admin_panel')


@login_required
@group_required('STEP Admin')
def remove_from_step(request, pk):
    # Removes USER from STEP Admin and STEP Employee groups
    try:
        # Check if user with the provided pk exists
        user = cae_home_models.User.objects.get(pk=pk)
    except ModuleNotFoundError:
        raise 'Employee Not found!'

    # pull STEP admin group and add user to it
    step_admin_group = Group.objects.get(name='STEP Admin')
    step_admin_group.user_set.remove(user)

    # remove user from Step Employee group
    step_employee_group = Group.objects.get(name='STEP Employee')
    step_employee_group.user_set.remove(user)

    # Provide user update message
    messages.warning(request, f'Removed {user} from STEP! ')
    # redirect to user admin panel page
    return redirect('success_center_core:user_admin_panel')


# For location admin panel
@login_required
@group_required('STEP Admin')
def location_admin_panel(request):
    """
    Student Success Center Location Admin Panel
    gets all current locations for the location panel page
    """

    # Check if employee is admin
    user_groups = request.user.groups.all()
    if not user_groups.filter(name__contains='STEP Admin').exists():
        raise PermissionError('You do not have permission to access this page.')

    step_admins = cae_home_models.User.objects.filter(
        groups__name='STEP Admin',
        is_active=True,
    ).values(
        'pk',
        'first_name',
        'username',
    )

    is_admin = False

    # Check if employee is admin
    user_groups = request.user.groups.all()
    if user_groups.filter(name__contains='STEP Admin'):
        is_admin = True

    locations = models.TutorLocations.objects.all().order_by('location_name')

    return TemplateResponse(request, 'success_center_core/location_admin_panel.html', {
        'locations': locations,
        'step_admin': step_admins,
        'is_admin': is_admin,

    })


@login_required
@group_required('STEP Admin')
def location_admin_edit(request, pk):
    """
    Student_Success_Center Location Admin edit view
    :param request: Just a general Django request
    :param pk: Pass in the admin user pk for editing

    we get form info of our current primary key and load it in to our form
    if we make changes to our form we check for valid iputs and call post
    to save changes.
    """

    # Check if employee is admin
    user_groups = request.user.groups.all()
    if not user_groups.filter(name__contains='STEP Admin').exists():
        raise PermissionError('You do not have permission to access this page.')

    if pk is not None:
        form_info = models.TutorLocations.objects.get(pk=pk)
        form = forms.EditLocationForm(request.POST or None, instance=form_info)
        # form.initial['date_created'] = form_info.date_created
        # form.initial['date_modified'] = form_info.date_modified
        if form.is_valid():
            form_info.date_modified = timezone.datetime.now()
            form.save()
            return redirect('success_center_core:location_admin_panel')

        return TemplateResponse(request, 'success_center_core/location_admin_edit.html', {
            'form': form,
            'form_info': form_info,
        })
    else:
        messages.error(request, 'Admin Pk not found!')
        return redirect('success_center_core:location_admin_panel')


@login_required
@group_required('STEP Admin')
def location_admin_add(request):
    """
    This view creates a new location and save it to our
    form when we call post
    """

    # Check if employee is admin
    user_groups = request.user.groups.all()
    if not user_groups.filter(name__contains='STEP Admin').exists():
        raise PermissionError('You do not have permission to access this page.')

    submitted = False
    if request.method == 'POST':
        form = forms.AddLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_center_core:location_admin_panel')
    else:
        form = forms.AddLocationForm()

    return TemplateResponse(request, 'success_center_core/location_admin_add.html', {
        'form': form,
        'submitted': submitted,
    })


@login_required
@group_required('STEP Admin')
def location_admin_delete(request, pk):
    # Check if employee is admin
    user_groups = request.user.groups.all()
    if user_groups.filter(name__contains='STEP Admin'):
        pass
    else:
        raise PermissionError('You do not have permission to access this page.')

    # This view deletes current selected location
    form_info = models.TutorLocations.objects.get(pk=pk)
    form_info.delete()
    return redirect('success_center_core:location_admin_panel')


@login_required
@group_required('STEP Admin')
def student_usage_panel(request):
    """
    Student Usage Data panel
    """

    # Filter out Admins and pk - for editing user | username/first_name for displaying purposes
    step_employee = cae_home_models.User.objects.filter(
        groups__name='STEP Employee',
        is_active=True,
    ).values(
        'pk',
        'username',
    )

    usage_filter = StudentUsageFilter(
        request.GET,
        queryset=filter_students_by_location(request)
    )

    students = usage_filter.qs.order_by('-check_in')
    paginator = Paginator(students, 50)

    page_count = request.GET.get('page')
    students = paginator.get_page(page_count if page_count else 1)

    return TemplateResponse(
        request,
        'success_center_core/student_usage_panel.html',
        {
            'students': students,
            'step_employee': step_employee,
            'usageFilter': usage_filter,
        },
    )


@login_required
@group_required('STEP Admin', 'STEP Employee')
def student_usage_edit(request, pk=None):
    if pk is not None:

        student_info = models.StudentUsageLog.objects.get(pk=pk)
        form = forms.StudentUsageForm(request.POST or None, instance=student_info)

        if form.is_valid():
            form.save()
            return redirect('success_center_core:student_usage_panel')

        return TemplateResponse(request, 'success_center_core/student_usage_edit.html', {
            'form': form,
            'student_info': student_info,
        })
    else:
        messages.error(request, 'Record not found!')
        return redirect('success_center_core:student_usage_panel')


@login_required
@group_required('STEP Admin', 'STEP Employee')
def student_approve(request, pk):
    """
    Approve Student time. Logic for approve button
    """
    # Get Student to approve
    student_info = models.StudentUsageLog.objects.get(pk=pk)
    student_info.approved = True
    # Save approved model
    student_info.save()

    # Return with a success message
    messages.success(request, f'Approved {student_info.student}')
    return redirect('success_center_core:student_usage_panel')


@login_required
@group_required('STEP Admin', 'STEP Employee')
def student_approve_ajax(request):
    """
    Nihal: New Approval Logic using checkboxes(Multiple Choice Field)
    """
    # Get Student to approve
    pk = request.POST.get("std_id")
    check_value = request.POST.get("check_value")

    if check_value == 'true':
        student_info = models.StudentUsageLog.objects.get(pk=pk)
        student_info.approved = True
        # Save approve information to model
        student_info.save()
    else:
        student_info = models.StudentUsageLog.objects.get(pk=pk)
        student_info.approved = False
        # Save approve information to model
        student_info.save()

    # Return with a success message in console saying its been approved
    messages.success(request, f'Approved {student_info.student}')
    return redirect('success_center_core:student_usage_panel')


@login_required
@group_required('STEP Admin', 'STEP Employee')
def student_approve_all(request):
    ids = request.POST.getlist('std_ids')
    stds = models.StudentUsageLog.objects.filter(pk__in=ids)
    for data in stds:
        data.approved = True
        data.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@group_required('STEP Admin')
def student_add(request):
    submitted = False
    if request.method == 'POST':
        form = forms.StudentUsageAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_center_core:student_usage_panel')

    else:
        form = forms.StudentUsageAddForm()

    return TemplateResponse(request, 'success_center_core/student_add.html', {
        'form': form,
        'submitted': submitted,
    })


@login_required
@group_required('STEP Admin')
def student_delete(request, pk):
    student_info = models.StudentUsageLog.objects.get(pk=pk)
    student_info.delete()
    return redirect('success_center_core:student_usage_panel')
