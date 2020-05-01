"""
Forms for CAE Tools app.
"""

# System Imports.
from django import forms

# User Imports.
from cae_home.forms import DatePickerWidget, DateTimePickerWidget, TimePickerWidget


class ExampleForm(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.
    """
    name = forms.CharField()
    date_widget = forms.DateField(widget=DatePickerWidget)
    time_widget = forms.TimeField(widget=TimePickerWidget)
    check_me = forms.BooleanField(required=False)
