"""
View permission decorators for CAE Home app.
"""

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from functools import wraps


def group_required(*required_groups):
    """
    Limits view access based on user group.
    Must be part of one or more groups provided.
    Logic from "https://codereview.stackexchange.com/questions/57073/django-custom-decorator-for-user-group-check"
    """
    def check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            print('User: {0}'.format(user))
            print('Args: {0}'.format(required_groups))

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
