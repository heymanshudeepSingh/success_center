"""
Forms for CAE_Home App.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm as auth_form

from . import models


#region Custom Widgets

class Select2Widget(forms.Select):
    """
    Widget for select2 "single selection" input.
    """
    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set html attribute values.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', 'select2')
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
        attrs.setdefault('class', 'select2-multiple')
        attrs.setdefault('multiple', 'multiple')
        return attrs

#endregion Custom Widgets



#region Standard View Forms

class AuthenticationForm(auth_form):
    """
    Modified login page form.
    """
    remember_me = forms.BooleanField(required=False)


class ExampleForm(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.
    """
    name = forms.CharField()
    time = forms.TimeField()
    check_me = forms.BooleanField(required=False)


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



class ProfileAdminForm(forms.ModelForm):
    """
    Define admin form view for the Profile model.
    """
    class Meta:
        model = models.Profile
        fields = {
            'user', 'address', 'phone_number', 'site_theme',
        }
        label = {
            'phone_number': 'Phone Number',
            'site_theme': 'Site Theme',
        }


class AddressAdminForm(forms.ModelForm):
    """
    Define admin form view for the Address model.
    """
    class Meta:
        model = models.Address
        fields = {
            'street', 'optional_street', 'city', 'state', 'zip',
        }
        label = {
            'optional_street': 'Optional Street',
        }


class PhoneNumberAdminForm(forms.ModelForm):
    """
    Define admin form view for the Phone Number model.
    """
    class Meta:
        model = models.PhoneNumber
        fields = {
            'phone_number',
        }
        label = {
            'phone_number': 'Phone Number',
        }
