"""
View permission decorators for CAE Home app.

To use on class based views, call with Django's "method_decorator".
To pass args, see https://stackoverflow.com/a/27864969
"""

# System Imports.
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from functools import wraps


def group_required(*required_groups):
    """
    Limits view access based on user group.
    To access view, user must be part of one or more groups provided.
    Logic from https://codereview.stackexchange.com/questions/57073/django-custom-decorator-for-user-group-check

    Note: If you update this, make sure to also update below GroupRequiredMixin class.
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


class GroupRequiredMixin:
    """
    Class mixin version of above group_required() function.
    Works the same, just allows logic to apply to classes as well.

    Note: If you update this, make sure to also update above group_required decorator function.
    """
    required_user_auth_groups = None

    def dispatch(self, request, *args, **kwargs):
        """
        Override class dispatch to check for user login and user group membership.
        """
        # Get current User.
        user = request.user

        # Check that user is authenticated.
        if not user.is_authenticated:
            messages.warning(request, 'Please log in to view the page.')
            return redirect_to_login(request.path)

        # Check that provided values are Group models. If not, convert to such.
        required_group_set = []
        if self.required_user_auth_groups:
            for passed_group in self.required_user_auth_groups:
                if isinstance(passed_group, list) or isinstance(passed_group, tuple):
                    # Is list of groups. Handle accordingly.
                    for inner_passed_group in passed_group:
                        required_group_set.append(_validate_group(inner_passed_group))
                else:
                    # Is single value. Handle accordingly.
                    required_group_set.append(_validate_group(passed_group))
        else:
            raise ValueError(
                'GroupRequiredMixin is called, but no groups provided. Please populate class the ' +
                '"required_user_auth_groups" value with desired groups.'
            )

        # Check that user is either superuser, or part of provided groups.
        if user.is_superuser or bool(user.groups.filter(name__in=required_group_set).exists()):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
