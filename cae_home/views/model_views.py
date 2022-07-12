"""
Model views for CaeHome app.
"""

# System Imports.
from django.template.response import TemplateResponse

# User Imports.
from cae_home.forms import UserLookupForm


# def get_or_add_wmu_user(request):
#     """"""
#     # Initialize form.
#     form = UserLookupForm()
#
#     # Handle for user-submitted data.
#     if request.POST:
#         # Update form.
#         form = UserLookupForm(request.POST)
#
#     return TemplateResponse(request, 'cae_home/')
