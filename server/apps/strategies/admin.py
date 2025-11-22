from django.contrib import admin
from .models import (
    StrategyModel, StrategyGenePoolModel, 
    StrategyBacktestModel, StrategyEvolutionLogModel
)


@admin.register(StrategyModel)
class StrategyAdmin(admin.ModelAdmin):
    """策略管理"""
    list_display = ['name', 'strategy_type', 'status', 'generation', 'score', 'win_rate', 'sharpe_ratio']
    list_filter = ['strategy_type', 'status', 'generation']
    search_fields = ['name', 'description']
    ordering = ['-score', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'retired_at', 'last_score_update']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'strategy_type', 'status', 'description', 'logic')
        }),
        ('策略基因', {
            'fields': ('gene_code', 'parameters')
        }),
        ('进化信息', {
            'fields': ('generation', 'parent_strategies', 'evolution_type')
        }),
        ('性能指标', {
            'fields': ('performance_metrics', 'win_rate', 'profit_loss_ratio', 'sharpe_ratio', 'max_drawdown', 'total_return')
        }),
        ('使用统计', {
            'fields': ('usage_count', 'success_count', 'fail_count', 'score', 'last_score_update')
        }),
        ('市场条件', {
            'fields': ('market_conditions',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StrategyGenePoolModel)
class StrategyGenePoolAdmin(admin.ModelAdmin):
    """策略基因池管理"""
    list_display = ['gene_type', 'gene_name', 'usage_count', 'success_rate', 'priority', 'is_active']
    list_filter = ['gene_type', 'is_active']
    search_fields = ['gene_name']
    ordering = ['-priority', '-usage_count']


@admin.register(StrategyBacktestModel)
class StrategyBacktestAdmin(admin.ModelAdmin):
    """策略回测管理"""
    list_display = ['strategy', 'start_date', 'end_date', 'status', 'total_return', 'sharpe_ratio', 'win_rate']
    list_filter = ['status', 'start_date']
    ordering = ['-created_at']
    readonly_fields = ['started_at', 'completed_at', 'created_at']


@admin.register(StrategyEvolutionLogModel)
class StrategyEvolutionLogAdmin(admin.ModelAdmin):
    """策略进化日志管理"""
    list_display = ['child_strategy', 'evolution_type', 'validation_completed', 'is_successful', 'created_at']
    list_filter = ['evolution_type', 'validation_completed', 'is_successful']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
