"""
Forms for Success Center app.
"""

# System Imports.
from django import forms

# User Imports.
from apps.Success_Center.success_center_core import models
from cae_home import forms as cae_home_forms
from cae_home import models as cae_home_models


class StudentLookupForm(forms.Form):
    student_id = forms.CharField(
        label='Student Winno or Bronconet:',
        widget=forms.PasswordInput(attrs={'autofocus': 'autofocus'}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StudentLogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit most fields to be readonly.
        self.fields['bronco_net'].widget = forms.HiddenInput()
        self.fields['winno'].widget = forms.HiddenInput()
        self.fields['first_name'].widget = forms.HiddenInput()
        self.fields['middle_name'].widget = forms.HiddenInput()
        self.fields['last_name'].widget = forms.HiddenInput()
        self.fields['official_email'].widget = forms.HiddenInput()

    class Meta:
        model = cae_home_models.WmuUser
        fields = [
            'bronco_net',
            'winno',
            'first_name',
            'middle_name',
            'last_name',
            'official_email',
        ]


class AddNewStudent(forms.Form):
    model = cae_home_models.User
    user = forms.CharField(label='Bronco net')
    is_active = forms.BooleanField(label='Is Active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StudentUsageForm(forms.ModelForm):
    class Meta:
        model = models.StudentUsageLog
        fields = ['location', 'check_in', 'check_out', 'approved', ]
        exclude = ['student']
        widgets = {
            'check_in': cae_home_forms.DateTimePickerWidget,
            'check_out': cae_home_forms.DateTimePickerWidget,
        }
        field_classes = {
            'check_in': forms.SplitDateTimeField,
            'check_out': forms.SplitDateTimeField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StudentUsageAddForm(forms.ModelForm):
    class Meta:
        model = models.StudentUsageLog
        fields = ['student', 'location', 'check_in', 'check_out']
        widgets = {
            'check_in': cae_home_forms.DateTimePickerWidget,
            'check_out': cae_home_forms.DateTimePickerWidget,
        }
        field_classes = {
            'check_in': forms.SplitDateTimeField,
            'check_out': forms.SplitDateTimeField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EditUserForm(forms.Form):
    username = forms.CharField(disabled=True)
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)
    email = forms.EmailField(disabled=True)
    location = forms.ModelChoiceField(queryset=models.TutorLocations.objects.filter(is_active=True))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EditLocationForm(forms.ModelForm):
    class Meta:
        model = models.TutorLocations
        fields = ['location_name', 'room_number', 'is_active', 'is_event']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AddLocationForm(forms.ModelForm):
    location_name = forms.CharField(max_length=80, disabled=False, required=True)
    room_number = forms.CharField(max_length=80, disabled=False, required=True)

    class Meta:
        model = models.TutorLocations
        fields = [
            'location_name',
            'room_number',
            'is_active',
            'is_event',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['room_number'].widget = forms.NumberInput()


class ProfileModelForm_DefaultLocation(forms.ModelForm):
    """
    User Profile model form for setting SuccessCenter default TutorLocation.
    See CaeHome for other related User Profile logic.

    (This has to be separate, kept in a separate form, so that CaeWorkspace does not rely on having the
    SuccessCtr project installed.)
    """
    class Meta:
        model = models.SuccessCtrProfile
        fields = (
            'default_tutor_location',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['default_tutor_location'].label = 'Tutor Location:'
        self.fields['default_tutor_location'].queryset = models.TutorLocations.objects.filter(is_active=True)
