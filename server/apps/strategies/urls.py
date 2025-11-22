from django.urls import path, include
from rest_framework import routers
from .views import StrategyViewSet, StrategyBacktestViewSet

router = routers.DefaultRouter()
router.register(r"", StrategyViewSet)
router.register(r"backtests", StrategyBacktestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
