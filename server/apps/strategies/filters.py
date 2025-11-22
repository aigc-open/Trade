
import django_filters
from .models import StrategiesModel

class StrategiesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = StrategiesModel
        fields = "__all__"

