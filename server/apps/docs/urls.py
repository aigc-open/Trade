from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocsViewSet

router = DefaultRouter()
router.register(r'', DocsViewSet, basename='docs')

urlpatterns = [
    path('', include(router.urls)),
]

