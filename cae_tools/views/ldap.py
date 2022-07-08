""""""

# System imports
import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy

# utility imports
from cae_home.decorators import group_required
from workspace.ldap_backends.wmu_auth.cae_backend import CaeAuthBackend
from workspace.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend
from workspace.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend
from cae_tools import forms
from workspace.ldap_backends import simple_ldap_lib
from workspace.settings.reusable_settings import CAE_CENTER_GROUPS


def sync_ldap():
    """
    handle syncing with ldap using settings in env.py
    """
    # initialize ldap library and syncing with settings in env
    ldap_lib = simple_ldap_lib.SimpleLdap()

    ldap_lib.set_host(settings.CAE_LDAP['host'])
    ldap_lib.set_master_account(
        settings.CAE_LDAP['login_dn'],
        settings.CAE_LDAP['login_password'],
        check_credentials=False,
        get_info='SCHEMA',
    )
    ldap_lib.set_search_base(settings.CAE_LDAP['user_search_base'])
    ldap_lib.set_uid_attribute(settings.CAE_LDAP['default_uid'])


@login_required()
@group_required('CAE Director', 'CAE Admin GA', 'CAE Programmer GA', 'CAE Admin', 'CAE Programmer')
def ldap_utility(request):
    """
    ldap utility function that searches user based on Bronco net, Email, Fullname, Win Number
    or Phone number and return results from CAE, Advising, and main Campus WMU Ldap

    """
    # check if ldap is setup
    if settings.CAE_LDAP['login_dn'] == "":
        messages.error(request, "Can't connect to Ldap server. :(")
    else:
        sync_ldap()
    # initialize ldap backend for all 3 ldap s - main campus, advising and CAE
    cae_auth_backend = CaeAuthBackend()
    advising_auth_backend = AdvisingAuthBackend()
    wmu_auth_backend = WmuAuthBackend()

    # initialize variables
    form = forms.LdapUtilityForm()
    uid = None
    cae_ldap_user_info = None
    advising_ldap_user_info = None
    wmu_ldap_user_info = None
    # cn holds username and will be used as page header
    cn = None

    if request.method == 'POST':
        form = forms.LdapUtilityForm(request.POST)
        if form.is_valid():
            # get user input
            search_by = form.cleaned_data['search_choice_field']
            search_for_value = form.cleaned_data['search_input']

            # Connect to LDAP server and pull user's full info.
            cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by,
                                                                     attributes=['uid'])
            if cae_ldap_user_info:
                uid = cae_ldap_user_info["uid"][0]

            wmu_ldap_user_info = wmu_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by,
                                                                     attributes=['uid'])
            if uid is None and wmu_ldap_user_info:
                uid = wmu_ldap_user_info["uid"][0]

            advising_ldap_user_info = advising_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by,
                                                                               attributes=['uid'])
            if uid is None and advising_ldap_user_info:
                uid = advising_ldap_user_info["uid"][0]

            if uid is None:
                messages.error(request, "Error Unknown Value!")

            # By this point we know we have UID for sure. Now fetch information using UID from all 3 ldap s
            cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(f'{uid}')
            wmu_ldap_user_info = wmu_auth_backend.get_ldap_user_info(f'{uid}')
            advising_ldap_user_info = advising_auth_backend.get_ldap_user_info(f'{uid}')

            # Check if we got LDAP response. If not, user does not exist in CAE LDAP.
            if cae_ldap_user_info is not None:
                cn = cae_ldap_user_info['cn'][0]
            else:
                messages.warning(request, "Failed to connect to CAE LDAP!")

            # Check if we got LDAP response. If not, user does not exist in Advising LDAP.
            if advising_ldap_user_info is not None:
                # If user doesn't exist, their cn (name) doesn't exist in Advising ldap.
                # this error only exists for Advising ldap.
                if advising_ldap_user_info['wmuKerberosUserStatus'][0] == "removed":
                    messages.warning(request, "User doesn't exist anymore!")
                else:
                    cn = advising_ldap_user_info['cn'][0]
            else:
                messages.warning(request, "Failed to connect to Advising LDAP!")

            # Check if we got LDAP response. If not, user does not exist in WMU LDAP.
            if wmu_ldap_user_info is not None:
                cn = wmu_ldap_user_info['cn'][0]

            else:
                messages.warning(request, "Failed to connect to WMU LDAP!")
    return TemplateResponse(request, 'cae_tools/ldap_utility.html', {
        'cae_ldap_user_info': cae_ldap_user_info,
        'advising_ldap_user_info': advising_ldap_user_info,
        'wmu_ldap_user_info': wmu_ldap_user_info,
        'form': form,
        'cn': cn
    })


@login_required()
@group_required('CAE Director', 'CAE Admin GA', 'CAE Programmer GA', 'CAE Admin', 'CAE Programmer')
def cae_password_reset(request):
    """
    Allows a logged-in CAE Center employee to reset other's passwords, such as in
    event of the other user forgetting their password.
    """
    ldap_not_set_up = False

    # Check if ldap settings are defined.
    if settings.CAE_LDAP['login_dn'] == '':
        messages.error(request, 'Can\'t connect to Ldap server. :( \n Are project LDAP settings setup?')
        ldap_not_set_up = True

    # Initialize SimpleLdapLibrary + CAE Ldap backend.
    try:
        ldap_lib = simple_ldap_lib.SimpleLdap()
    except AttributeError:
        messages.error(request, 'Can\'t connect to Ldap server. :( \n Is the SimpleLdapLib installed?')
        ldap_not_set_up = True

    # Initialize form.
    form = forms.CaePasswordResetForm()

    # Handle for form submission.
    if not ldap_not_set_up and request.method == 'POST':
        form = forms.CaePasswordResetForm(request.POST)

        # Validate form.
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            from_email = settings.DEFAULT_FROM_EMAIL

            # Generate temporary password for user.
            generated_password = str(settings.USER_SEED_PASSWORD) + str(random.randint(0, 999))

            # Pull ldap values from settings.
            host = settings.CAE_LDAP['host']
            admin_dn = settings.CAE_LDAP['admin_dn']
            admin_password = settings.CAE_LDAP['admin_password']
            search_base = settings.CAE_LDAP['user_search_base']

            # Note: "ldap password not found error" will be thrown if Ldap-utils is not installed.
            try:
                # Validate provided user_id value.
                user = get_user_model().objects.get(username=user_id)

                results = ldap_lib.password_reset(
                    user_id,
                    'invalid',
                    generated_password,
                    host=host,
                    dn=admin_dn,
                    password=admin_password,
                    search_base=search_base,
                    skip_password_auth=True,
                )
                # Check status.
                if results[0] is False:
                    messages.error(request, results[1])
                else:
                    messages.success(request, 'Password successfully changed.')

                    # Get email for user who's password is being reset.
                    user_email = user.email

                    # Get list of emails to send to.
                    # Includes user that had password reset, as well as all active GA's (so they can check against
                    # potentially malicious password-resetting actions).
                    recipient_email = [user_email] + list(get_user_model().get_cae_ga().values_list('email', flat=True))

                    # Get IP of the user changing password.
                    # Reference - https://stackoverflow.com/a/4581997
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')

                    # Send notification email.
                    send_mail(
                        'CAE Password Changed',
                        (
                            '{0}\'s ({1} {2}) CAE Center Password has been reset by {3} ({4} {5})\n'
                            'Reset occurred from Ip Address: "{6}"\n'
                            '\n'
                            '\n'
                            'Your new password is "{7}".\n'
                        ).format(
                            user_id,
                            user.first_name,
                            user.last_name,
                            request.user,
                            request.user.first_name,
                            request.user.last_name,
                            ip,
                            generated_password,
                        ),
                        from_email,
                        recipient_email,
                    )
                    messages.success(request, 'Password set to temporary value. Please check your email.')
                    return redirect(reverse_lazy('cae_home:user_details'))

            except get_user_model().DoesNotExist:
                # Handle for invalid username provided.
                messages.error(request, 'Failed to find username of "{0}".'.format(user_id))

            except ConnectionError:
                # Handle for failing to connect to LDAP.
                messages.error(request, 'LDAP connection error. Unable to reset password.')

    # Render response.
    return TemplateResponse(request, 'cae_tools/password_reset.html', {
        'form': form,
        'button_text': 'Reset',
    })
