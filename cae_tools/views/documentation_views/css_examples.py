"""
CSS Example views for CAE Tools app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.
from cae_tools import forms


def css_examples(request):
    """
    Main page for examples of custom HTML/CSS layout and stylings provided by CAE Workspace.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples.html', {})


def css_alerts(request):
    """
    Displays examples of custom HTML/CSS layout for "alert" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/alerts.html', {})


def css_articles(request):
    """
    Displays examples of custom HTML/CSS layout for "article" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/articles.html', {})


def css_buttons(request):
    """
    Displays examples of custom HTML/CSS layout for "button" elements.
    """
    return TemplateResponse(request, 'cae_tools/css_examples/buttons.html', {})


def css_card(request):
    """
    Displays examples of custom HTML/CSS layout for "card" elements.
    """
    from cae_home import models as cae_home_models
    wmu_user = cae_home_models.WmuUser.objects.get(bronco_net="fgn1003")
    # wmu_user_major = cae_home_models.Major.objects.filter(wmuuser=wmu_user, is_active=True)
    wmu_user_major = wmu_user.major.filter(is_active=True)
    # grad_app = grad_app_model.objects.filter(wmuuser = wmuuser)
    return TemplateResponse(request, 'cae_tools/css_examples/card.html', {
        "wmu_user": wmu_user,
        'wmu_user_major': wmu_user_major,
        # "grad_app": grad_app,
    })


# region Form Example Views

def css_forms(request):
    """
    Displays examples of custom HTML/CSS layout for "form" elements.
    """
    # Get example forms.
    form = forms.BaseExampleForm()
    if request.method == 'POST':
        form = forms.BaseExampleForm(request.POST)

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/form.html', {
        'form': form,
    })


def css_forms_default_fields(request):
    """
    Displays examples of custom HTML/CSS layout for various default "form field" elements.
    """
    # Get example forms.
    text_form = forms.DefaultFieldExampleForm_TextFields()
    text_form_uncommon = forms.DefaultFieldExampleForm_TextFieldsUncommon()
    number_form = forms.DefaultFieldExampleForm_NumberFields()
    number_form_adjusted = forms.DefaultFieldExampleForm_NumberFieldsAdjusted()
    date_form = forms.DefaultFieldExampleForm_DateFields()
    date_form_adjusted = forms.DefaultFieldExampleForm_DateFieldsAdjusted()
    choice_form = forms.DefaultFieldExampleForm_ChoiceFields()
    misc_form = forms.DefaultFieldExampleForm_MiscFields()

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/default_fields.html', {
        'text_form': text_form,
        'text_form_uncommon': text_form_uncommon,
        'number_form': number_form,
        'number_form_adjusted': number_form_adjusted,
        'date_form': date_form,
        'date_form_adjusted': date_form_adjusted,
        'choice_form': choice_form,
        'misc_form': misc_form,
    })


def css_forms_custom_fields(request):
    """
    Displays examples of custom HTML/CSS layout for various custom "form field" elements.
    """
    # Get example forms.
    datetime_form = forms.CustomFieldExampleForm_DateWidgets()
    select_buttons_form = forms.CustomFieldExampleForm_SelectButtons()
    select_buttons_side_form = forms.CustomFieldExampleForm_SelectButtonsSide()
    select2_form = forms.CustomFieldExampleForm_Select2()
    signature_form = forms.CustomFieldExampleForm_Signature()

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/custom_fields.html', {
        'datetime_form': datetime_form,
        'select_buttons_form': select_buttons_form,
        'select_buttons_side_form': select_buttons_side_form,
        'select2_form': select2_form,
        'signature_form': signature_form,
    })


def css_forms_misc(request):
    """
    Displays examples of custom HTML/CSS layout for all other form-related elements that don't fit in the above views.
    """
    # Get example forms.

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/misc.html', {

    })


# endregion Form Example Views


def css_nav(request):
    """
    Displays examples of custom HTML/CSS layout for "nav" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/nav.html', {})


def css_page_tabbing(request):
    """
    Displays examples of custom HTML/CSS layout for "page tabbing" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/page_tabbing.html', {})


def css_panels(request):
    """
    Displays examples of custom HTML/CSS layout for "panel" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/panels.html', {})


def css_status_messages(request):
    """
    Displays examples of custom HTML/CSS layout for "status message" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/status_messages.html', {})


def css_tables(request):
    """
    Displays examples of custom HTML/CSS layout for "table" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/tables.html', {})


def css_text_highlighting(request):
    """
    Displays examples of custom HTML/CSS layout for "text highlight" elements.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/text_highlighting.html', {})
