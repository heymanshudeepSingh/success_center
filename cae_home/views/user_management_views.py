"""
Form views for CAE Home app.
"""

# System Imports.
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView

# User Imports.
from cae_home import forms, models
from cae_home.decorators import group_required
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
        current_user = self.request.user
        user_profile = current_user.profile

        context.update({
            'current_user': current_user,
            'user_profile': user_profile,
        })
        return context


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
@group_required('CAE Director', 'CAE Admin GA', 'CAE Programmer GA', 'CAE Admin', 'CAE Programmer')
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