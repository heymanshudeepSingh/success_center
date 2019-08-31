"""
Filters for CAE Home app.
Used in DjangoRest views.
"""

# System Imports.
import django_filters

# User Class Imports.
from cae_home import models


class DepartmentFilter(django_filters.FilterSet):
    """
    Json Api filter for department model.
    """
    class Meta:
        model = models.Department
        fields = {
            'name': ['startswith'],
        }
