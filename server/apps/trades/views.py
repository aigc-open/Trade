from rest_framework import viewsets, permissions
from .models import TradeModel, PositionModel, PortfolioModel
from .serializers import TradeSerializer, PositionSerializer, PortfolioSerializer
from apps import CustomPagination

class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TradeModel.objects.all()
    serializer_class = TradeSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PositionModel.objects.all()
    serializer_class = PositionSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PortfolioModel.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
