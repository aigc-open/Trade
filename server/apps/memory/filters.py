
import django_filters
from .models import MemoryModel

class MemoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = MemoryModel
        fields = "__all__"

