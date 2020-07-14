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
    Displays examples of custom HTML/CSS layout for "forms" elements.
    """
    # Get example forms.
    form = forms.ExampleForm()
    if request.method == 'POST':
        form = forms.ExampleForm(request.POST)

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_examples/forms.html', {
        'form': form,
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
