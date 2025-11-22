from django.urls import path, include
from rest_framework import routers
from .views import (
    AgentStatusViewSet, TradingPlanViewSet, 
    DecisionRecordViewSet, MarketOpportunityViewSet
)

router = routers.DefaultRouter()
router.register(r"status", AgentStatusViewSet)
router.register(r"plans", TradingPlanViewSet)
router.register(r"decisions", DecisionRecordViewSet)
router.register(r"opportunities", MarketOpportunityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
