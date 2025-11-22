from django.contrib import admin
from .models import TradeModel, PositionModel, PortfolioModel, RiskControlLogModel


@admin.register(TradeModel)
class TradeAdmin(admin.ModelAdmin):
    """交易记录管理"""
    list_display = ['trade_id', 'symbol', 'action', 'account_type', 'status', 'order_price', 'filled_price', 'order_time', 'pnl']
    list_filter = ['action', 'status', 'account_type', 'order_time']
    search_fields = ['trade_id', 'symbol']
    ordering = ['-order_time']
    date_hierarchy = 'order_time'
    readonly_fields = ['order_time', 'filled_time', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('trade_id', 'symbol', 'action', 'account_type', 'account_name')
        }),
        ('价格与数量', {
            'fields': ('order_price', 'order_quantity', 'filled_price', 'filled_quantity')
        }),
        ('执行信息', {
            'fields': ('status', 'order_time', 'filled_time')
        }),
        ('成本信息', {
            'fields': ('commission', 'slippage', 'total_amount')
        }),
        ('关联与决策', {
            'fields': ('strategy', 'decision', 'decision_process', 'reason')
        }),
        ('风控与盈亏', {
            'fields': ('stop_loss', 'take_profit', 'pnl', 'pnl_pct', 'holding_period_hours')
        }),
        ('执行质量', {
            'fields': ('execution_quality', 'execution_time_ms', 'market_price', 'market_vix'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PositionModel)
class PositionAdmin(admin.ModelAdmin):
    """持仓管理"""
    list_display = ['symbol', 'account_type', 'quantity', 'avg_cost', 'current_price', 'unrealized_pnl', 'unrealized_pnl_pct', 'is_closed']
    list_filter = ['account_type', 'is_closed', 'opened_at']
    search_fields = ['symbol', 'account_name']
    ordering = ['-opened_at']
    readonly_fields = ['opened_at', 'closed_at', 'created_at', 'updated_at']


@admin.register(PortfolioModel)
class PortfolioAdmin(admin.ModelAdmin):
    """投资组合管理"""
    list_display = ['account_name', 'account_type', 'total_asset', 'cash', 'market_value', 'total_return', 'win_rate', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['account_name']
    ordering = ['-total_asset']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('账户信息', {
            'fields': ('account_name', 'account_type', 'is_active')
        }),
        ('资金信息', {
            'fields': ('initial_capital', 'total_asset', 'cash', 'available_cash', 'frozen_cash', 'market_value')
        }),
        ('盈亏统计', {
            'fields': ('total_pnl', 'total_return', 'today_pnl', 'today_return')
        }),
        ('交易统计', {
            'fields': ('total_trades', 'win_trades', 'lose_trades', 'win_rate')
        }),
        ('风险指标', {
            'fields': ('max_drawdown', 'sharpe_ratio', 'volatility')
        }),
        ('配置', {
            'fields': ('risk_preference', 'max_position_pct', 'equity_curve'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RiskControlLogModel)
class RiskControlLogAdmin(admin.ModelAdmin):
    """风控日志管理"""
    list_display = ['risk_type', 'action', 'trade', 'portfolio', 'executed', 'created_at']
    list_filter = ['risk_type', 'action', 'executed', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
