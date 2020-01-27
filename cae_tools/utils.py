"""
Utility Functions for Cae Tools.
"""

# System Imports.
import logging
from django.core.mail import send_mail, send_mass_mail


def test_single_email():
    """
    Tests sending of email with "send_mail" function.
    This function is acceptable when a single email is to be sent.
    """

    logging.info('Sending test single email...\n')

    # Compose email.
    email_from = 'cae-programmers@wmich.edu'
    email_to = 'cae-programmers@wmich.edu'
    email_subject = 'Test Email from CAE Workspace Project'
    email_message = \
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi bibendum est a nisl convallis, at laoreet' \
        'lorem vehicula. Phasellus nulla magna, vulputate vel ex vel, suscipit convallis diam. Aenean nec velit' \
        'velit. Cras dictum bibendum erat, et rutrum quam scelerisque in. Integer sed nunc non velit lobortis' \
        'congue ultrices malesuada est. Aliquam efficitur id mi eget malesuada. Mauris tempor leo nec mi blandit,' \
        'sed sagittis augue dapibus. Pellentesque sem leo, pulvinar eget tellus in, vehicula imperdiet dolor.' \
        'Donec nec pharetra nulla. Fusce ac nulla aliquet, pellentesque diam at, dictum tortor. '

    # Send email.
    send_mail(
        email_subject,
        email_message,
        email_from,
        [email_to, ],
        fail_silently=False,
    )

    logging.info('Email sent.\n')


def test_mass_email():
    """
    Tests sending of email with "send_mass_mail" function.
    This function is far more efficient when sending multiple emails. We are likely to use this as the default.
    Note that, despite the name, send_mass_email can still send a single email, if desired.
    """

    logging.info('Sending test emails...\n')

    # Compose email contents.
    email_from = 'cae-programmers@wmich.edu'
    email_to = 'cae-programmers@wmich.edu'
    email_subject = 'Test Email from CAE Workspace Project'
    email_1_message = \
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi bibendum est a nisl convallis, at laoreet' \
        'lorem vehicula. Phasellus nulla magna, vulputate vel ex vel, suscipit convallis diam. Aenean nec velit' \
        'velit. Cras dictum bibendum erat, et rutrum quam scelerisque in. Integer sed nunc non velit lobortis' \
        'congue ultrices malesuada est. Aliquam efficitur id mi eget malesuada. Mauris tempor leo nec mi blandit,' \
        'sed sagittis augue dapibus. Pellentesque sem leo, pulvinar eget tellus in, vehicula imperdiet dolor.' \
        'Donec nec pharetra nulla. Fusce ac nulla aliquet, pellentesque diam at, dictum tortor. '
    email_2_message = 'This is a test mass email from the CAE Center.'

    # Compose emails.
    email_1 = (email_subject, email_1_message, email_from, [email_to, ])
    email_2 = (email_subject, email_2_message, email_from, [email_to, ])

    # Send emails.
    send_mass_mail((email_1, email_2), fail_silently=False)

    logging.info('Emails sent.\n')


def send_mass_email(*args, email_subject=None, email_message=None,email_to=None, **kwargs):
    """
    Tests sending of email with "send_mass_mail" function.
    This function is far more efficient when sending multiple emails. We are likely to use this as the default.
    Note that, despite the name, send_mass_email can still send a single email, if desired.
    """
    if email_subject is None or email_subject == "":
        raise TypeError("Email Subject Cannot Be None.")

    if email_message is None or email_message == "":
        raise TypeError("Email Message Cannot Be None.")

    if email_to is None or email_to == "":
        raise ValueError("Email Recipient cannot be None")

    logging.info('Sending test emails...\n')

    # Compose email contents.
    email_from = 'cae-programmers@wmich.edu'
    # email_to = 'xaf8122@wmich.edu'

    # Compose emails.
    composed_email = (email_subject, email_message, email_from, [email_to, ])

    # Send emails.
    send_mass_mail((composed_email, ), fail_silently=False)

    logging.info('Emails sent.\n')
