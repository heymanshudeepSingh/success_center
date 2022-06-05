"""
"Models" documentation views for CAE Tools app.
"""

# System Imports.
import copy

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse

# User Imports.
from cae_tools import forms, models


def docs_models(request):
    """
    Documentation of custom "Model" logic in project.
    """
    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/models.html', {})


def docs_models_signature(request):
    """
    Documentation of custom "SignatureField" model logic.
    Saves to database.
    """
    # Only try to render form if user is logged in.
    form = None
    if request.user.is_authenticated:
        # User is logged in. Initialize form.
        try:
            user = request.user
            signature_instance = models.ExampleDocsSignatureModel.objects.get(user=user)
        except models.ExampleDocsSignatureModel.DoesNotExist:
            # No model saved yet. Render blank signature form.
            user = None
            signature_instance = None
        form = forms.ModelExampleForm_Signature(instance=signature_instance)

        # Handle post request.
        if request.method == 'POST':
            # data = copy.deepcopy(request.POST)
            # data['user'] = user.id if user else None
            form = forms.ModelExampleForm_Signature(instance=signature_instance, data=request.POST)

            # Validate form.
            if form.is_valid():
                # Form is valid. Save.
                signature_model = form.save(commit=False)
                signature_model.user = request.user
                signature_model.save()

                # Render response for user.
                messages.success(request, 'Successfully submitted signature.')
                return HttpResponseRedirect(reverse('cae_tools:documentation_models_signature'))

            else:
                messages.error(request, 'Error submitting signature.')

    # Render template to user.
    return TemplateResponse(request, 'cae_tools/documentation/models/signature.html', {
        'form': form,
    })
