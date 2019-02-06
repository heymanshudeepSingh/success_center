"""
Views for CAE_Home App.
"""

import logging
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail, send_mass_mail
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from . import forms


# Import logger.
logger = logging.getLogger(__name__)


def login(request, *args, **kwargs):
    """
    Modified login view for "remember me" checkbox.
    Once processed, passes login to default auth views.
    """
    # Check if user is logged in. If so, automatically redirect to index page.
    if request.user.is_authenticated:
        return redirect('cae_home:index')

    # User not logged in. Check if request is POST.
    if request.method == 'POST':

        # See if remember_me box is checked.
        if request.POST.get('remember_me', None):
            # Remember me is checked. Hold user session indefinitely.
            request.session.set_expiry(0)
        else:
            # Remember me is not checked. Set session to time out in 3600 seconds (1 hour).
            request.session.set_expiry(3600)

    return auth_views.login(request, *args, authentication_form=forms.AuthenticationForm, **kwargs)


#region Debug/Development Views

def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'cae_home/index.html', {})
    else:
        raise Http404()


def internal_dev_index(request):
    """
    The internal (cae home) index page.
    Displays front-end information/examples specific to the internal site layout and stylings.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'cae_home/css_example.html', {})
    else:
        raise Http404()


def external_dev_index(request):
    """
    The external (wmu clone) index page.
    Displays front-end information/examples specific to the external site layout and stylings.
    This should only be accessible in development environments.
    """
    if settings.DEV_URLS:
        return TemplateResponse(request, 'wmu_home/index.html', {})
    else:
        raise Http404()


def test_single_email(request):
    """
    Tests sending of email with "send_mail" function.
    This function is acceptable when a single email is to be sent.
    """
    if settings.DEBUG:
        logging.info('Sending test email...\n')

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
            [email_to,],
            fail_silently=False,
        )

        logging.info('Email sent.\n')

        # Redirect to home.
        return redirect('cae_home:index')
    else:
        raise Http404()


def test_mass_email(request):
    """
    Tests sending of email with "send_mass_mail" function.
    This function is far more efficient when sending multiple emails. We are likely to use this as the default.
    Note that, despite the name, send_mass_email can still send a single email, if desired.
    """
    if settings.DEBUG:
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
        email_2_message = 'This is a test email from the CAE Center.'

        # Compose emails.
        email_1 = (email_subject, email_1_message, email_from, [email_to,])
        email_2 = (email_subject, email_2_message, email_from, [email_to,])

        # Send emails.
        send_mass_mail((email_1, email_2), fail_silently=False)

        logging.info('Emails sent.\n')

        # Redirect to home.
        return redirect('cae_home:index')
    else:
        raise Http404()

#endregion Debug/Development Views
