from django.urls import path, include
from rest_framework import routers
from .views import TradeViewSet, PositionViewSet, PortfolioViewSet

router = routers.DefaultRouter()
router.register(r"trades", TradeViewSet)
router.register(r"positions", PositionViewSet)
router.register(r"portfolio", PortfolioViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
