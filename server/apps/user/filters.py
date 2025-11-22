
import django_filters
from .models import UserModel

class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = UserModel
        fields = "__all__"

