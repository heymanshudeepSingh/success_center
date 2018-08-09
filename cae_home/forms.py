"""
Forms for CAE_Home App.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm as auth_form

from . import models


class AuthenticationForm(auth_form):
    """
    Modified login page form.
    """
    remember_me = forms.BooleanField(required=False)


class ProfileAdminForm(forms.ModelForm):
    """
    Define admin form view for the Profile model.
    """
    class Meta:
        model = models.Profile
        fields = {
            'user', 'address', 'phone_number',
        }
        label = {
            'phone_number': 'Phone Number',
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
