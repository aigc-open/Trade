from rest_framework import viewsets, permissions
from .models import StrategyModel, StrategyBacktestModel
from .serializers import StrategySerializer, StrategyBacktestSerializer
from apps import CustomPagination

class StrategyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StrategyModel.objects.all()
    serializer_class = StrategySerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StrategyBacktestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StrategyBacktestModel.objects.all()
    serializer_class = StrategyBacktestSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
