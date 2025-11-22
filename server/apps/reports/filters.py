
import django_filters
from .models import ReportsModel

class ReportsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ReportsModel
        fields = "__all__"

