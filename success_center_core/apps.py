"""
Core app definition and hook into main project.
"""

# System Imports.
from django.apps import AppConfig

# User Class Imports.
from workspace.settings.reusable_settings import get_dynamic_app_path


class SuccessCenterCoreConfig(AppConfig):
    name = '{0}'.format(get_dynamic_app_path(__file__))
    verbose_name = 'Success Center Core'

    def ready(self):
        # Connect signals.
        pass
