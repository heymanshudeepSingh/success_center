"""
Misc views for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

# User Imports.
from cae_home import forms
from cae_home.decorators import group_required
from cae_home.utils import get_or_create_login_user_model, get_or_create_wmu_user_model
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


# region Error-Handling Views

def handler400(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/400.html', status=400)


def handler403(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/403.html', status=403)


def handler404(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/404.html', status=404)


def handler500(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/500.html', status=500)

# endregion Error-Handling Views


# region Public Info Views

def info_schedules(request):
    """
    Temporary page to publicly display schedules of users.
    """
    return TemplateResponse(request, 'cae_home/info_schedules.html', {})


def info_servers(request):
    """
    Temporary page to publicly display servers maintained by admins.
    """
    return TemplateResponse(request, 'cae_home/info_servers.html', {
        'contact_mandroo': 'Andrew Barnes<br>znd7233@wmich.edu',
        'contact_hussein': 'Hussein Sheakh<br>hbn2774@wmich.edu',
        'contact_kira': 'Kira Hamelink<br>kdr1002@wmich.edu',
        'contact_musaab': 'Musaab Yousif<br>myn8219@wmich.edu',
        'contact_shagun': 'Shagun Choudhary<br>sgk8005@wmich.edu',
        'contact_phillip': 'Phillip Varner<br>pgs8661@wmich.edu',
    })


def info_software(request):
    """
    Temporary page to publicly display software maintained by programmers.
    """
    return TemplateResponse(request, 'cae_home/info_software.html', {
        'contact_brandon': 'Brandon Rodriguez<br>bfp5870@wmich.edu',
        'contact_jesse': 'Jesse Meachum<br>jdc4014@wmich.edu',
        'contact_singh': 'Simar Singh<br>hfv6838@wmich.edu'
    })

# endregion Public Info Views


@login_required
@group_required(settings.CAE_CENTER_GROUPS)
def helpful_resources(request):
    """
    "Useful links" page for CAE Center employees.
    """
    return TemplateResponse(request, 'cae_home/helpful_resources.html', {})


# @method_decorator(group_required(cae_employee_groups), name='dispatch')
class GetLoginUserExample(LoginRequiredMixin, FormView):
    """
    An example of using a FormView class to check for a (Login) User model.
    If value does not exist in the Django database, then it makes a query to LDAP to search for an associated user.
    Catches errors if LDAP is not properly configured on local machine.
    """
    template_name = 'cae_home/get_login_user.html'
    form_class = forms.UserLookupForm
    success_url = reverse_lazy('cae_home:get_login_user')

    def get_context_data(self, **kwargs):
        """
        Add additional context (variables) for template to display.
        """
        context = super().get_context_data(**kwargs)

        # Check if we have a BroncoNet or Winno in our session values.
        user_id = self.request.session.pop('cae_home__user_id', None)

        # Attempt to get model.
        user_model = get_or_create_login_user_model(self.request, user_id)

        # Check if TemplateResponse object was returned.
        if isinstance(user_model, TemplateResponse):
            # TemplateResponse returned. Note that in a MethodView (instead of a ClassView),
            # this TemplateResponse object can just be returned directly as is, at this point.
            # Instead, we do extra logic here because ClassViews can be picky with where you return a TemplateResponse.
            message = 'LDAP is required to properly view this page. ' \
                      'The web server does not appear to have LDAP connections setup.'
            messages.error(self.request, message)
            logger.error(message)
            user_model = None

        context.update({
            'user_model': user_model,
        })
        return context

    def form_valid(self, form):
        """
        Logic to run on valid form data return.
        """
        user_id = form.cleaned_data['user_id']

        # Attempt to get model.
        user_model = get_or_create_login_user_model(self.request, user_id)

        # Check if TemplateResponse object was returned.
        if isinstance(user_model, TemplateResponse):
            # TemplateResponse returned. Note that in a MethodView (instead of a ClassView),
            # this TemplateResponse object can just be returned directly as is, at this point.
            # Instead, we do extra logic here because ClassViews can be picky with where you return a TemplateResponse.
            message = 'LDAP is required to properly view this page. ' \
                      'The web server does not appear to have LDAP connections setup.'
            messages.error(self.request, message)
            logger.error(message)
            user_model = None

        # Check if result was found.
        if user_model is not None:
            self.request.session['cae_home__user_id'] = user_model.username
        else:
            messages.warning(self.request, 'Provided value did not match a known BroncoNet or Winno.')

            # Display our template to user once more. Pass our form data so fields stay filled out.
            return self.render_to_response(self.get_context_data(form=form))

        return redirect(reverse_lazy('cae_home:get_login_user'))


# @method_decorator(group_required(cae_employee_groups), name='dispatch')
class GetWmuUserExample(LoginRequiredMixin, FormView):
    """
    An example of using a FormView class to check for a WmuUser model.
    If value does not exist in the Django database, then it makes a query to LDAP to search for an associated user.
    Catches errors if LDAP is not properly configured on local machine.
    """
    template_name = 'cae_home/get_wmu_user.html'
    form_class = forms.UserLookupForm
    success_url = reverse_lazy('cae_home:get_wmu_user')

    def get_context_data(self, **kwargs):
        """
        Add additional context (variables) for template to display.
        """
        context = super().get_context_data(**kwargs)

        # Check if we have a BroncoNet or Winno in our session values.
        user_id = self.request.session.pop('cae_home__user_id', None)

        # If id was present, get associated model.
        user_model = get_or_create_wmu_user_model(self.request, user_id)

        # Check if TemplateResponse object was returned.
        if isinstance(user_model, TemplateResponse):
            # TemplateResponse returned. Note that in a MethodView (instead of a ClassView),
            # this TemplateResponse object can just be returned directly as is, at this point.
            # Instead, we do extra logic here because ClassViews can be picky with where you return a TemplateResponse.
            message = 'LDAP is required to properly view this page. ' \
                      'The web server does not appear to have LDAP connections setup.'
            messages.error(self.request, message)
            logger.error(message)
            user_model = None

        context.update({
            'user_model': user_model,
        })
        return context

    def form_valid(self, form):
        """
        Logic to run on valid form data return.
        """
        # Get and validate submitted form value.
        user_id = form.cleaned_data['user_id'].strip()
        if ',' in user_id:
            user_id = user_id.split(',')[0]

        # Attempt to get model.
        user_model = get_or_create_wmu_user_model(self.request, user_id)

        # Check if TemplateResponse object was returned.
        if isinstance(user_model, TemplateResponse):
            # TemplateResponse returned. Note that in a MethodView (instead of a ClassView),
            # this TemplateResponse object can just be returned directly as is, at this point.
            # Instead, we do extra logic here because ClassViews can be picky with where you return a TemplateResponse.
            message = (
                'LDAP is required to properly view this page. '
                'The web server does not appear to have LDAP connections setup.'
            )
            messages.error(self.request, message)
            logger.error(message)
            user_model = None

        # Check if result was found.
        if user_model is not None:
            self.request.session['cae_home__user_id'] = user_model.bronco_net
        else:
            messages.warning(self.request, 'Provided value did not match a known BroncoNet or Winno.')

            # Display our template to user once more. Pass our form data so fields stay filled out.
            return self.render_to_response(self.get_context_data(form=form))

        return redirect(reverse_lazy('cae_home:get_wmu_user'))
