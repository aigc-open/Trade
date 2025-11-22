import django_filters
from .models import MarketDataModel, MarketIndexModel, NewsEventModel, StockInfoModel


class MarketDataFilter(django_filters.FilterSet):
    """市场数据过滤器"""
    symbol = django_filters.CharFilter(field_name='symbol', lookup_expr='iexact')
    market = django_filters.ChoiceFilter(choices=MarketDataModel._meta.get_field('market').choices)
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    change_pct_min = django_filters.NumberFilter(field_name='change_pct', lookup_expr='gte')
    change_pct_max = django_filters.NumberFilter(field_name='change_pct', lookup_expr='lte')

    class Meta:
        model = MarketDataModel
        fields = ['symbol', 'market', 'data_source']


class MarketIndexFilter(django_filters.FilterSet):
    """市场指数过滤器"""
    index_code = django_filters.CharFilter(lookup_expr='icontains')
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = MarketIndexModel
        fields = ['index_code']


class NewsEventFilter(django_filters.FilterSet):
    """新闻事件过滤器"""
    source = django_filters.CharFilter(lookup_expr='icontains')
    event_level_min = django_filters.NumberFilter(field_name='event_level', lookup_expr='gte')
    published_after = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = NewsEventModel
        fields = ['source', 'event_level']


class StockInfoFilter(django_filters.FilterSet):
    """股票信息过滤器"""
    market = django_filters.CharFilter(lookup_expr='iexact')
    industry = django_filters.CharFilter(lookup_expr='icontains')
    sector = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = StockInfoModel
        fields = ['market', 'industry', 'sector', 'is_active']
