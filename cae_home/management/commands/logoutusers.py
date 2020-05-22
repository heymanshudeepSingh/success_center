"""
Command to logout all "actively logged in" user sessions.

General logic from https://gist.github.com/playpauseandstop/1818351
"""

# System Imports.
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from django.utils import timezone
from importlib import import_module

# User Imports.


class Command(BaseCommand):
    help = 'Logout all "actively logged in" user sessions.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write('Logging out all users...')
        self.stdout.write('')

        # Get all active sessions.
        request = HttpRequest()
        current_time = timezone.now()
        sessions = Session.objects.filter(expire_date__gt=current_time)

        # Logout all found sessions.
        self.stdout.write('Examining active sessions:')
        for active_session in sessions:
            try:
                user_pk = active_session.get_decoded().get('_auth_user_id')
                username = get_user_model().objects.get(id=user_pk)
                self.stdout.write('    Logging out user "{0}".'.format(username))
            except get_user_model().ObjectDoesNotExist:
                self.stdout.write('    Logging out user "{0}".'.format(user_pk))

            request.session = self.init_session(active_session.session_key)
            logout(request)

        self.stdout.write('')
        self.stdout.write('Users logged out.')

    def init_session(self, session_key):
        """
        Initialize same session as done for "SessionMiddleware".
        """
        engine = import_module(settings.SESSION_ENGINE)
        return engine.SessionStore(session_key)
