from rest_framework import viewsets, permissions
from .models import ReviewReportModel, AlertModel
from .serializers import ReviewReportSerializer, AlertSerializer
from apps import CustomPagination

class ReviewReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewReportModel.objects.all()
    serializer_class = ReviewReportSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertModel.objects.all()
    serializer_class = AlertSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
