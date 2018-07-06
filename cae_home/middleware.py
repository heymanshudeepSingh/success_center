"""CAE Workspace Middleware"""
import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    """Allow views to autoconvert from UTC to user's timezone"""
    def process_request(self, request):
        tzname = None
        if request.user.is_authenticated():
            tzname = request.user.profile.user_timezone
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
