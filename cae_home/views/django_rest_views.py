"""
DjangoRest views for CAE Home app.
"""

# System Imports.
from rest_framework import viewsets, permissions

# User Imports.
from cae_home import models
from cae_home.rest import filters, serializers
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)



# region DjangoRest Views

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    DjangoRest views for department model.
    """
    queryset = models.Department.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer
    filter_class = filters.DepartmentFilter

# endregion DjangoRest Views
