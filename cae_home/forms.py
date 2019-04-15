"""
Forms for CAE_Home App.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm as auth_form

from . import models


#region Custom Widgets

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


class Select2MultipleWidget(forms.Select):
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

#endregion Custom Widgets



#region Standard View Forms

class AuthenticationForm(auth_form):
    """
    Modified login page form.
    """
    remember_me = forms.BooleanField(required=False, label='Keep Me Logged In:')


class ExampleForm(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.
    """
    name = forms.CharField()
    date_widget = forms.DateField(widget=DatePickerWidget)
    time_widget = forms.TimeField(widget=TimePickerWidget)
    check_me = forms.BooleanField(required=False)


class UserForm(forms.ModelForm):
    """
    (Login) User model form for standard views.
    """
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['disabled'] = True

    class Meta:
        model = models.User
        fields = (
            'username', 'first_name', 'last_name',
        )


class ProfileForm(forms.ModelForm):
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


class ProfileForm_OnlyPhone(forms.ModelForm):
    """
    User Profile model form for standard views.
    Only displays phone number field.
    """
    class Meta:
        model = models.Profile
        fields = (
            'phone_number',
        )


class ProfileForm_OnlySiteOptions(forms.ModelForm):
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


class AddressForm(forms.ModelForm):
    """
    Address model form for standard views.
    """
    class Meta:
        model = models.Address
        fields = (
            'street', 'optional_street', 'city', 'state', 'zip',
        )


class RoomForm(forms.ModelForm):
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

#endregion Standard View Forms
