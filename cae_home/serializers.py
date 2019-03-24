"""
Serializers for CAE_Home App.
Used in DjangoRest views.
"""

from rest_framework import serializers

from . import models


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Department model.
    """
    class Meta:
        model = models.Department
        fields = ('name',)
