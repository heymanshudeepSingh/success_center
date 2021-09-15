"""
View permission decorators for CAE Home app.

To use on class based views, call with Django's "method_decorator".
To pass args, see https://stackoverflow.com/a/27864969
"""

# System Imports.
from channels.db import close_old_connections as _term_conns
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import Group
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
            # Get current User.
            user = request.user

            # Check that user is authenticated.
            if not user.is_authenticated:
                messages.warning(request, 'Please log in to view the page.')
                return redirect_to_login(request.path)

            # Check that provided values are Group models. If not, convert to such.
            required_group_set = []
            for passed_group in required_groups:
                if isinstance(passed_group, list) or isinstance(passed_group, tuple):
                    # Is list of groups. Handle accordingly.
                    for inner_passed_group in passed_group:
                        required_group_set.append(_validate_group(inner_passed_group))
                else:
                    # Is single value. Handle accordingly.
                    required_group_set.append(_validate_group(passed_group))

            # Check that user is either superuser, or part of provided groups.
            if user.is_superuser or bool(user.groups.filter(name__in=required_group_set).exists()):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return check_group


def _validate_group(group):
    """
    Validates if provided value is auth Group model or not.
    If not, then assumes is str representation of desired Group name.
    """
    # Check if Group model instance.
    if isinstance(group, Group):
        # Is Group model. Add to directly list.
        return group
    else:
        # Not Group model. Assume is str of desired Group's name.
        try:
            return Group.objects.get(name=str(group).strip())
        except Group.DoesNotExist:
            raise Group.DoesNotExist(
                'Invalid Group name of "{0}" provided. Could not find corresponding group.'.format(group),
            )
