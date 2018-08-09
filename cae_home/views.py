"""
Views for CAE_Home App.
"""

from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from . import forms


def index(request):
    """
    Root site index. Displays links to all added sub-projects.
    """
    return TemplateResponse(request, 'cae_home/index.html', {})


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



def wmu_test(request):
    """
    "WMU clone" test page. Used for development of imitation WMU layout.
    """
    return TemplateResponse(request, 'wmu_home/index.html', {})
