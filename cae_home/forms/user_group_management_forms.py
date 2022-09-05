"""
User permission/group management forms for CAE Home app.
"""

# System Imports.
import copy
from django import forms
from django.conf import settings
from django.contrib.auth.models import Group
from django.http import QueryDict

# User Imports.
from cae_home import models
from cae_home.forms.form_widgets import Select2WidgetWithTagging, Select2MultipleWidget


class CaeCenterUserForm(forms.Form):
    user_id = forms.ChoiceField(widget=Select2WidgetWithTagging)
    groups = forms.MultipleChoiceField(widget=Select2MultipleWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_id'].label = 'Student Winno or BroncoNet:'
        self.fields['groups'].label = 'Permission Groups:'

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

        # Get group choices.
        cae_groups = Group.objects.filter(name__in=settings.CAE_CENTER_GROUPS)
        choices = [('', '')]
        for group in cae_groups:
            new_choice = (
                '{0}'.format(group.name),
                '{0}'.format(group.name),
            )
            choices.append(new_choice)
        self.fields['groups'].choices = choices

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
