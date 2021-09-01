"""
Utility Functions for Cae Tools.
"""

# System Imports.
import logging
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import Http404


def send_single_email(email_to, email_subject, email_message, *args, email_from=None, as_html=False, **kwargs):
    """
    Sends a single email, using provided args. Args are validated prior to sending.

    If multiple emails are provided in the "email_to" arg, then single email is sent to all of them.
    All included recipients in the "email_to" line will see each other's email addresses in the email header.

    :param email_to: The "to" address for an email.
    :param email_subject: The "subject" line for an email.
    :param email_message: The message for an email.
    :param email_from: The "from" address for an email. If not provided, then will default to project "from" address.
    :param as_html: Boolean indicating if email allows html elements.
    """
    # Check for "email_from" arg.
    if not isinstance(email_from, str) or email_from.strip() == '':
        # Handle for blank "from" email.
        if settings.DEFAULT_FROM_EMAIL == '' or settings.DEFAULT_FROM_EMAIL == 'webmaster@localhost':
            # Was set, but to an invalid value.
            raise ValueError('Email sender cannot be blank.')
        else:
            # Was likely blank. Set to default.
            email_from = settings.DEFAULT_FROM_EMAIL
    email_from = email_from.strip()

    # Check for "email_to" arg.
    validated_email_to = []
    if isinstance(email_to, list) or isinstance(email_to, tuple):
        # Handle for array.

        # Check that one or more recipients provided.
        if len(email_to) == 0:
            raise ValueError('Email recipient cannot be blank.')

        # Validate each individual recipient.
        for value in email_to:
            if not isinstance(value, str):
                raise ValueError('Email recipient must be a string or list of strings.')
            value = value.strip()
            if value == '':
                raise ValueError('Email recipient cannot be blank.')

            validated_email_to.append(value)

    # Is single recipient. Validate.
    elif not isinstance(email_to, str):
        # Handle for non-string.
        raise ValueError('Email recipient must be a string or list of strings.')
    elif email_to.strip() == '':
        # Handle for empty string.
        raise ValueError('Email recipient cannot be blank.')
    else:
        validated_email_to.append(email_to.strip())

    # Check for "email_subject" arg.
    if not isinstance(email_subject, str):
        # Handle for non-string.
        raise ValueError('Email subject must be a string.')
    email_subject = email_subject.strip()
    if email_subject == '':
        # Handle for empty string.
        raise TypeError('Email subject cannot be blank.')

    # Check for "email_message" arg.
    if not isinstance(email_message, str):
        # Handle for non-string.
        raise ValueError('Email message must be a string.')
    email_message = email_message.strip()
    if email_message == '':
        # Handle for empty string.
        raise TypeError('Email message cannot be blank.')

    # Send email.
    send_mail(
        email_subject,
        email_message,
        email_from,
        validated_email_to,
        fail_silently=False,
        html_message=email_message if as_html else None,
    )

    logging.info('Sent single email with subject "{0}" to "{1}".'.format(email_subject, validated_email_to))


def test_single_email():
    """
    Tests sending of email with "send_mail" function.
    This function is acceptable when a single email is to be sent.
    """
    if settings.DEV_URLS:
        logging.info('Sending single test email...\n')

        # Validate to/from fields.
        email_to_from = settings.DEFAULT_FROM_EMAIL
        if not isinstance(email_to_from, str) or email_to_from == '' or email_to_from == 'webmaster@localhost':
            raise ValueError('Invalid settings DEFAULT_FROM_EMAIL value of "{0}".'.format(email_to_from))

        # Compose email contents.
        email_subject = 'Test "Single Email" from CAE Workspace Project'
        email_message = \
            'Testing "single email" functionality.\n' \
            'This sends a single email to a single address.\n\n' \
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi bibendum est a nisl convallis, at laoreet' \
            'lorem vehicula. Phasellus nulla magna, vulputate vel ex vel, suscipit convallis diam. Aenean nec velit' \
            'velit. Cras dictum bibendum erat, et rutrum quam scelerisque in. Integer sed nunc non velit lobortis' \
            'congue ultrices malesuada est. Aliquam efficitur id mi eget malesuada. Mauris tempor leo nec mi blandit,' \
            'sed sagittis augue dapibus. Pellentesque sem leo, pulvinar eget tellus in, vehicula imperdiet dolor.' \
            'Donec nec pharetra nulla. Fusce ac nulla aliquet, pellentesque diam at, dictum tortor. '

        # Send test email.
        send_single_email(
            email_from=email_to_from,
            email_to=email_to_from,
            email_subject=email_subject,
            email_message=email_message,
        )

        logging.info('Single test email sent.\n')
    else:
        raise Http404()
