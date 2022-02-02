# System imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.contrib import messages

# utility imports
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
            # This prevents user not found in other Ldap if attribute not found ex. home phone is only in Advising but
            # with this we can use it to pull info from other ldap s
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
                messages.error(request, "Failed to connect to CAE LDAP!")

            # Check if we got LDAP response. If not, user does not exist in Advising LDAP.
            if advising_ldap_user_info is not None:
                # If user doesnt exist, their cn (name) doesnt exist in Advising ldap.
                # this error only exists for Advising ldap.
                if advising_ldap_user_info['wmuKerberosUserStatus'][0] == "removed":
                    messages.warning(request, "User doesn't exist anymore!")
                else:
                    cn = advising_ldap_user_info['cn'][0]
            else:
                messages.error(request, "Failed to connect to Advising LDAP!")

            # Check if we got LDAP response. If not, user does not exist in WMU LDAP.
            if wmu_ldap_user_info is not None:
                cn = wmu_ldap_user_info['cn'][0]

            else:
                messages.error(request, "Failed to connect to WMU LDAP!")
    return TemplateResponse(request, 'cae_tools/ldap_utility.html', {
        'cae_ldap_user_info': cae_ldap_user_info,
        'advising_ldap_user_info': advising_ldap_user_info,
        'wmu_ldap_user_info': wmu_ldap_user_info,
        'form': form,
        'cn': cn
    })


@login_required
@group_required('CAE Director', 'CAE Admin GA', 'CAE Programmer GA', 'CAE Admin', 'CAE Programmer')
def cae_ldap_password_reset(request):
    """
    Resets password for Cae center employees
    """
    sync_ldap()

    # initialize ldap backend for CAE Ldap
    cae_auth_backend = CaeAuthBackend()

