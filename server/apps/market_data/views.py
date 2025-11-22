from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import MarketDataModel, MarketIndexModel, MarketSentimentModel, NewsEventModel, StockInfoModel
from .serializers import (
    MarketDataSerializer, MarketIndexSerializer, MarketSentimentSerializer,
    NewsEventSerializer, StockInfoSerializer
)
from apps import CustomPagination

_tag = "Market Data"


class MarketDataViewSet(viewsets.ReadOnlyModelViewSet):
    """市场行情数据 API"""
    queryset = MarketDataModel.objects.all()
    serializer_class = MarketDataSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['symbol', 'market']
    search_fields = ['symbol']
    ordering_fields = ['timestamp']


class MarketIndexViewSet(viewsets.ReadOnlyModelViewSet):
    """市场指数 API"""
    queryset = MarketIndexModel.objects.all()
    serializer_class = MarketIndexSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MarketSentimentViewSet(viewsets.ReadOnlyModelViewSet):
    """市场情绪 API"""
    queryset = MarketSentimentModel.objects.all()
    serializer_class = MarketSentimentSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class NewsEventViewSet(viewsets.ReadOnlyModelViewSet):
    """新闻事件 API"""
    queryset = NewsEventModel.objects.all()
    serializer_class = NewsEventSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_level']
    ordering_fields = ['published_at']


class StockInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """股票信息 API"""
    queryset = StockInfoModel.objects.all()
    serializer_class = StockInfoSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['market', 'industry']
    search_fields = ['symbol', 'name']
