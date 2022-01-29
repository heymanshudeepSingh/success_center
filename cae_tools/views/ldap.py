from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse

from cae_home.utils import logger
from workspace.ldap_backends import simple_ldap_lib
from workspace.ldap_backends.simple_ldap_lib.resources import ldap_lib
from workspace.ldap_backends.wmu_auth.cae_backend import CaeAuthBackend
from workspace.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend
from workspace.ldap_backends.wmu_auth.wmu_backend import WmuAuthBackend
from cae_tools import forms


def ldap_utility(request):
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

    # initialize ldap backend for all 3 ldap s - main campus, advising and CAE
    cae_auth_backend = CaeAuthBackend()
    advising_auth_backend = AdvisingAuthBackend()
    wmu_auth_backend = WmuAuthBackend()

    # initialize variables
    uid = None
    cae_ldap_user_info = None
    advising_ldap_user_info = None
    wmu_ldap_user_info = None
    # cn holds user name and will be used as page header
    cn = None

    if request.method == 'POST':
        for key, value in request.POST.items():
            print(f'Key: {key}')
            print(f'Value: {value}')
        form = forms.LdapUtilityForm(request.POST)
        if form.is_valid():
            # get user input
            search_by = form.cleaned_data['search_choice_field']
            search_for_value = form.cleaned_data['search_input']

            # Connect to LDAP server and pull user's full info.
            cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by, attributes=['uid'])
            if cae_ldap_user_info:
                uid = cae_ldap_user_info["uid"][0]

            wmu_ldap_user_info = wmu_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by, attributes=['uid'])
            if uid is None and wmu_ldap_user_info:
                uid = wmu_ldap_user_info["uid"][0]

            advising_ldap_user_info = advising_auth_backend.get_ldap_user_info(search_for_value, search_by=search_by, attributes=['uid'])
            if uid is None and advising_ldap_user_info:
                uid = advising_ldap_user_info["uid"][0]

            if uid is None:
                print("Error Unknown Value!")

            # By this point we know we have UID for sure. Now fetch information using UID from all 3 ldap s
            cae_ldap_user_info = cae_auth_backend.get_ldap_user_info(f'{uid}')
            wmu_ldap_user_info = wmu_auth_backend.get_ldap_user_info(f'{uid}')
            advising_ldap_user_info = advising_auth_backend.get_ldap_user_info(f'{uid}')

            # Check if we got LDAP response. If not, user does not exist in CAE LDAP.
            if cae_ldap_user_info is not None:
                print(f'user info : {cae_ldap_user_info}')
                cn = cae_ldap_user_info['cn'][0]
            else:
                print("Failed to connect to CAE LDAP!")

            print("-" * 80)
            # Check if we got LDAP response. If not, user does not exist in Advising LDAP.
            if advising_ldap_user_info is not None:
                print(f'user info : {advising_ldap_user_info}')
                cn = advising_ldap_user_info['cn'][0]

            else:
                print("Failed to connect to Advising LDAP!")
            print("-" * 80)

            # Check if we got LDAP response. If not, user does not exist in WMU LDAP.
            if wmu_ldap_user_info is not None:
                print(f'user info : {wmu_ldap_user_info}')
                cn = wmu_ldap_user_info['cn'][0]

            else:
                print("Failed to connect to WMU LDAP!")
            print("-" * 80)
    form = forms.LdapUtilityForm()
    return TemplateResponse(request, 'cae_tools/ldap_utility.html', {
        'cae_ldap_user_info': cae_ldap_user_info,
        'advising_ldap_user_info': advising_ldap_user_info,
        'wmu_ldap_user_info': wmu_ldap_user_info,
        'form': form,
        'cn': cn
    })
