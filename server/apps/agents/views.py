from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import AgentStatusModel, TradingPlanModel, DecisionRecordModel, MarketOpportunityModel
from .serializers import (
    AgentStatusSerializer, TradingPlanSerializer, 
    DecisionRecordSerializer, MarketOpportunitySerializer
)
from apps import CustomPagination


class AgentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """智能体状态 API"""
    queryset = AgentStatusModel.objects.all()
    serializer_class = AgentStatusSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TradingPlanViewSet(viewsets.ModelViewSet):
    """交易计划 API"""
    queryset = TradingPlanModel.objects.all()
    serializer_class = TradingPlanSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan_type', 'status']
    ordering_fields = ['plan_date']


class DecisionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """决策记录 API"""
    queryset = DecisionRecordModel.objects.all()
    serializer_class = DecisionRecordSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['decision_type', 'symbol', 'is_executed']
    search_fields = ['symbol']
    ordering_fields = ['decision_time']


class MarketOpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    """市场机会 API"""
    queryset = MarketOpportunityModel.objects.all()
    serializer_class = MarketOpportunitySerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['opportunity_type', 'status']
    search_fields = ['symbol']
    ordering_fields = ['identified_at']
