import django_filters
from .models import TradeModel, PositionModel, PortfolioModel


class TradeFilter(django_filters.FilterSet):
    """交易记录过滤器"""
    symbol = django_filters.CharFilter(lookup_expr='iexact')
    action = django_filters.ChoiceFilter(choices=TradeModel._meta.get_field('action').choices)
    status = django_filters.ChoiceFilter(choices=TradeModel._meta.get_field('status').choices)
    account_type = django_filters.ChoiceFilter(choices=TradeModel._meta.get_field('account_type').choices)
    order_time_after = django_filters.DateTimeFilter(field_name='order_time', lookup_expr='gte')
    order_time_before = django_filters.DateTimeFilter(field_name='order_time', lookup_expr='lte')
    
    class Meta:
        model = TradeModel
        fields = ['symbol', 'action', 'status', 'account_type']


class PositionFilter(django_filters.FilterSet):
    """持仓过滤器"""
    symbol = django_filters.CharFilter(lookup_expr='iexact')
    account_type = django_filters.ChoiceFilter(choices=PositionModel._meta.get_field('account_type').choices)
    is_closed = django_filters.BooleanFilter()
    
    class Meta:
        model = PositionModel
        fields = ['symbol', 'account_type', 'is_closed']


class PortfolioFilter(django_filters.FilterSet):
    """投资组合过滤器"""
    account_type = django_filters.ChoiceFilter(choices=PortfolioModel._meta.get_field('account_type').choices)
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = PortfolioModel
        fields = ['account_type', 'is_active']
