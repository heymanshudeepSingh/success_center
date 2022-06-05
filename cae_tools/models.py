"""
Models for CAE Tools app.
"""

# System Imports.
from django.conf import settings
from django.db import models


class GenericSignatureModel(models.Model):
    """
    Generic implementation of a Signature model.
    To be paired with the generic "signature field" form item.
    """
    signature = models.TextField(default='1')

    class Meta:
        abstract = True


class ExampleDocsSignatureModel(GenericSignatureModel):
    """
    Implementation of the above GenericSignatureModel, for example use in the cae_tools docs.

    When implementing a signature, please inherit from the above Generic class, not this one.
    This class is for example implementation purposes only.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Example Signature'
        verbose_name_plural = 'Example Signatures'
