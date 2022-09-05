"""
User permission/group management forms for CAE Home app.
"""

# System Imports.
import copy
from django import forms
from django.conf import settings
from django.contrib.auth.models import Group
from django.http import QueryDict
from django.template.response import TemplateResponse

# User Imports.
from cae_home import models
from cae_home.forms.form_widgets import Select2WidgetWithTagging, Select2MultipleWidget
from cae_home.utils import get_or_create_login_user_model
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


class CoreUserGroupManagementForm(forms.Form):
    """
    Core form for managing a given user's groups.
    This is how we select the actual user to modify.
    """
    user_id = forms.ChoiceField(widget=Select2WidgetWithTagging)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_id'].label = 'Student Winno or BroncoNet:'

        # Get initial user choices. In this case, we get existing CaeCenter users,
        # under the assumption that we're likely to edit those.
        cae_users = models.User.get_cae_users().order_by('first_name', 'last_name')
        choices = [('', '')]
        for user in cae_users:
            new_choice = (
                '{0}, {1}'.format(user.userintermediary.bronco_net, user.userintermediary.winno),
                '{0} {1}'.format(user.first_name, user.last_name),
            )
            choices.append(new_choice)
        self.fields['user_id'].choices = choices

        # Dynamic handling for if a user was submitted that wasn't in our initial list.
        # Handle if form data was submitted.
        data = kwargs.pop('data', None)
        # For some reason as of summer 2022, request.POST seems to be occasionally submitting as a tuple (via args)
        # instead of the expected dict (via kwargs). This is a workaround for being able to get data in either case.
        if data is None and len(args) > 0:
            for arg in args:
                if isinstance(arg, QueryDict):
                    data = arg

        if data:
            # Data was submitted. Get the field value.
            form_data = copy.deepcopy(data)
            user_id = form_data.pop('user_id', None)
            if (isinstance(user_id, list) or isinstance(user_id, tuple)) and len(user_id) > 0:
                user_id = user_id[0]

            # If field value is non-empty, then modify our select2 "allowed choices" to include this field.
            if user_id is not None:
                self.fields['user_id'].choices.append((user_id, user_id))

    def clean_user_id(self):
        # Get submitted form value.
        value = self.cleaned_data['user_id']
        value = value.split(', ')[0].strip()

        # Attempt to find corresponding (Login)User model, either via BroncoNet or Winno.
        user_model = get_or_create_login_user_model(None, value)

        # Check if value returned proper User instance. If not, assume invalid.
        if user_model is None or isinstance(user_model, TemplateResponse):
            self.add_error('user_id', 'Unknown user of "{0}".'.format(value))

        # Return original input value.
        return value


class CaeGroupManagementForm(forms.Form):
    """
    Form for managing a user's CAE Center access privileges.
    """
    cae_groups = forms.MultipleChoiceField(widget=Select2MultipleWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cae_groups'].label = 'CAE Permission Groups:'

        # Get group choices.
        cae_groups = Group.objects.filter(name__in=settings.CAE_CENTER_GROUPS)
        choices = [('', '')]
        for group in cae_groups:
            new_choice = (
                '{0}'.format(group.name),
                '{0}'.format(group.name),
            )
            choices.append(new_choice)
        self.fields['cae_groups'].choices = choices


class GradAppsGroupManagementForm(forms.Form):
    """
    Form for managing a user's GradApps access privileges.
    """
    grad_apps_groups = forms.MultipleChoiceField(widget=Select2MultipleWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['grad_apps_groups'].label = 'GradApps Permission Groups:'

        # Get group choices.
        cae_groups = Group.objects.filter(name__in=settings.GRAD_APPS_GROUPS)
        choices = [('', '')]
        for group in cae_groups:
            new_choice = (
                '{0}'.format(group.name),
                '{0}'.format(group.name),
            )
            choices.append(new_choice)
        self.fields['grad_apps_groups'].choices = choices


class SuccessCtrGroupManagementForm(forms.Form):
    """
    Form for managing a user's SuccessCenter access privileges.
    """
    success_ctr_groups = forms.MultipleChoiceField(widget=Select2MultipleWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['success_ctr_groups'].label = 'SuccessCtr Permission Groups:'

        # Get group choices.
        cae_groups = Group.objects.filter(name__in=settings.SUCCESS_CENTER_GROUPS)
        choices = [('', '')]
        for group in cae_groups:
            new_choice = (
                '{0}'.format(group.name),
                '{0}'.format(group.name),
            )
            choices.append(new_choice)
        self.fields['success_ctr_groups'].choices = choices
