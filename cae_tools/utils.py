"""
Utility Functions for Cae Tools.
"""

# System Imports.
import logging
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import Http404


def send_single_email(*args, email_from=None, email_to=None, email_subject=None, email_message=None, **kwargs):
    """
    Sends a single email, using provided args.
    :param email_from: The "from" address for an email.
    :param email_to: The "to" address for an email.
    :param email_subject: The "subject" line for an email.
    :param email_message: The message for an email.
    """
    # Check for "email_from" arg.
    if not isinstance(email_from, str) or email_from == '':
        if settings.DEFAULT_FROM_EMAIL == '' or settings.DEFAULT_FROM_EMAIL == 'webmaster@localhost':
            raise ValueError('Email sender cannot be blank.')
        else:
            email_from = settings.DEFAULT_FROM_EMAIL

    # Check for "email_to" arg.
    if not isinstance(email_to, str):
        # Handle for non-string.
        raise ValueError('Email recipient must be a string.')
    elif email_to == '':
        # Handle for empty string.
        raise ValueError('Email recipient cannot be blank.')

    # Check for "email_subject" arg.
    if not isinstance(email_subject, str):
        # Handle for non-string.
        raise ValueError('Email subject must be a string.')
    elif email_subject == '':
        # Handle for empty string.
        raise TypeError('Email subject cannot be blank.')

    # Check for "email_message" arg.
    if not isinstance(email_message, str):
        # Handle for non-string.
        raise ValueError('Email message must be a string.')
    elif email_message == '':
        # Handle for empty string.
        raise TypeError('Email message cannot be blank.')

    # Send email.
    send_mail(
        email_subject,
        email_message,
        email_from,
        [email_to],
        fail_silently=False,
    )

    logging.info('Sent single email with subject "{0}" to "{1}".'.format(email_subject, email_to))


def send_mass_email(*args, email_from=None, email_to=None, email_subject=None, email_message=None, **kwargs):
    """
    Sends multiple (mass) emails, using provided args.
    Note:
        * Despite the name, send_mass_email can still send a single email, if desired.
        * All included recipients in the "email_to" line will see each other's email addresses in the email header.
        * Unlike Django "mass email" function, this sends one email at a time, just to multiple users.
            To send multiple emails with different contents, simply call this function multiple times.

    :param email_from: The "from" address for an email.
    :param email_to: The "to" address for an email.
    :param email_subject: The "subject" line for an email.
    :param email_message: The message for an email.
    """
    # Check for "email_from" arg.
    if not isinstance(email_from, str) or email_from == '':
        if settings.DEFAULT_FROM_EMAIL == '' or settings.DEFAULT_FROM_EMAIL == 'webmaster@localhost':
            raise ValueError('Email sender cannot be blank.')
        else:
            email_from = settings.DEFAULT_FROM_EMAIL

    # Check for "email_to" arg.
    if isinstance(email_to, list) or isinstance(email_to, tuple):
        # Handle if email_to field is a list or tuple.
        for recipient in email_to:
            if not isinstance(recipient, str) or recipient == '':
                raise ValueError('Invalid email recipient. {0}'.format(email_to))
    elif isinstance(email_to, str):
        # Handle if email_to field is a string.
        if not isinstance(email_to, str) or email_to == '':
            raise ValueError('Invalid email recipient. {0}'.format(email_to))
        else:
            email_to = [email_to]
    else:
        # Handle for all other types.
        raise TypeError('Expected "email_to" field to be of type list, tuple, or string. Got {0}.'.format(
            type(email_to)
        ))

    # Check for "email_subject" arg.
    if not isinstance(email_subject, str):
        # Handle for non-string.
        raise ValueError('Email subject must be a string.')
    elif email_subject == '':
        # Handle for empty string.
        raise TypeError('Email subject cannot be blank.')

    # Check for "email_message" arg.
    if not isinstance(email_message, str):
        # Handle for non-string.
        raise ValueError('Email message must be a string.')
    elif email_message == '':
        # Handle for empty string.
        raise TypeError('Email message cannot be blank.')

    # Send emails.
    send_mail(
        email_subject,
        email_message,
        email_from,
        email_to,
        fail_silently=False,
    )

    logging.info('Sent mass emails with subject "{0}" to "{1}".\n'.format(email_subject, email_to))


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


def test_mass_email():
    """
    Tests sending of email with "send_mass_mail" function.
    This function is far more efficient when sending multiple emails. We are likely to use this as the default.
    Note that, despite the name, send_mass_email can still send a single email, if desired.
    """
    if settings.DEV_URLS:
        logging.info('Sending mass test emails...\n')

        # Validate from field.
        email_from = settings.DEFAULT_FROM_EMAIL
        if not isinstance(email_from, str) or email_from == '' or email_from == 'webmaster@localhost':
            raise ValueError('Invalid settings "DEFAULT_FROM_EMAIL" value of "{0}".'.format(email_from))

        # Validate to field.
        admins = settings.ADMINS
        email_to = []
        if isinstance(admins, list) and len(admins):
            # Is non-empty list. Validate all items within.
            for admin in admins:
                if not isinstance(admin[1], str) or admin[1] == '':
                    # At least one item is not a valid email.
                    raise ValueError('Invalid settings "ADMINS" value of "{0}".'.format(admins))
                else:
                    email_to.append(admin[1])
        else:
            # Non-list, or empty list.
            raise ValueError('Invalid settings "ADMINS" value of "{0}".'.format(admins))

        # Compose email contents.
        email_subject = 'Test "Mass Email" from CAE Workspace Project'
        email_message = \
            'Testing "mass email" functionality.\n' \
            'This sends a single email to a one or more addresses.\n\n' \
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi bibendum est a nisl convallis, at laoreet' \
            'lorem vehicula. Phasellus nulla magna, vulputate vel ex vel, suscipit convallis diam. Aenean nec velit' \
            'velit. Cras dictum bibendum erat, et rutrum quam scelerisque in. Integer sed nunc non velit lobortis' \
            'congue ultrices malesuada est. Aliquam efficitur id mi eget malesuada. Mauris tempor leo nec mi blandit,' \
            'sed sagittis augue dapibus. Pellentesque sem leo, pulvinar eget tellus in, vehicula imperdiet dolor.' \
            'Donec nec pharetra nulla. Fusce ac nulla aliquet, pellentesque diam at, dictum tortor. '

        # Send test emails.
        send_mass_email(
            email_from=email_from,
            email_to=email_to,
            email_subject=email_subject,
            email_message=email_message,
        )

        logging.info('Mass test emails sent.\n')
    else:
        raise Http404()
