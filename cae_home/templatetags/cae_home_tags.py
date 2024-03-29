"""
Custom template tags for CAE Home app.
"""

# System Imports.
from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.html import mark_safe


register = template.Library()


@register.simple_tag
def site_mode_is_debug():
    """
    Checks if site is set to debug or production mode.
    :return: True on debug, false on production.

    Note: Technically, there is a built in template tag "debug". However, the built in tag requires setting an
    "internal_ips" value in settings, for every dev user.

    Instead, this method skips ip evaluation and gets the debug value directly, since we have a non-standard
    implementation of establishing debug and production environments. The settings.DEBUG value is a simple True/False
    boolean, so there should be no issues using it for template logic.
    """
    return settings.DEBUG


@register.simple_tag
def render_model_docstring(obj):
    """
    Used to display each model's Docstring in the Django Admin.
    Helps clarify what each model's intended use is.
    """
    if obj.__doc__:
        return mark_safe('<p>{0}</p>'.format(obj.__doc__))
    else:
        return mark_safe('<p>No docstring.</p>')


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Template tag to determine if user belongs to provided group.
    :param user: Current user.
    :param group_name: Group to check membership of.
    """
    return user.groups.filter(name=group_name).exists()


@register.simple_tag
def datetime_as_time_passed(datetime_value, *args, display_seconds=False):
    """
    Displays given datetime value as time elapsed in Days/Hours/Minutes/Seconds.
    :param datetime_value: The datetime passed from template.
    :param display_seconds: Bool controlling if seconds should display in final string.
    """
    # Get current time.
    current_time = timezone.now()

    # Convert time values to total seconds.
    datetime_value = datetime_value.timestamp()
    current_time = current_time.timestamp()

    # Get amount of seconds that have passed between two time values.
    passed_time = current_time - datetime_value

    # Calculate total values.
    total_passed_seconds = int(passed_time)
    total_passed_minutes = int(total_passed_seconds / 60)
    total_passed_hours = int(total_passed_minutes / 60)
    total_passed_days = int(total_passed_hours / 24)

    # Mod to get user-friendly display.
    passed_days = int(total_passed_days)
    passed_hours = int(total_passed_hours % 24)
    passed_minutes = int(total_passed_minutes % 60)
    passed_seconds = int(total_passed_seconds % 60)

    # Finally condense it all down to a single string.
    passed_days_string = ''
    if passed_days > 0:
        passed_days_string = '{0} Days '.format(passed_days)

    passed_seconds_string = ''
    if display_seconds:
        passed_seconds_string = ' {0} Seconds'.format(passed_seconds)

    # Return our final string value.
    return '{0}{1} Hours {2} Minutes{3}'.format(
        passed_days_string,
        passed_hours,
        passed_minutes,
        passed_seconds_string,
    )


@register.filter
def dict_key(dictionary, key):
    """
    Allows accessing dictionary values from Django templates.
    :param dictionary: Dictionary to access.
    :param key: Key to attempt to get value from.
    :return: Value corresponding to dict key, or empty string if key is not present.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    else:
        raise TypeError(
            'Template attempting to get dictionary value. But "{0}" is type "{1}", not dict.'.format(
                dictionary,
                type(dictionary),
            )
        )


@register.filter
def is_string(val):
    """
    Allows user to check if the value in template is a string
    """
    return isinstance(val, str)


@register.filter
def is_list(val):
    """
    Allows user to check if the value in template is a list
    """
    return isinstance(val, list) or isinstance(val,tuple)


@register.filter(name='range')
def filter_range(number):
    """
    Effectively the template equivalent of Python's "range" function.
    Aka, returns a list of numbers, for quick/easy loop iteration.

    Only difference is this version starts at 1 (due to user-display stuff).
    Then provides number of items equal to the provided number.
    """
    return range(1, int(number) + 1)


@register.simple_tag
def define(val=None):
    """
    For defining variables within the current template scope.
    """
    return val
