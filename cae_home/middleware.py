"""
Middleware for CAE Home app.
"""

# System Imports.
import pytz, re
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.handlers.exception import response_for_exception
from django.db.models import ObjectDoesNotExist
from django.http import Http404
from django.utils import timezone

# User Imports.
from cae_home import models
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


class GetUserProfileMiddleware(object):
    """
    Load profile associated with authenticated user and append to user request object for other middleware/view access.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # Add extra values if user is logged in.
        if request.user.is_authenticated:
            # Get user profile info.
            request.user.profile = request.user.userintermediary.profile

            # Determine if user is CAE Center user.
            user_groups = request.user.groups.all().values_list('name', flat=True)
            is_cae_user = False
            for group in user_groups:
                if group in settings.CAE_CENTER_GROUPS:
                    is_cae_user = True
            request.user.is_cae_user = is_cae_user

        # Resume view call as normal.
        response = self.get_response(request)
        return response


class SetTimezoneMiddleware(object):
    """
    Allows views to auto-convert from UTC to user's timezone.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # Attempt to set timezone for user in all views.
        tzname = None
        if request.user.is_authenticated:
            tzname = request.user.profile.user_timezone
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

        # Resume view call as normal.
        response = self.get_response(request)
        return response


class GetProjectDetailMiddleware(object):
    """
    Passes project detail information to all views.

    Note: To function properly, all views must use "TemplateResponse" instead of "Render"
          Views should also provide an object dictionary even in the event that they pass no data (such as an index).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # Check to ensure DjangoRest views don't error.
        if response.context_data is not None:

            # Get if site is being served as development or production mode.
            # Note we get "DEV_URLS" instead of "DEBUG" because Django has special, built-in extra logic for "DEBUG".
            # (See settings/extra_settings file for more info.)
            # Using an equivalent custom settings variable saves potential future headache.
            response.context_data['debug'] = settings.DEV_URLS

            # Get site serve type (HTTP or HTTPS).
            # Generally speaking though, the site serves HTTP for development, and HTTPS for production.
            response.context_data['https'] = request.is_secure()

            # Get site domain.
            response.context_data['domain'] = get_current_site(request)

            # Get installed project/app details.
            response.context_data['imported_projects'] = settings.INSTALLED_APP_DETAILS

            # Check if CAE Web is installed. Needed for setting the "default" header nav.
            response.context_data['caeweb_installed'] = 'apps.CAE_Web.cae_web_core.apps.CaeWebCoreConfig' in settings.INSTALLED_APPS

            # Get CAE Programmer email (For footer).
            try:
                prog_email = models.WmuUser.objects.get(bronco_net='ceas_prog').official_email
                response.context_data['cae_prog_email'] = prog_email
            except ObjectDoesNotExist:
                pass

        return response


class GetUserSiteOptionsMiddleware(object):
    """
    Gets site theme for all views.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # Resume view call as normal.
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # Check to ensure DjangoRest views don't error.
        if response.context_data is not None:

            if request.user.is_authenticated:
                # User authenticated. Attempt to get user's model.
                response.context_data['site_theme'] = request.user.profile.site_theme
                response.context_data['desktop_font_size'] = request.user.profile.get_desktop_font_size()
                response.context_data['mobile_font_size'] = request.user.profile.get_mobile_font_size()
            else:
                # Default to "wmu" site theme.
                response.context_data['site_theme'] = models.SiteTheme.objects.get(slug='wmu')
                response.context_data['desktop_font_size'] = 'base'
                response.context_data['mobile_font_size'] = 'base'

        # Parse url. All we care about is the argument before the first "/" character.
        url_split = re.split('^/([^/]*)/*', request.path)

        # Check that at least one argument was found.
        if len(url_split) > 1:
            app_url = url_split[1]
            try:
                request.session['cae_workspace_main_nav_template_path'] = settings.INSTALLED_APP_URL_DICT[app_url]
            except KeyError:
                # Arg was not for subproject. Likely a page in cae_home, such as user profile edit page.
                # Skip saving to session.
                pass

        # Get main nav template path from session.
        try:
            response.context_data['main_nav_template_path'] = request.session['cae_workspace_main_nav_template_path']
        except KeyError:
            # Session was not populated. Default to cae_home main nav path.
            response.context_data['main_nav_template_path'] = 'cae_home/nav/default_app_nav.html'

        return response


class HandleExceptionsMiddleware(object):
    """
    Handles all exceptions.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # Resume view call as normal.
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handles when any view raises an uncaught exception.
        """
        # Log error, except for some specific types (such as user Permission 403 error).
        # For all of these "specific types", do not log as error message, so we don't get spammed with emails.
        # However, log to warning message, in case we need to troubleshoot.
        if isinstance(exception, PermissionDenied):
            # Is 403 Permission error. User does not have permission to access page.
            logger.auth_warning('403: User "{0}" tried to access url "{1}".'.format(
                request.user,
                request.get_full_path_info(),
            ))

        elif isinstance(exception, Http404):
            # Is 404 "not found" error.
            # User likely entered a url that doesn't actually have a corresponding model.
            logger.auth_warning('404: User "{0}" tried to access url "{1}".'.format(
                request.user,
                request.get_full_path_info(),
            ))
        else:
            # Unhandled error type. Log and send error email.
            logger.error('{0}'.format(exception), exc_info=True)

        # Call standard Django response handling for given exception.
        response_for_exception(request, exception)

        # Note that this function SHOULD NOT return any value.
        # Otherwise, all exception pages that raise will look like a 500.
