"""
Custom model field definitions.
"""

# System Imports.
import re
from django.db import models


class CodeField(models.CharField):
    """
    Code Model Field

    Is effectively a standard "Django CharField", except with modified input values.
    Codes are always uppercase, and stripped of spaces.
    """
    def pre_save(self, model_instance, add, *args, **kwargs):
        """
        Strip spaces and make uppercase, prior to saving field.
        """
        # Get field attribute.
        value = getattr(model_instance, self.attname, None)

        # Check if attribute was non-empty.
        if value:
            # Use regex replacement to guarantee we get all types of whitespace, in entirety of string.
            pattern = re.compile(r'\s+')
            value = re.sub(pattern, '', str(value)).upper()
            setattr(model_instance, self.attname, value)
        else:
            value = super().pre_save(model_instance, add, *args, **kwargs)

        # Return formatted field attribute.
        return value
