from django.urls import path, include
from rest_framework import routers
from .views import AgentMemoryViewSet, KnowledgeNodeViewSet

router = routers.DefaultRouter()
router.register(r"memories", AgentMemoryViewSet)
router.register(r"knowledge", KnowledgeNodeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
