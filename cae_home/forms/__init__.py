"""
Imports view logic for Core "forms" folder.
Makes project imports to this folder behave like a standard single file.
"""


from .form_widgets import (
    DatePickerWidget,
    TimePickerWidget,
    DateTimePickerWidget,
    SelectButtonsWidget,
    SelectButtonsSideWidget,
    Select2Widget,
    Select2WidgetWithTagging,
    Select2MultipleWidget,
    SignatureWidget,
)


from .general_forms import (
    AuthenticationForm,
    UserLookupForm,
    UserModelForm,
    ChangePasswordCustomForm,
    ProfileModelForm,
    ProfileModelForm_OnlyPhone,
    ProfileModelForm_OnlySiteOptions,
    ProfileModelForm_OnlySiteOptionsGA,
    AddressModelForm,
    RoomModelForm,
)


from .user_group_management_forms import (
    CaeCenterUserForm,
)
