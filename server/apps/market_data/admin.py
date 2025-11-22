from django.contrib import admin
from .models import (
    MarketDataModel, MarketIndexModel, MarketSentimentModel, 
    NewsEventModel, StockInfoModel
)


@admin.register(MarketDataModel)
class MarketDataAdmin(admin.ModelAdmin):
    """市场行情数据管理"""
    list_display = ['symbol', 'market', 'timestamp', 'close', 'volume', 'change_pct', 'data_source']
    list_filter = ['market', 'data_source', 'timestamp']
    search_fields = ['symbol']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('symbol', 'market', 'timestamp', 'data_source')
        }),
        ('价格数据', {
            'fields': ('open', 'high', 'low', 'close', 'volume', 'amount')
        }),
        ('技术指标', {
            'fields': ('change_pct', 'turnover_rate')
        }),
        ('元数据', {
            'fields': ('raw_data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketIndexModel)
class MarketIndexAdmin(admin.ModelAdmin):
    """市场指数管理"""
    list_display = ['index_code', 'index_name', 'timestamp', 'value', 'change_pct', 'rise_count', 'fall_count']
    list_filter = ['index_code', 'timestamp']
    search_fields = ['index_code', 'index_name']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(MarketSentimentModel)
class MarketSentimentAdmin(admin.ModelAdmin):
    """市场情绪管理"""
    list_display = ['timestamp', 'vix', 'fear_greed_index', 'put_call_ratio', 'social_sentiment_score']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(NewsEventModel)
class NewsEventAdmin(admin.ModelAdmin):
    """新闻事件管理"""
    list_display = ['title', 'source', 'published_at', 'event_level', 'sentiment_score']
    list_filter = ['event_level', 'source', 'published_at']
    search_fields = ['title', 'content']
    ordering = ['-published_at']
    date_hierarchy = 'published_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'source', 'url', 'published_at')
        }),
        ('内容', {
            'fields': ('content',)
        }),
        ('AI分析', {
            'fields': ('event_level', 'sentiment_score', 'impact_analysis', 'related_symbols')
        }),
        ('元数据', {
            'fields': ('tags', 'raw_data', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockInfoModel)
class StockInfoAdmin(admin.ModelAdmin):
    """股票信息管理"""
    list_display = ['symbol', 'name', 'market', 'industry', 'market_cap', 'pe_ratio', 'is_active']
    list_filter = ['market', 'industry', 'is_active']
    search_fields = ['symbol', 'name', 'industry']
    ordering = ['symbol']
    readonly_fields = ['created_at', 'updated_at']
