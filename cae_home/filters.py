"""
Filters for CAE_Home App.
Used in DjangoRest views.
"""

import django_filters

from . import models


class DepartmentFilter(django_filters.FilterSet):
    """
    Json Api filter for department model.
    """
    class Meta:
        model = models.Department
        fields = {
            'name': ['startswith'],
        }
