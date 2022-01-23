from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse

from cae_home.utils import logger


def index(request):
    if settings.CAE_LDAP['host'] == '' or settings.WMU_LDAP['host'] == '' or settings.ADV_LDAP['login_dn'] == '':
        # Missing local LDAP credentials.
        logger.warning('LDAP credentials not set. Failed to get (WmuUser model) LDAP information.')
        return TemplateResponse(request, 'error_views/ldap_required.html', {})
    else:
        # Local LDAP credentials found. Attempt connection.
        try:
            from workspace.ldap_backends.wmu_auth import wmu_backend
            wmu_ldap = wmu_backend.WmuAuthBackend()
            user_id = request.POST.get("user_id")
            if user_id.isdigit():
                # Is likely a winno. Get bronconet.
                bronconet = wmu_ldap.get_bronconet_from_winno(user_id)
                if bronconet is not None:
                    user_id = bronconet

            # Pull WmuUser info from LDAP using bronconet.
            user_model = wmu_ldap.create_or_update_wmu_user_model(user_id)
        except (ImportError, ModuleNotFoundError):
            # LDAP is not installed on machine. Redirect to template stating such.
            logger.warning('Error importing LDAP module. Is the CAE "simple_ldap_lib" library installed?')
            return TemplateResponse(request, 'error_views/ldap_required.html', {})

        except ValidationError:
            # Provided user_id value is invalid.
            user_model = None

    return user_model
