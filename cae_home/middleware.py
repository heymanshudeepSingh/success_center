"""
Middleware for CAE Home app.
"""

# System Imports.
import pytz, re
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import ObjectDoesNotExist
from django.utils import timezone


from django.core.handlers.exception import response_for_exception

# User Class Imports.
from cae_home import models
from settings import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


class GetUserProfileMiddleware(object):
    """
    Load profile associated with authenticated user and append to user request object for other middleware/view access.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # If user is logged in, get profile info.
        if request.user.is_authenticated:
            request.user.profile = request.user.userintermediary.profile

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

            # Get site serve type (HTTP or HTTPS). HTTP should be for development, HTTPS for production.
            response.context_data['https'] = request.is_secure()

            # Get site domain.
            response.context_data['domain'] = get_current_site(request)

            # Get installed project/app details.
            response.context_data['imported_projects'] = settings.INSTALLED_APP_DETAILS

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
        logger.error('{0}'.format(exception), exc_info=True)

        # Call standard Django response handling for given exception.
        return response_for_exception(request, exception)

