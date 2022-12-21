import django_filters
from django_filters import CharFilter, ModelChoiceFilter

from .models import *


class StudentUsageFilter(django_filters.FilterSet):
    student__first_name = CharFilter(lookup_expr='icontains', label='First Name')
    student__last_name = CharFilter(lookup_expr='icontains', label='Last Name')
    student__bronco_net = CharFilter(lookup_expr='icontains', label='Bronco Net ID')

    location__location_name = ModelChoiceFilter(queryset=TutorLocations.objects.filter(is_active=True))

    # $approved = BooleanFilter()
    class Meta:
        model = StudentUsageLog
        fields = []
