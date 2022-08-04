"""
Forms for CAE Home app.
"""

# System Imports.
import copy
from django import forms
from django.contrib.auth.forms import AuthenticationForm as auth_form
from django.http import QueryDict

# User Imports.
from cae_home import models
from cae_home.forms.form_widgets import Select2Widget, Select2WidgetWithTagging, Select2MultipleWidget


class AuthenticationForm(auth_form):
    """
    Modified login page form.
    """
    # Define form fields.
    remember_me = forms.BooleanField(required=False, label='Keep Me Logged In:')


class UserLookupForm(forms.Form):
    # Define form fields.
    user_id = forms.ChoiceField(widget=Select2WidgetWithTagging)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_id'].label = 'Student Winno or Bronconet:'

        # Get initial choices. Since this is an example, we get CaeCenter users.
        cae_users = models.User.get_cae_users().order_by('first_name', 'last_name')
        choices = [('', '')]
        for user in cae_users:
            new_choice = (
                '{0}, {1}'.format(user.userintermediary.bronco_net, user.userintermediary.winno),
                '{0} {1}'.format(user.first_name, user.last_name),
            )
            choices.append(new_choice)

        self.fields['user_id'].choices = choices

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


class UserModelForm(forms.ModelForm):
    """
    (Login) User model form for standard views.
    """
    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['disabled'] = True

    class Meta:
        model = models.User
        fields = (
            'username', 'first_name', 'last_name',
        )


class ChangePasswordCustomForm(forms.Form):
    """
    form to reset password for CAE center users
    """
    # Define form fields.
    current_password = forms.CharField(label="Current Password", widget=forms.PasswordInput(), required=True)
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput(), required=True)
    repeat_new_password = forms.CharField(label="Repeat New Password", widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get cleaned form data.
        cleaned_data = super().clean()

        # check if the passwords match
        if cleaned_data.get("new_password") != cleaned_data.get("repeat_new_password"):
            self.add_error('repeat_new_password', error="Passwords don't match!")


# region Profile Model Forms

class ProfileModelForm(forms.ModelForm):
    """
    User Profile model form for standard views.
    Displays all possible profile fields.
    """
    class Meta:
        model = models.Profile
        fields = (
            'address',
            'phone_number',
            'site_theme',
            'user_timezone',
            'desktop_font_size',
            'mobile_font_size',
            'fg_color',
            'bg_color',
        )
        widgets = {
            'user_timezone': Select2Widget,
        }


class ProfileModelForm_OnlyPhone(forms.ModelForm):
    """
    User Profile model form for standard views.
    Only displays phone number field.
    """
    class Meta:
        model = models.Profile
        fields = (
            'phone_number',
        )


class ProfileModelForm_OnlySiteOptions(forms.ModelForm):
    """
    User Profile model form for standard views.
    Only displays site option fields.
    """
    class Meta:
        model = models.Profile
        fields = (
            'site_theme', 'user_timezone', 'desktop_font_size', 'mobile_font_size', 'fg_color', 'bg_color',
        )
        widgets = {
            'user_timezone': Select2Widget,
        }


class ProfileModelForm_OnlySiteOptionsGA(forms.ModelForm):
    """
    GA User Profile model form for standard views.
    Only displays site option fields.
    """
    class Meta:
        model = models.Profile
        fields = (
            'site_theme',
            'user_timezone',
            'desktop_font_size',
            'mobile_font_size',
            'fg_color',
            'bg_color',
            'employee_shift_display_default',
        )
        widgets = {
            'user_timezone': Select2Widget,
        }

# endregion Profile Model Forms


class AddressModelForm(forms.ModelForm):
    """
    Address model form for standard views.
    """
    class Meta:
        model = models.Address
        fields = (
            'street', 'optional_street', 'city', 'state', 'zip',
        )


class RoomModelForm(forms.ModelForm):
    """
    Room model form for standard views.
    """
    class Meta:
        model = models.Room
        fields = (
            'name', 'department', 'room_type', 'description', 'capacity',
        )
        widgets = {
            'department': Select2MultipleWidget,
        }
