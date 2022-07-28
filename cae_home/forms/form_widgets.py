

# region Custom Widgets
"""
Forms for CAE Home app.
"""

# System Imports.
from django import forms


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
