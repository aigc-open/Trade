import django_filters
from .models import TradingPlanModel, DecisionRecordModel, MarketOpportunityModel


class TradingPlanFilter(django_filters.FilterSet):
    """交易计划过滤器"""
    plan_type = django_filters.ChoiceFilter(choices=TradingPlanModel._meta.get_field('plan_type').choices)
    status = django_filters.ChoiceFilter(choices=TradingPlanModel._meta.get_field('status').choices)
    plan_date_after = django_filters.DateFilter(field_name='plan_date', lookup_expr='gte')
    plan_date_before = django_filters.DateFilter(field_name='plan_date', lookup_expr='lte')
    
    class Meta:
        model = TradingPlanModel
        fields = ['plan_type', 'status']


class DecisionRecordFilter(django_filters.FilterSet):
    """决策记录过滤器"""
    symbol = django_filters.CharFilter(lookup_expr='iexact')
    decision_type = django_filters.ChoiceFilter(choices=DecisionRecordModel._meta.get_field('decision_type').choices)
    confidence_level = django_filters.ChoiceFilter(choices=DecisionRecordModel._meta.get_field('confidence_level').choices)
    is_executed = django_filters.BooleanFilter()
    decision_time_after = django_filters.DateTimeFilter(field_name='decision_time', lookup_expr='gte')
    decision_time_before = django_filters.DateTimeFilter(field_name='decision_time', lookup_expr='lte')
    
    class Meta:
        model = DecisionRecordModel
        fields = ['symbol', 'decision_type', 'is_executed']


class MarketOpportunityFilter(django_filters.FilterSet):
    """市场机会过滤器"""
    symbol = django_filters.CharFilter(lookup_expr='iexact')
    opportunity_type = django_filters.ChoiceFilter(choices=MarketOpportunityModel._meta.get_field('opportunity_type').choices)
    status = django_filters.ChoiceFilter(choices=MarketOpportunityModel._meta.get_field('status').choices)
    risk_level_min = django_filters.NumberFilter(field_name='risk_level', lookup_expr='gte')
    risk_level_max = django_filters.NumberFilter(field_name='risk_level', lookup_expr='lte')
    
    class Meta:
        model = MarketOpportunityModel
        fields = ['symbol', 'opportunity_type', 'status']
