from django.contrib import admin
from .models import (
    ReviewReportModel, EvolutionReportModel, 
    PerformanceMetricsModel, AlertModel, SimulationComparisonModel
)


@admin.register(ReviewReportModel)
class ReviewReportAdmin(admin.ModelAdmin):
    """复盘报告管理"""
    list_display = ['report_date', 'report_type', 'total_return', 'win_rate', 'sharpe_ratio', 'is_published']
    list_filter = ['report_type', 'is_published', 'report_date']
    ordering = ['-report_date']
    date_hierarchy = 'report_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EvolutionReportModel)
class EvolutionReportAdmin(admin.ModelAdmin):
    """进化报告管理"""
    list_display = ['report_date', 'strategy_pool_size', 'new_strategies_count', 'retired_strategies_count', 'decision_accuracy']
    ordering = ['-report_date']
    date_hierarchy = 'report_date'
    readonly_fields = ['created_at']


@admin.register(PerformanceMetricsModel)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    """性能指标管理"""
    list_display = ['metric_type', 'object_name', 'metric_date', 'daily_return', 'cumulative_return', 'sharpe_ratio', 'win_rate']
    list_filter = ['metric_type', 'metric_date']
    ordering = ['-metric_date']
    date_hierarchy = 'metric_date'


@admin.register(AlertModel)
class AlertAdmin(admin.ModelAdmin):
    """告警管理"""
    list_display = ['alert_level', 'alert_type', 'title', 'status', 'triggered_at', 'is_notified']
    list_filter = ['alert_level', 'alert_type', 'status', 'is_notified', 'triggered_at']
    search_fields = ['title', 'message']
    ordering = ['-triggered_at']
    date_hierarchy = 'triggered_at'
    readonly_fields = ['triggered_at', 'acknowledged_at', 'resolved_at', 'created_at', 'updated_at']


@admin.register(SimulationComparisonModel)
class SimulationComparisonAdmin(admin.ModelAdmin):
    """模拟盘对比管理"""
    list_display = ['comparison_date', 'best_strategy', 'aggressive_score', 'conservative_score', 'ai_score']
    ordering = ['-comparison_date']
    date_hierarchy = 'comparison_date'
    readonly_fields = ['created_at']
