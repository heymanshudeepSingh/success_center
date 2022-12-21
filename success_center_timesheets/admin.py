"""
Admin views for Success Center Timesheets app.
"""

# System Imports.
from django.contrib import admin

# User Imports.
from . import models


# Model Registration.
admin.site.register(models.TimesheetShift)
admin.site.register(models.PayPeriod)
admin.site.register(models.CurrentStepEmployees)
