"""
Testing command to send minimal email as a test.
Useful for verifying server email is working at all.
"""

# System Imports.
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Send server test email.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write('CAE_TOOLS: Sending test email.')

        self.send_test_email()

        self.stdout.write('CAE_TOOLS: Test emails sent.\n')

    def send_test_email(self):
        """
        Logic to send test email.
        """
        email_body_text = (
            "<p>This test email was sent from the CAE Center programmer's Django project.</p>"
            "<p>If you received this, then email is working.</p>"
        )

        # Send to all admin users.
        if len(settings.ADMINS) > 0:
            # One or more admin users defined in settings.
            # Send emails to all.
            for admin_user in settings.ADMINS:
                # Send email.
                email_to = [admin_user[1]]
                send_mail(
                    'CAE Center Test Email',
                    None,
                    settings.EMAIL_HOST_USER,
                    email_to,
                    html_message=email_body_text,
                )
        else:
            # No admin users defined in settings. Show warning.
            self.stdout.write('Failed to find any admin users, defined in settings the "env.py" file.')
