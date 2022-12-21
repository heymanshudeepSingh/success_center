"""
Success Center command to close all open student usage records.

Should be run every night on production via a cronjob.
Ideal runtime is sometime between 2 am and 4 am, probably.
"""

# System Imports.
from django.core.management.base import BaseCommand
from django.utils import timezone


# User Class Imports.
from apps.Success_Center.success_center_core import models


class Command(BaseCommand):
    help = 'Closes all open student usage records.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('SUCCESS_CENTER: Validating all student usage records.'))

        self.validate_usage_records()

        self.stdout.write(self.style.HTTP_INFO('SUCCESS_CENTER: Student usage record validation complete.\n'))

    def validate_usage_records(self):
        """
        Loops through all student usage records that meet don't have a end time.
        """

        # Find all entries that are still open.
        usage_logs = models.StudentUsageLog.objects.filter(check_out=None)

        # Loop through all currently active shifts and clock them out.
        for usage_log in usage_logs:
            usage_log.check_out = timezone.now()
            usage_log.save()
