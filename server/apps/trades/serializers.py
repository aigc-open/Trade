from rest_framework import serializers
from .models import TradeModel, PositionModel, PortfolioModel

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeModel
        fields = "__all__"

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionModel
        fields = "__all__"

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioModel
        fields = "__all__"
