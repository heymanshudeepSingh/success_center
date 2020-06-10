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


def css_examples(request):
    """
    Displays examples of custom HTML/CSS layout and stylings used in site.
    """
    # Get example forms.
    form = forms.ExampleForm()
    if request.method == 'POST':
        form = forms.ExampleForm(request.POST)

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/css_example.html', {
        'form': form,
    })


def css_page_tabbing(request):
    """
    Displays examples of custom HTML/CSS layout for "page tabbing" elements.
    """
    return TemplateResponse(request, 'cae_tools/css_examples/page_tabbing.html', {})


def color_tool(request):
    """
    Color tool.
    """
    return TemplateResponse(request, 'cae_tools/color_tool.html', {})
