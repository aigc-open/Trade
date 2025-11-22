from django.contrib import admin
from .models import (
    AgentStatusModel, TradingPlanModel, 
    DecisionRecordModel, MarketOpportunityModel
)


@admin.register(AgentStatusModel)
class AgentStatusAdmin(admin.ModelAdmin):
    """智能体状态管理"""
    list_display = ['agent_type', 'status', 'last_heartbeat', 'last_action', 'error_count']
    list_filter = ['agent_type', 'status']
    ordering = ['agent_type']
    readonly_fields = ['created_at', 'updated_at', 'last_heartbeat']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('agent_type', 'status')
        }),
        ('运行信息', {
            'fields': ('last_heartbeat', 'last_action', 'current_task')
        }),
        ('性能与错误', {
            'fields': ('metrics', 'error_count', 'last_error')
        }),
        ('配置', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TradingPlanModel)
class TradingPlanAdmin(admin.ModelAdmin):
    """交易计划管理"""
    list_display = ['plan_date', 'plan_type', 'status', 'expected_return', 'actual_return', 'completion_rate']
    list_filter = ['plan_type', 'status', 'plan_date']
    search_fields = ['plan_date']
    ordering = ['-plan_date']
    date_hierarchy = 'plan_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('plan_type', 'plan_date', 'status', 'created_by')
        }),
        ('计划内容', {
            'fields': ('plan_data', 'objectives', 'target_symbols')
        }),
        ('风险评估', {
            'fields': ('risk_assessment', 'expected_return', 'max_risk_pct')
        }),
        ('执行结果', {
            'fields': ('actual_return', 'completion_rate', 'execution_summary'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DecisionRecordModel)
class DecisionRecordAdmin(admin.ModelAdmin):
    """决策记录管理"""
    list_display = ['symbol', 'decision_type', 'decision_time', 'confidence_level', 'confidence_score', 'is_executed']
    list_filter = ['decision_type', 'confidence_level', 'is_executed', 'decision_time']
    search_fields = ['symbol']
    ordering = ['-decision_time']
    date_hierarchy = 'decision_time'
    readonly_fields = ['decision_time', 'created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('symbol', 'decision_type', 'decision_time')
        }),
        ('决策建议', {
            'fields': ('proposal', 'target_price', 'target_quantity', 'target_position_pct')
        }),
        ('多智能体辩论', {
            'fields': ('aggressive_view', 'conservative_view', 'quant_analysis', 'debate_summary')
        }),
        ('最终决策', {
            'fields': ('final_decision', 'confidence_level', 'confidence_score')
        }),
        ('风险控制', {
            'fields': ('stop_loss', 'take_profit', 'max_loss_amount')
        }),
        ('执行状态', {
            'fields': ('is_executed', 'execution_time', 'execution_result'),
            'classes': ('collapse',)
        }),
        ('事后评估', {
            'fields': ('outcome', 'actual_return', 'post_analysis'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketOpportunityModel)
class MarketOpportunityAdmin(admin.ModelAdmin):
    """市场机会管理"""
    list_display = ['symbol', 'opportunity_type', 'status', 'identified_at', 'expected_return', 'risk_level', 'success']
    list_filter = ['opportunity_type', 'status', 'success', 'identified_at']
    search_fields = ['symbol', 'description']
    ordering = ['-identified_at']
    date_hierarchy = 'identified_at'
    readonly_fields = ['identified_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('symbol', 'opportunity_type', 'status', 'identified_at', 'valid_until')
        }),
        ('机会描述', {
            'fields': ('description', 'rationale', 'expected_return', 'risk_level')
        }),
        ('触发条件', {
            'fields': ('trigger_conditions', 'entry_price', 'exit_price')
        }),
        ('结果追踪', {
            'fields': ('decision', 'actual_return', 'success'),
            'classes': ('collapse',)
        }),
    )
