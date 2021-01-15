"""
Authentication-related views for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# User Imports.
from . import cae_employee_groups, step_employee_groups
from cae_home import forms
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


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
                    return redirect('success_center_core:index')

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
