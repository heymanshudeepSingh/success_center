"""
Views for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from rest_framework import viewsets, permissions

# User Class Imports.
from . import forms, models
from .rest import filters, serializers
from settings import logging as init_logging
from cae_tools.utils import test_mass_email as utils_test_mass_email
from cae_tools.utils import test_single_email as utils_test_single_email


# Import logger.
logger = init_logging.get_logger(__name__)


# CAE Center specific User Group names.
cae_employee_groups = [
    'CAE Director',
    'CAE Building Coordinator',
    'CAE Attendant',
    'CAE Admin',
    'CAE Programmer',
]

# STEP specific User Group names.
step_employee_groups = [
    'STEP Admin',
    'STEP Employee',
]


def login(request, *args, **kwargs):
    """
    Modified login view for "remember me" checkbox.
    Once processed, passes login to default auth views.
    """
    # Check if user is logged in. If so, automatically redirect to index page.
    if request.user.is_authenticated:
        return redirect('cae_home:login_redirect')

    # User not logged in. Check if request is POST.
    if request.method == 'POST':

        # See if remember_me box is checked.
        if request.POST.get('remember_me', None):
            # Remember me is checked. Hold user session for 604800 seconds (7 days).
            # Set to 0 to hold indefinitely (not recommended).
            request.session.set_expiry(604800)
        else:
            # Remember me is not checked. Set session to time out in 3600 seconds (1 hour).
            request.session.set_expiry(3600)

    return auth_views.LoginView.as_view(authentication_form=forms.AuthenticationForm, **kwargs)(request)


def login_redirect(request):
    """
    Determines redirect url after user login. Varies based on user group permissions.
    """
    if not request.user.is_authenticated:
        return redirect('cae_home:login')
    else:
        user_groups = request.user.groups.values_list('name', flat=True)

        # Check if programmer and development mode.
        if settings.DEV_URLS:
            if 'CAE Programmer' in user_groups:
                return redirect('cae_home:index')

        # Check if CAE Center employee.
        if  'cae_web' in settings.INSTALLED_CAE_PROJECTS:
            for cae_group in cae_employee_groups:
                if cae_group in user_groups:
                    return redirect('cae_web_core:index')

        # Check if STEP (Success Center) employee.
        if 'success_center' in settings.INSTALLED_CAE_PROJECTS:
            for step_group in step_employee_groups:
                if step_group in user_groups:
                    return redirect('success_center:index')

        # Unknown user group.
        exception = 'Server did not recognize login user\'s ({0}) group. Please contact the CAE Center.'.format(
            request.user,
        )
        logger.error(exception)
        return TemplateResponse(request, 'cae_home/errors/404.html', {
            'error_message': exception,
        },
            status=404,
        )


def logout(request):
    """
    Determines redirect url after user logout. Varies based on user group permissions.
    Then passes this to Django's standard logout function to handle the rest.
    """
    if not request.user.is_authenticated:
        return redirect('cae_home:login')
    else:
        user_groups = request.user.groups.values_list('name', flat=True)

        # Fallback url.
        logout_redirect_url = redirect('cae_home:login')
        url_set = False

        # Check if programmer and development mode.
        if settings.DEV_URLS:
            if 'CAE Programmer' in user_groups:
                logout_redirect_url = redirect('cae_home:index')
                url_set = True

        # Check if CAE Center employee.
        if not url_set and 'cae_web' in settings.INSTALLED_CAE_PROJECTS:
            for cae_group in cae_employee_groups:
                if cae_group in user_groups:
                    logout_redirect_url = redirect('cae_web_core:index')
                    url_set = True

        # Check if STEP (Success Center) employee.
        if not url_set and 'success_center' in settings.INSTALLED_CAE_PROJECTS:
            for step_group in step_employee_groups:
                if step_group in user_groups:
                    logout_redirect_url = redirect('success_center_core:index')
                    url_set = True

        logger.auth_info('{0}: Logging user out.'.format(request.user))

        # Call Django's standard logout function.
        return auth_views.LogoutView.as_view(next_page=logout_redirect_url.url)(request)


def info_schedules(request):
    """
    Temporary page to publicly display schedules of users.
    """
    return TemplateResponse(request, 'cae_home/info_schedules.html', {})


def info_servers(request):
    """
    Temporary page to publicly display servers maintained by admins.
    """
    return TemplateResponse(request, 'cae_home/info_servers.html', {
        'contact_mandroo': 'Andrew Barnes<br>znd7233@wmich.edu',
        'contact_hussein': 'Hussein Sheakh<br>hbn2774@wmich.edu',
        'contact_kira': 'Kira Hamelink<br>kdr1002@wmich.edu',
        'contact_musaab': 'Musaab Yousif<br>myn8219@wmich.edu',
        'contact_shagun': 'Shagun Choudhary<br>sgk8005@wmich.edu',
        'contact_phillip': 'Phillip Varner<br>pgs8661@wmich.edu',
    })


def info_software(request):
    """
    Temporary page to publicly display software maintained by programmers.
    """
    return TemplateResponse(request, 'cae_home/info_software.html', {
        'contact_brandon': 'Brandon Rodriguez<br>bfp5870@wmich.edu',
        'contact_jesse': 'Jesse Meachum<br>jdc4014@wmich.edu',
        'contact_singh': 'Simar Singh<br>hfv6838@wmich.edu'
    })


@login_required
def helpful_resources(request):
    """
    "Useful links" page for CAE Center employees.
    """
    return TemplateResponse(request, 'cae_home/helpful_resources.html', {})


@login_required
def user_edit(request, slug):
    """
    Edit view for a single user.


    Note that multiple users may have the same address. Or after years pass, a new user may use a previous user's
    address. Thus, on update, first try to get an address with equivalent values. Only on failure do we validate and
    save form data.

    Furthermore, if two users share an address, we don't want one user moving and updating their address
    to also change the second user's address. Thus, if validating and saving form data, force a new instance of the
    model to be created (by doing commit=False and setting pk to None, before saving) rather than updating the existing,
    shared model.
    """
    # Pull models from database.
    user_intermediary = get_object_or_404(models.UserIntermediary, slug=slug)
    user = user_intermediary.user
    user_profile = user_intermediary.profile
    address = user_profile.address

    form_list = []
    form = forms.UserModelForm(instance=user)
    form.display_name = 'General Info'
    form_list.append(form)

    form = forms.ProfileModelForm_OnlyPhone(instance=user_profile)
    form.display_name = 'Phone Number'
    form_list.append(form)

    form = forms.AddressModelForm(instance=address)
    form.display_name = 'Address'
    # form_list.append(form)

    form = forms.ProfileModelForm_OnlySiteOptions(instance=user_profile)
    form.display_name = 'Site Settings'
    form_list.append(form)

    # Check if request is post.
    if request.method == 'POST':
        valid_forms = True
        form_list = []

        # Handle for disabled field.
        POST = request.POST.copy()
        POST['username'] = user.username
        form = forms.UserModelForm(instance=user, data=POST)
        form.name = 'UserForm'
        form.display_name = 'General Info'
        form_list.append(form)

        form = forms.ProfileModelForm_OnlyPhone(instance=user_profile, data=request.POST)
        form.name = 'PhoneNumberForm'
        form.display_name = 'Phone Number'
        form_list.append(form)

        form = forms.AddressModelForm(instance=address, data=request.POST)
        form.name = 'AddressForm'
        form.display_name = 'Address'
        # form_list.append(form)

        form = forms.ProfileModelForm_OnlySiteOptions(instance=user_profile, data=request.POST)
        form.name = 'SiteSettingsForm'
        form.display_name = 'Site Settings'
        form_list.append(form)

        # Check that all forms are valid.
        for form in form_list:
            # Validate address form.
            if form.name == 'AddressForm':
                address = None
                try:
                    # Attempt to find existing model. Helps prevent unique_required validation errors.
                    address = models.Address.objects.get(
                        street=request.POST['street'],
                        optional_street=request.POST['optional_street'],
                        city=request.POST['city'],
                        state=request.POST['state'],
                        zip=request.POST['zip'],
                    )
                except ObjectDoesNotExist:
                    # Could not find model. Attempt to validate form.
                    if not form.is_valid():
                        valid_forms = False

            # Validate all other forms.
            elif not form.is_valid():
                valid_forms = False

        if valid_forms:
            # All forms came back as valid. Save.
            for form in form_list:
                if form.name == 'AddressForm':
                    if not address:
                        address = form.save(commit=False)
                        address.pk = None
                        address.save()
                elif form.name == 'SiteSettingsForm':
                    profile = form.save(commit=False)
                    profile.address = address
                    profile.save()
                else:
                    form.save()

            # Render response for user.
            messages.success(request, 'Successfully updated user {0}.'.format(user))
            return HttpResponseRedirect(reverse('cae_home:user_edit', args=(user.username,)))
        else:
            # One or more forms failed to validate.
            messages.warning(request, 'Failed to update user info.')

    # Handle for non-post request.
    return TemplateResponse(request, 'cae_home/user_edit.html', {
        'forms': form_list,
        'user_model': user,
        'profile': user_profile,
        'address': address,
    })


#region DjangoRest Views

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    DjangoRest views for department model.
    """
    queryset = models.Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer
    filter_class = filters.DepartmentFilter

#endregion DjangoRest Views


#region Debug/Development Views

def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'cae_home/index.html', {})
    else:
        raise Http404()


def internal_dev_index(request):
    """
    The internal (cae home) development index page.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return redirect('cae_tools:css_examples')
    else:
        raise Http404()


def external_dev_index(request):
    """
    The external (wmu clone) index page.
    Displays front-end information/examples specific to the external site layout and stylings.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'wmu_home/index.html', {})
    else:
        raise Http404()


def test_single_email(request):
    """
    Tests sending of email with "send_mail" function.
    This function is acceptable when a single email is to be sent.
    """
    if settings.DEBUG:
        # Run test.
        utils_test_single_email()

        # Redirect to home.
        return redirect('cae_home:index')
    else:
        raise Http404()


def test_mass_email(request):
    """
    Tests sending of email with "send_mass_mail" function.
    This function is far more efficient when sending multiple emails. We are likely to use this as the default.
    Note that, despite the name, send_mass_email can still send a single email, if desired.
    """
    if settings.DEBUG:
        # Run test.
        utils_test_mass_email()

        # Redirect to home.
        return redirect('cae_home:index')
    else:
        raise Http404()

#endregion Debug/Development Views
