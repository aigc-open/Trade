from rest_framework import serializers
from .models import AgentMemoryModel, KnowledgeNodeModel

class AgentMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMemoryModel
        fields = "__all__"

class KnowledgeNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeNodeModel
        fields = "__all__"
