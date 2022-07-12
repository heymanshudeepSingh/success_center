"""
Forms for CAE Home app.
"""

# System Imports.
from django import forms
from django.contrib.auth.forms import AuthenticationForm as auth_form

# User Imports.
from . import models


# region Custom Widgets

class DatePickerWidget(forms.DateInput):
    """
    Generic widget for Date fields.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-date-picker')
        return attrs


class TimePickerWidget(forms.TimeInput):
    """
    Generic widget for Time fields.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-time-picker')
        return attrs


class DateTimePickerWidget(forms.SplitDateTimeWidget):
    """
    Generic widget for DateTime fields.

    Note: Forms using this must set:
        field_classes = {
            '<datetime field>': forms.SplitDateTimeField,
        }
    """

    def __init__(self, attrs=None, date_attrs=None, time_attrs=None):
        if date_attrs is None:
            date_attrs = {'class': 'form-widget-date-picker'}
        if time_attrs is None:
            time_attrs = {'class': 'form-widget-time-picker'}

        super(DateTimePickerWidget, self).__init__(self, attrs, date_attrs=date_attrs, time_attrs=time_attrs)


class SelectButtonsWidget(forms.Select):
    """
    Widget for select input as clickable buttons.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-select-buttons')
        return attrs


class SelectButtonsSideWidget(forms.Select):
    """
    Widget for select input as clickable buttons.
    Displays on side of form.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-select-buttons-side')
        return attrs


class Select2Widget(forms.Select):
    """
    Widget for select2 "single selection" input.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-select2')
        return attrs


class Select2MultipleWidget(forms.SelectMultiple):
    """
    Widget for select2 "multiple selection" input.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-select2-multiple')
        attrs.setdefault('multiple', 'multiple')
        return attrs


class SignatureWidget(forms.TextInput):
    """
    Widget for signature input.

    Note:
        * This element should be a "TextField" when used in a model.
        * This element should be a "CharField" when used in a form.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'form-widget-signature-field')
        return attrs


# endregion Custom Widgets


# region Standard View Forms

class AuthenticationForm(auth_form):
    """
    Modified login page form.
    """
    remember_me = forms.BooleanField(required=False, label='Keep Me Logged In:')


class UserLookupForm(forms.Form):
    user_id = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_id'].label = 'Student Winno or Bronconet:'
        # Set datalist value, for auto-completion.
        self.fields['user_id'].widget.attrs['list'] = 'user_id_datalist'

    class Media:
        # Additional JS file definitions.
        js = ('cae_home/js/lookups.js',)


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

# endregion Standard View Forms
