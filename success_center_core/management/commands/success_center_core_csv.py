"""
Success Center command to export student usage data to csv for main campus.

Should be run every night on production via a cronjob.
TODO: Ask Chris when this needs to happen.
"""

# System Imports.
from django.core.management.base import BaseCommand

# User Class Imports.
from apps.Success_Center.success_center_core import models


class Command(BaseCommand):
    help = 'Creates CSV from the student usage logs.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """

        self.stdout.write(
            self.style.HTTP_INFO('SUCCESS_CENTER: Write student usage logs to CSV.')
        )

        self.write_csv_from_usage_logs()

        self.stdout.write(
            self.style.HTTP_INFO('SUCCESS_CENTER: Student usage log transfer complete.')
        )

    def write_csv_from_usage_logs(self):
        """
        Loops through all student usage records and writes to csv file.
        """

        def log_to_str(s):
            return '{},"{}","{}",{},{}\n'.format(
                s.student.winno,
                s.check_in.replace(tzinfo=None, microsecond=0),
                s.check_out.replace(tzinfo=None, microsecond=0),
                s.check_out.isocalendar()[1],
                s.location,
            )

        # Find all entries that are still open.
        usage_logs = models.StudentUsageLog.objects.filter(approved=True)
        with open('../home/successctr/success_center_data.csv', 'w') as fd:
            # Loop through all currently active shifts and clock them out.
            fd.writelines(map(log_to_str, usage_logs))
