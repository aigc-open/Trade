
import django_filters
from .models import TokenModel

class TokenFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = TokenModel
        fields = "__all__"

