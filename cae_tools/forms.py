"""
Forms for CAE Tools app.
"""

# System Imports.
from django import forms

# User Imports.
from cae_home import forms as cae_home_forms

# Create choices tuple. Used for select/choice fields down below.
CHOICES = (
    (1, 'Choice 1'),
    (2, 'Choice 2'),
    (3, 'Choice 3'),
    (4, 'Choice 4'),
    (5, 'Choice 5'),
)


class BaseExampleForm(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has a few randomly chosen fields, to show how a standard, basic form may look.
    """
    name = forms.CharField()
    date_widget = forms.DateField(widget=cae_home_forms.DatePickerWidget)
    time_widget = forms.TimeField(widget=cae_home_forms.DatePickerWidget)
    check_me = forms.BooleanField(required=False)


class DefaultFieldExampleForm_TextFields(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has the most common text fields.
    """
    char_field_example = forms.CharField()
    text_field_example = forms.CharField(widget=forms.Textarea)


class DefaultFieldExampleForm_TextFieldsUncommon(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has all less common text fields.
    """
    regex_field_example = forms.RegexField(r'[a-zA-Z0-9]')  # Checks for standard letters and numbers.
    email_field_example = forms.EmailField()
    slug_field_example = forms.SlugField()
    url_field_example = forms.URLField()


class DefaultFieldExampleForm_NumberFields(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has numeric-related fields.
    """
    integer_field_example = forms.IntegerField()
    decimal_field_example = forms.DecimalField()
    float_field_example = forms.FloatField()


class DefaultFieldExampleForm_NumberFieldsAdjusted(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has more user-friendly numeric-related fields.
    """
    integer_field_example = forms.IntegerField()
    decimal_field_example = forms.DecimalField(decimal_places=2, max_digits=4)
    float_field_example = forms.FloatField(min_value=-1, max_value=1, widget=forms.NumberInput(attrs={'step': '0.1'}))


class DefaultFieldExampleForm_DateFields(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has date/time related fields.
    """
    date_field_example = forms.DateField()
    datetime_field_example = forms.DateTimeField()
    time_field_example = forms.TimeField()


class DefaultFieldExampleForm_DateFieldsAdjusted(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has very minorly more user-friendly date/time related fields.
    """
    date_field_example = forms.DateField(widget=forms.SelectDateWidget)
    datetime_field_example = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    time_field_example = forms.TimeField()


class DefaultFieldExampleForm_ChoiceFields(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has choice/selection related fields.
    """
    choice_field_example = forms.ChoiceField(choices=CHOICES)
    typed_choice_field_example = forms.TypedChoiceField(choices=CHOICES)
    multiple_choice_field_example = forms.MultipleChoiceField(choices=CHOICES)
    typed_multiple_choice_field_example = forms.TypedMultipleChoiceField(choices=CHOICES)


class DefaultFieldExampleForm_MiscFields(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has all other fields that didn't fit in the above fieldsets.
    """
    boolean_field_example = forms.BooleanField()
    null_boolean_field_example = forms.NullBooleanField()
    duration_field_example = forms.DurationField()
    file_field_example = forms.FileField()
    # filepath_field_example = forms.FilePathField()
    image_field_example = forms.ImageField()
    generic_ip_address_field_example = forms.GenericIPAddressField()
    uuid_field_example = forms.UUIDField()


class CustomFieldExampleForm_DateWidgets(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has date-related custom-made form fields, provided by this workspace project.
    """
    reference_char_field = forms.CharField()
    reference_text_field = forms.CharField(widget=forms.Textarea)
    date_widget_example = forms.DateField(widget=cae_home_forms.DatePickerWidget)
    time_widget_example = forms.TimeField(widget=cae_home_forms.TimePickerWidget)
    date_time_widget_example = forms.DateTimeField(widget=cae_home_forms.DateTimePickerWidget())


class CustomFieldExampleForm_SelectButtons(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has "select button"-related custom-made form fields, provided by this workspace project.
    """
    reference_char_field = forms.CharField()
    reference_text_field = forms.CharField(widget=forms.Textarea)
    select_button_widget_example = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=cae_home_forms.SelectButtonsWidget,
    )


class CustomFieldExampleForm_SelectButtonsSide(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has "side select button"-related custom-made form fields, provided by this workspace project.
    """
    reference_char_field = forms.CharField()
    reference_text_field = forms.CharField(widget=forms.Textarea)
    select_button_side_widget_example = forms.ChoiceField(
        choices=CHOICES,
        widget=cae_home_forms.SelectButtonsSideWidget,
    )


class CustomFieldExampleForm_Select2(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has "select2"-related custom-made form fields, provided by this workspace project.
    """
    reference_char_field = forms.CharField()
    reference_text_field = forms.CharField(widget=forms.Textarea)
    select2_widget_example = forms.ChoiceField(
        choices=CHOICES,
        widget=cae_home_forms.Select2Widget,
    )
    select2_multiple_widget_example = forms.ChoiceField(
        choices=CHOICES,
        widget=cae_home_forms.Select2MultipleWidget,
    )


class CustomFieldExampleForm_Signature(forms.Form):
    """
    An example form, used in the css examples page.
    Should not actually submit any data.

    Has signature-related custom-made form fields, provided by this workspace project.
    """
    reference_char_field = forms.CharField()
    reference_text_field = forms.CharField(widget=forms.Textarea)
    signature = forms.CharField(widget=cae_home_forms.SignatureWidget)


class LdapUtilityForm(forms.Form):
    """
    Ldap form to search for user info
    """
    search_choices = [
        ("wmuUID", "Bronco Net"),
        ("mail", "Email"),
        ("cn", "Full Name"),
        ("wmuBannerID", "Win Number"),
        ("homePhone", "Phone Number"),
    ]
    search_choice_field = forms.CharField(label='Search By', widget=forms.Select(choices=search_choices))
    search_input = forms.CharField(label="Value", max_length=60)


class CaePasswordResetForm(forms.Form):
    """
    form to reset password for CAE center users
    """
    user_id = forms.CharField(label="User ID", max_length=60, required=True)
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
        if cleaned_data["new_password"] != cleaned_data["repeat_new_password"]:
            self.add_error(self, "Passwords don't match!")
