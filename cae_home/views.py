"""
Views for CAE_Home App.
"""

import logging
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail, send_mass_mail
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from rest_framework import viewsets, permissions

from . import forms, models
from .rest import filters, serializers


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

    return auth_views.LoginView.as_view(authentication_form=forms.AuthenticationForm, **kwargs)(request)


def login_redirect(request):
    """
    Determines redirect url after user login. Varies based on user group permissions.
    """
    if not request.user.is_authenticated:
        return redirect('cae_home:login')
    else:
        user_groups = request.user.groups.values_list('name', flat=True)

        # Check if programmer and development mode.
        if settings.DEV_URLS:
            if 'CAE Programmer' in user_groups:
                return redirect('cae_home:index')

        # Check if CAE Center employee.
        cae_employee_groups = [
            'CAE Director',
            'CAE Building Coordinator',
            'CAE Attendant',
            'CAE Admin',
            'CAE Programmer',
        ]
        for cae_group in cae_employee_groups:
            if cae_group in user_groups:
                return redirect('cae_web_core:index')

        # Unknown user group.
        exception = 'Server did not recognize login user\'s group. Please contact the CAE Center.'
        return TemplateResponse(request, 'cae_home/errors/404.html', {
            'error_message': exception,
        },
            status=404,
        )


@login_required
def user_edit(request, slug):
    """
    Edit view for a single user.
    """
    # Pull models from database.
    user_intermediary = get_object_or_404(models.UserIntermediary, slug=slug)
    user = user_intermediary.user
    user_profile = user_intermediary.profile
    address = user_profile.address
    phone_number = user_profile.phone_number

    form_list = []
    form = forms.UserForm(instance=user)
    form.display_name = 'General Info'
    form_list.append(form)

    form = forms.PhoneNumberForm(instance=phone_number)
    form.display_name = 'Phone Number'
    form_list.append(form)

    form = forms.AddressForm(instance=address)
    form.display_name = 'Address'
    form_list.append(form)

    form = forms.ProfileForm(instance=user_profile)
    form.display_name = 'Site Settings'
    form_list.append(form)

    # Check if request is post.
    if request.method == 'POST':
        valid_forms = True
        form_list = []

        # Handle for disabled field.
        POST = request.POST.copy()
        POST['username'] = user.username
        form = forms.UserForm(instance=user, data=POST)
        form.name = 'UserForm'
        form.display_name = 'General Info'
        form_list.append(form)

        form = forms.PhoneNumberForm(instance=phone_number, data=request.POST)
        form.name = 'PhoneNumberForm'
        form.display_name = 'Phone Number'
        form_list.append(form)

        form = forms.AddressForm(instance=address, data=request.POST)
        form.name = 'AddressForm'
        form.display_name = 'Address'
        form_list.append(form)

        form = forms.ProfileForm(instance=user_profile, data=request.POST)
        form.name = 'ProfileForm'
        form.display_name = 'Site Settings'
        form_list.append(form)

        # Check that all forms are valid.
        for form in form_list:
            if not form.is_valid():
                valid_forms = False

        if valid_forms:
            # All forms came back as valid. Save.
            for form in form_list:
                if form.name == 'PhoneNumberForm':
                    phone_number = form.save()
                elif form.name == 'AddressForm':
                    address = form.save()
                elif form.name == 'ProfileForm':
                    profile = form.save(commit=False)
                    profile.address = address
                    profile.phone_number = phone_number
                    profile.save()
                else:
                    form.save()

            # Render response for user.
            messages.success(request, 'Successfully updated user {0}.'.format(user))
            return HttpResponseRedirect(reverse('cae_home:user_edit', args=(user.username,)))
        else:
            # One or more forms failed to validate.
            messages.warning(request, 'Failed to update user info.')

    # Handle for non-post request.
    return TemplateResponse(request, 'cae_home/user_edit.html', {
        'forms': form_list,
        'user_model': user,
        'profile': user_profile,
        'address': address,
    })


#region DjangoRest Views

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    DjangoRest views for department model.
    """
    queryset = models.Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer
    filter_class = filters.DepartmentFilter


#endregion DjangoRest Views


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
        # Get example forms.
        form = forms.ExampleForm()
        if request.method == 'POST':
            form = forms.ExampleForm(request.POST)

        # Render template to user.
        return TemplateResponse(request, 'cae_home/css_example.html', {
            'form': form,
        })
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
