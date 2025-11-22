from django.contrib import admin
from .models import (
    AgentMemoryModel, KnowledgeNodeModel, KnowledgeEdgeModel,
    TradingPrincipleModel, MarketPatternModel, CognitiveBiasLogModel
)


@admin.register(AgentMemoryModel)
class AgentMemoryAdmin(admin.ModelAdmin):
    """智能体记忆管理"""
    list_display = ['memory_type', 'summary', 'importance_score', 'when', 'access_count', 'is_forgotten']
    list_filter = ['memory_type', 'is_forgotten', 'created_at']
    search_fields = ['content', 'summary']
    ordering = ['-importance_score', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_accessed', 'forgotten_at']


@admin.register(KnowledgeNodeModel)
class KnowledgeNodeAdmin(admin.ModelAdmin):
    """知识节点管理"""
    list_display = ['node_id', 'node_type', 'name', 'importance', 'reference_count']
    list_filter = ['node_type']
    search_fields = ['node_id', 'name', 'description']
    ordering = ['-importance', '-reference_count']


@admin.register(KnowledgeEdgeModel)
class KnowledgeEdgeAdmin(admin.ModelAdmin):
    """知识关系管理"""
    list_display = ['from_node', 'relationship', 'to_node', 'weight', 'confidence', 'evidence_count']
    list_filter = ['relationship']
    ordering = ['-weight', '-confidence']


@admin.register(TradingPrincipleModel)
class TradingPrincipleAdmin(admin.ModelAdmin):
    """交易原则管理"""
    list_display = ['principle_type', 'title', 'source', 'success_rate', 'priority', 'is_active']
    list_filter = ['principle_type', 'source', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['-priority', '-success_rate']


@admin.register(MarketPatternModel)
class MarketPatternAdmin(admin.ModelAdmin):
    """市场模式管理"""
    list_display = ['pattern_type', 'name', 'occurrence_count', 'success_count', 'avg_return', 'confidence', 'is_active']
    list_filter = ['pattern_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-confidence', '-occurrence_count']


@admin.register(CognitiveBiasLogModel)
class CognitiveBiasLogAdmin(admin.ModelAdmin):
    """认知偏见日志管理"""
    list_display = ['bias_type', 'detected_at', 'impact_level', 'is_corrected']
    list_filter = ['bias_type', 'is_corrected', 'detected_at']
    ordering = ['-detected_at']
    date_hierarchy = 'detected_at'
