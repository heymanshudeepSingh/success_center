"""
Various utility functions for CAE Home app. intended to make use of LDAP easier.
"""

# System Imports.
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse

# User Imports.
from cae_home.models import User, WmuUser
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


#region Ldap Simplification Functions

def get_or_create_login_user_model(request, user_id):
    """
    Attempts to get the "Login User" model with the associated user id.
    Relies on get_or_create_wmu_user_model() method if Winno is passed as id.

    A "Login User" is the User model associated with Django, to allow someone to login to the site.
    Has a direct, One-to-One connection with a UserIntermediary model.

    :param request: Django request object.
    :param user_id: Either BroncoNet or Winno of student.
    :return: The associated "Login User" model or None if not found.
    """
    if user_id is None:
        return None

    # Attempt to get model from django database.
    try:
        # First assume identifier is BroncoNet.
        user_model = User.objects.get(username=user_id)
    except User.DoesNotExist:
        # Failed on BroncoNet. Try Winno to be safe. To do this, we must go through the WmuUser model.
        wmu_user = get_or_create_wmu_user_model(request, user_id)

        # Proceed if WmuUser model value returned.
        if wmu_user is not None and not isinstance(wmu_user, TemplateResponse):
            # Got valid WmuUser model. Orig value must be a valid Winno.
            user_id = wmu_user.bronco_net

            # Try a second time, with proper BroncoNet.
            try:
                user_model = User.objects.get(username=user_id)
            except User.DoesNotExist:
                # Failed to get (Login) User model. Does not appear to exist in Django database.
                user_model = None

        # Failed to get equivalent WmuUser as well.
        else:
            # Check if TemplateResponse object was returned.
            if isinstance(wmu_user, TemplateResponse):
                # TemplateResponse returned. Indicates that ldap is likely not set up properly on local machine.
                return wmu_user
            else:
                # Passed value is likely not a valid BroncoNet or Winno.
                return None

    # Resort to LDAP if no (Login) User model was found.
    if user_model is None:
        # Use LDAP backend.
        from django.conf import settings
        if settings.CAE_LDAP['host'] == '' or settings.WMU_LDAP['host'] == '' or settings.ADV_LDAP['login_dn'] == '':
            # Missing local LDAP credentials.
            logger.warning('LDAP credentials not set. Failed to get (User model) LDAP information.')
            return TemplateResponse(request, 'error_views/ldap_required.html', {})
        else:
            # Local LDAP credentials found. Attempt connection.
            try:
                from workspace.ldap_backends.wmu_auth import cae_backend, wmu_backend
                cae_ldap = cae_backend.CaeAuthBackend()
                wmu_ldap = wmu_backend.WmuAuthBackend()

                # Pull (Login) User info from LDAP using BroncoNet.
                user_model = cae_ldap.create_or_update_user_model(user_id)
            except (ImportError, ModuleNotFoundError):
                # LDAP is not installed on machine. Redirect to template stating such.
                logger.warning('Error importing LDAP module. Is the CAE "simple_ldap_lib" library installed?')
                return TemplateResponse(request, 'error_views/ldap_required.html', {})

            except ValidationError:
                # Provided user_id value is invalid.
                user_model = None

    return user_model


def get_or_create_wmu_user_model(request, user_id):
    """
    Attempts to get the "Wmu User" model with the associated user id.

    A "Wmu User" is the User model associated with Django, to allow someone to login to the site.
    Has a direct, One-to-One connection with a UserIntermediary model.

    :param request: Django request object.
    :param user_id: Either BroncoNet or Winno of student.
    :return: The associated "Login User" model | None if not found | TemplateResponse if no local Ldap connection.
    """
    if user_id is None:
        return None

    # Attempt to get model from django database.
    try:
        # First assume identifier is BroncoNet.
        user_model = WmuUser.objects.get(bronco_net=user_id)
    except WmuUser.DoesNotExist:
        # Failed on BroncoNet. Try Winno to be safe.
        try:
            user_model = WmuUser.objects.get(winno=user_id)
        except WmuUser.DoesNotExist:
            # Failed to get WmuUser model. Does not appear to exist in Django database.
            user_model = None

    # Resort to LDAP if no WmuUser model was found.
    if user_model is None:
        # Use LDAP backend.
        from django.conf import settings
        if settings.CAE_LDAP['host'] == '' or settings.WMU_LDAP['host'] == '' or settings.ADV_LDAP['login_dn'] == '':
            # Missing local LDAP credentials.
            logger.warning('LDAP credentials not set. Failed to get (WmuUser model) LDAP information.')
            return TemplateResponse(request, 'error_views/ldap_required.html', {})
        else:
            # Local LDAP credentials found. Attempt connection.
            try:
                from workspace.ldap_backends.wmu_auth import wmu_backend
                wmu_ldap = wmu_backend.WmuAuthBackend()

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

#endregion Ldap Simplification Functions
