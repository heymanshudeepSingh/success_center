"""
Form views for CAE Home app.
"""

# System Imports.
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView

# User Imports.
from cae_home import forms, models
from cae_home.decorators import group_required
from cae_home.utils import get_or_create_login_user_model
from workspace import logging as init_logging


# Initialize logging.
logger = init_logging.get_logger(__name__)


@login_required
def user_details(request):
    current_user = request.user
    user_profile = current_user.profile
    return TemplateResponse(request, "cae_home/user_details.html", {
        "current_user": current_user,
        "user_profile": user_profile
    })


class UserDetails(TemplateView):
    template_name = 'cae_home/user_details.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Grab variables.
        current_user = self.request.user
        user_profile = current_user.profile
        user_groups = current_user.groups.all().values_list('name', flat=True)
        # Check if user has one or more of "CAE admin groups". If so, display additional links.
        is_cae_admin = False
        is_cae_user = False
        for group in settings.CAE_ADMIN_GROUPS:
            if group in user_groups:
                is_cae_admin = True
        # Also display if is superuser.
        if current_user.is_superuser:
            is_cae_admin = True
        is_cae_user = is_cae_admin
        # Also check if cae user.
        if not is_cae_user:
            for group in settings.CAE_CENTER_GROUPS:
                if group in user_groups:
                    is_cae_user = True

        # Pass values to template.
        context.update({
            'current_user': current_user,
            'user_profile': user_profile,
            'user_groups': user_groups,
            'is_cae_admin': is_cae_admin,
            'is_cae_user': is_cae_user,
        })
        return context


@login_required
@group_required(settings.CAE_ADMIN_GROUPS)
def manage_cae_users(request):
    """
    For adding/managing new CAE Center users.
    """
    # Initialize form.
    form = forms.CaeCenterUserForm()

    # Handle for user-submitted data.
    if request.POST:

        # Update form.
        form = forms.CaeCenterUserForm(request.POST)

        # Validate form.
        if form.is_valid():
            # Form is valid. Proceed.
            user_id = form.cleaned_data['user_id']
            group_set = form.cleaned_data['groups']

            user_id = str(user_id).split(', ')[0]

            # Get user data from provided value.
            # Note that this acts as a second level of validation, against LDAP.
            # We get None if LDAP connection is present and user data was invalid.
            # We get TemplateResponse if LDAP connection is not present, and Django database could not find user.
            # We get a user model if user was found.
            user = get_or_create_login_user_model(request, user_id)
            failed_to_find_user_msg = 'Failed to find user with BroncoNet/Winno of "{0}".'.format(user_id)
            if user is None:
                # LDAP connection works but invalid value.
                messages.warning(request, failed_to_find_user_msg)
            elif isinstance(user, TemplateResponse):
                # User does not found in Django database and LDAP not set up.
                messages.warning(request, failed_to_find_user_msg)
                messages.error(request, 'LDAP connection does not appear to be set up. Could not check against LDAP.')
            else:
                # User found.
                orig_user_groups = user.groups.all()

                # Add all corresponding groups provided in form.
                group_set = Group.objects.filter(name__in=group_set)
                for group in group_set:
                    user.groups.add(group)
                messages.success(request, 'Updated CAE user groups for {0} {1}.'.format(
                    user.first_name,
                    user.last_name,
                ))

                # Remove groups not in form.
                for group in orig_user_groups:
                    if group not in group_set:
                        user.groups.remove(group)

            # Redirect to committee management page.
            return redirect(reverse('cae_home:manage_cae_users'))

    # Render response.
    return TemplateResponse(request, 'cae_home/manage_cae_users.html', {
        'form': form,
    })


@login_required
def user_edit(request):
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
    user = request.user
    user_intermediary = get_object_or_404(models.UserIntermediary, slug=user.username)
    user = user_intermediary.user
    user_profile = user_intermediary.profile
    address = user_profile.address
    user_groups = request.user.groups.values_list('name', flat=True)

    form_list = []
    form = forms.UserModelForm(instance=user)
    form.display_name = 'General Info'
    form.additional_link = 'cae_home:user_change_password'
    form.additional_link_text = "Change Password?"
    # form.slug = user.username
    form_list.append(form)

    form = forms.ProfileModelForm_OnlyPhone(instance=user_profile)
    form.display_name = 'Phone Number'
    form_list.append(form)

    form = forms.AddressModelForm(instance=address)
    form.display_name = 'Address'
    # form_list.append(form)

    if 'CAE Admin GA' in user_groups or 'CAE Programmer GA' in user_groups:
        form = forms.ProfileModelForm_OnlySiteOptionsGA(instance=user_profile)
    else:
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

        if 'CAE Admin GA' in user_groups or 'CAE Programmer GA' in user_groups:
            form = forms.ProfileModelForm_OnlySiteOptionsGA(instance=user_profile, data=request.POST)
        else:
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


@login_required
@group_required(settings.CAE_CENTER_GROUPS)
def change_password(request):
    """
    Allows a user to update their own password to a new value.
    """
    ldap_not_set_up = False

    # Check if ldap settings are defined.
    if settings.CAE_LDAP['login_dn'] == '':
        messages.error(request, 'Can\'t connect to Ldap server. :( \n Are project LDAP settings setup?')
        ldap_not_set_up = True

    # Initialize SimpleLdapLibrary.
    try:
        from workspace.ldap_backends import simple_ldap_lib
        ldap_lib = simple_ldap_lib.SimpleLdap()
    except (AttributeError, ModuleNotFoundError):
        messages.error(request, 'Can\'t connect to Ldap server. :( \n Is the SimpleLdapLib installed?')
        ldap_not_set_up = True

    # Initialize form.
    form = forms.ChangePasswordCustomForm()

    # Handle for submission.
    if not ldap_not_set_up and request.method == 'POST':
        form = forms.ChangePasswordCustomForm(request.POST)

        # Validate form.
        if form.is_valid():
            user_id = request.user

            # Pull ldap values from settings.
            host = settings.CAE_LDAP['host']
            admin_dn = settings.CAE_LDAP['admin_dn']
            admin_password = settings.CAE_LDAP['admin_password']
            new_password = form.cleaned_data['new_password']
            search_base = settings.CAE_LDAP['user_search_base']
            current_password = form.cleaned_data['current_password']

            # Note: "ldap password not found" error will be thrown if Ldap-utils is not installed.
            try:
                results = ldap_lib.password_reset(
                    user_id,
                    current_password,
                    new_password,
                    host=host,
                    dn=admin_dn,
                    password=admin_password,
                    search_base=search_base,
                )
                # Check status.
                if results[0] is True:
                    messages.success(request, 'Password successfully changed.')
                    return redirect(reverse_lazy('cae_home:user_details'))
                else:
                    messages.error(request, results[1])

            except ConnectionError:
                messages.error(request, 'Error connecting. Unable to reset password.')

    # Render response.
    return TemplateResponse(request, 'cae_home/change_password.html', {
        'form': form,
        'button_text': 'Reset',
    })
