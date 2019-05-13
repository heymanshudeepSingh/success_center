"""
Custom template tags for CAE Home app.
"""

from django import template
from django.conf import settings
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

    :param obj:
    :return:
    """
    if obj.__doc__:
        return mark_safe('<p>{0}</p>'.format(obj.__doc__))
    else:
        return mark_safe('<p>No docstring.</p>')
