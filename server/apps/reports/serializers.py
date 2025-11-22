from rest_framework import serializers
from .models import ReviewReportModel, AlertModel

class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReportModel
        fields = "__all__"

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertModel
        fields = "__all__"
