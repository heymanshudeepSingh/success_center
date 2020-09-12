"""
View permission decorators for CAE Home app.

To use on class based views, call with Django's "method_decorator".
To pass args, see https://stackoverflow.com/a/27864969
"""

# System Imports.
from channels.db import close_old_connections as _term_conns
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from functools import wraps


def close_old_db_connections(func):
    """
    Decorator for functions that connect to the database.
    According to http://www.programmersought.com/article/1815911998/, may be a solution for the "channels sockets
    stopped connecting" error that's been plaguing us.

    More on error: https://dev.mysql.com/doc/refman/8.0/en/gone-away.html
    """
    def wrapper(*args, **kwargs):
        # UnitTests were failing with this.
        # Furthermore, Django 3.0 provided very helpful error messages that helped pinpoint problems with Channels.
        # It's possible that we don't need this decorator anymore.
        # If it turns out we do, delete this comment and uncomment the line below, once more.

        # _term_conns()
        return func(*args, **kwargs)

    return wrapper


def group_required(*required_groups):
    """
    Limits view access based on user group.
    To access view, user must be part of one or more groups provided.
    Logic from https://codereview.stackexchange.com/questions/57073/django-custom-decorator-for-user-group-check
    """
    def check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Check that user is authenticated.
            if not user.is_authenticated:
                messages.warning(request, 'Please log in to view the page.')
                return redirect_to_login(request.path)

            # Check that user is part of provided groups.
            if bool(user.groups.filter(name__in=required_groups)):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return check_group
