from rest_framework import serializers
from .models import MarketDataModel, MarketIndexModel, MarketSentimentModel, NewsEventModel, StockInfoModel


class MarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketDataModel
        fields = "__all__"


class MarketIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndexModel
        fields = "__all__"


class MarketSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSentimentModel
        fields = "__all__"


class NewsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsEventModel
        fields = "__all__"


class StockInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockInfoModel
        fields = "__all__"
