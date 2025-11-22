
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from .views import TokenViewSet

router = routers.DefaultRouter()
router.register(r"", TokenViewSet)

urlpatterns = [
    path("", include(router.urls)),
]


