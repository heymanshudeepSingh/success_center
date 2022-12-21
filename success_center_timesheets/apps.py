"""
Timesheets app definition and hook into main project.
"""

# System Imports.
from django.apps import AppConfig

# User Class Imports.
from workspace.settings.reusable_settings import get_dynamic_app_path


class SuccessCenterTimesheetsConfig(AppConfig):
    name = '{0}'.format(get_dynamic_app_path(__file__))
    verbose_name = 'Success Center Timesheets'

    def ready(self):
        # Connect signals.
        pass
