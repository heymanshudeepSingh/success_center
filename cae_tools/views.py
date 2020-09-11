"""
Views for CAE Tools app.
"""

# System Imports.
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# User Imports.
from . import forms


def index(request):
    """
    CAE Tools index.
    Currently only redirects to color tool
    """
    return redirect('cae_tools:color_tool')


#region CSS Example Views

def css_examples(request):
    """
    Main page for examples of custom HTML/CSS layout and stylings provided by CAE Workspace.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_example.html', {})


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

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/custom_fields.html', {
        'datetime_form': datetime_form,
        'select_buttons_form': select_buttons_form,
        'select_buttons_side_form': select_buttons_side_form,
        'select2_form': select2_form,
    })


def css_forms_misc(request):
    """
    Displays examples of custom HTML/CSS layout for all other form-related elements that don't fit in the above views.
    """
    # Get example forms.

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms/misc.html', {

    })


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

#endregion CSS Example Views


def color_tool(request):
    """
    Color tool.
    """
    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
