from django.urls import path, include
from rest_framework import routers
from .views import (
    MarketDataViewSet, MarketIndexViewSet, MarketSentimentViewSet,
    NewsEventViewSet, StockInfoViewSet
)

router = routers.DefaultRouter()
router.register(r"data", MarketDataViewSet)
router.register(r"indices", MarketIndexViewSet)
router.register(r"sentiment", MarketSentimentViewSet)
router.register(r"news", NewsEventViewSet)
router.register(r"stocks", StockInfoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
