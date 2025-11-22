from rest_framework import serializers
from .models import AgentStatusModel, TradingPlanModel, DecisionRecordModel, MarketOpportunityModel


class AgentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStatusModel
        fields = "__all__"


class TradingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingPlanModel
        fields = "__all__"


class DecisionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionRecordModel
        fields = "__all__"


class MarketOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketOpportunityModel
        fields = "__all__"
