from rest_framework import viewsets, permissions
from .models import AgentMemoryModel, KnowledgeNodeModel
from .serializers import AgentMemorySerializer, KnowledgeNodeSerializer
from apps import CustomPagination

class AgentMemoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentMemoryModel.objects.all()
    serializer_class = AgentMemorySerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class KnowledgeNodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KnowledgeNodeModel.objects.all()
    serializer_class = KnowledgeNodeSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
