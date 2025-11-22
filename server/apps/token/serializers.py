
from rest_framework import serializers
from .models import TokenModel

class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenModel
        fields = "__all__"
        depth = 0
        
class TokenRateLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenModel
        fields = ['rate']
