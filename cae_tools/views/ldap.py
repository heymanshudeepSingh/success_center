# System imports
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.contrib import messages
from django.core.mail import send_mail

# utility imports
import cae_home.models
from cae_home.decorators import group_required
from workspace.ldap_backends.wmu_auth.cae_backend import CaeAuthBackend
from workspace.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend
from workspace.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend
from cae_tools import forms
from workspace.ldap_backends import simple_ldap_lib


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
                # If user doesnt exist, their cn (name) doesnt exist in Advising ldap.
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


@login_required
@group_required('CAE Director', 'CAE Admin GA', 'CAE Programmer GA', 'CAE Admin', 'CAE Programmer')
def cae_password_reset(request, password = None):
    """
    Resets password for Cae center employees
    """

    # check if ldap is setup in env
    if settings.CAE_LDAP['login_dn'] == "":
        messages.error(request, "Can't connect to Ldap server. :(")
    else:
        sync_ldap()

    # initialize ldap backend for CAE Ldap
    cae_auth_backend = CaeAuthBackend()

    # initialize form
    form = forms.CaePasswordResetForm()

    if request.method == 'POST':
        form = forms.CaePasswordResetForm(request.POST)

        if form.is_valid():
            user_id = form.cleaned_data['user_id']

            # initialize uid for ldap
            uid = None

            # Connect to LDAP server and pull user's full info.
            cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(user_id, search_by="uid",
                                                                     attributes=['uid','cn'])
            if cae_ldap_user_info:
                uid = cae_ldap_user_info["uid"][0]

            if uid is None:
                messages.error(request, "User Not Found!")
            else:
                # By this point we know we have UID for sure. Now fetch information using UID from CAE Ldap
                cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(f'{uid}')

                # Check if user is associated with any group - programmers, director, admins, etc.
                get_user_group = cae_auth_backend.get_ldap_user_groups(uid)
                valid_group = any(user_group is True for user_group in get_user_group.values())

                if valid_group:
                    user_cn = cae_ldap_user_info["cn"][0]
                    if not user_cn:
                        raise ValueError("User does not have cn!")

                    # Initialize connection elements
                    host = "ldap://padl.ceas.wmich.edu"

                    # Get user from form and convert it into LDAP search format
                    user_dn = "cn={0},{1}".format(user_cn,settings.CAE_LDAP['user_search_base'])

                    # Get admin DN and Password as we need admin privileges to reset passwords
                    admin_dn = settings.CAE_LDAP['admin_dn']
                    admin_password = settings.CAE_LDAP['admin_password']

                    # Check if password is provided in the function call
                    if password:
                        user_password = password

                    # Else default to env password
                    else:
                        user_password = settings.USER_SEED_PASSWORD

                    # Command that resets the password - for reference try http://manpages.ubuntu.com/manpages/bionic/man1/ldappasswd.1.html
                    cmd = "ldappasswd -H {} -x -D '{}' -w '{}' -s '{}' '{}'".format(
                        host,
                        admin_dn,
                        admin_password,
                        user_password,
                        user_dn,
                    )
                    try:
                        # Run command in terminal.
                        os.system(cmd)
                        messages.success(request, "Password Changed!")
                        # initialize programmers email .
                        programmers_email = cae_home.models.WmuUser.objects.get(bronco_net="ceas_prog").official_email

                        # convert recipient_email to list as that is the format accepted by send email function
                        recipient_email = [cae_home.models.WmuUser.objects.get(bronco_net=uid).shorthand_email()]

                        # Get IP of the user changing password.
                        # Reference - https://stackoverflow.com/a/4581997
                        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                        if x_forwarded_for:
                            ip = x_forwarded_for.split(',')[0]
                        else:
                            ip = request.META.get('REMOTE_ADDR')

                        try:
                            # Try Sending Email
                            send_mail("CAE Password Changed!",
                                      f"Your CAE Center Password has been reset! \n by {request.user} \n IP: {ip}",
                                      programmers_email,
                                      recipient_email)
                            messages.success(request, "Email Send!")
                        except ConnectionError:
                            messages.error(request,"Unable to send Email!")

                    except ConnectionError:
                        messages.error(request,"Unable to reset password!")

                else:
                    messages.error(request, "Invalid user group!")

    return TemplateResponse(request, 'cae_tools/password_reset.html', {
        'form': form,
        'button_text':"Reset!",

    })
