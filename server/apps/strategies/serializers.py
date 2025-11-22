from rest_framework import serializers
from .models import StrategyModel, StrategyBacktestModel

class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategyModel
        fields = "__all__"

class StrategyBacktestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategyBacktestModel
        fields = "__all__"
