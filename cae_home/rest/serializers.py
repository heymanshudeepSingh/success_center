"""
Serializers for CAE Home app.
Used in DjangoRest views.
"""

# System Imports.
from rest_framework import serializers

# User Class Imports.
from cae_home import models


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Department model.
    """
    class Meta:
        model = models.Department
        fields = ('name',)
