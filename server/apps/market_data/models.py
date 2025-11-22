from django.db import models
from django.contrib.postgres.fields import JSONField as PostgresJSONField
from django.db.models import JSONField
import sys


class MarketDataModel(models.Model):
    """市场行情数据模型"""
    
    MARKET_CHOICES = [
        ('A_STOCK', 'A股'),
        ('US_STOCK', '美股'),
        ('HK_STOCK', '港股'),
        ('CRYPTO', '加密货币'),
    ]
    
    symbol = models.CharField(max_length=50, db_index=True, verbose_name='标的代码')
    market = models.CharField(max_length=20, choices=MARKET_CHOICES, db_index=True, verbose_name='市场类型')
    timestamp = models.DateTimeField(db_index=True, verbose_name='时间戳')
    
    # OHLCV数据
    open = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='开盘价')
    high = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='最高价')
    low = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='最低价')
    close = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='收盘价')
    volume = models.BigIntegerField(verbose_name='成交量')
    
    # 扩展数据
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='成交额')
    change_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='涨跌幅')
    turnover_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='换手率')
    
    # 元数据
    data_source = models.CharField(max_length=50, default='unknown', verbose_name='数据源')
    raw_data = JSONField(default=dict, blank=True, verbose_name='原始数据')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'market_data'
        ordering = ['-timestamp']
        unique_together = [['symbol', 'market', 'timestamp']]
        indexes = [
            models.Index(fields=['symbol', 'market', '-timestamp']),
            models.Index(fields=['market', '-timestamp']),
        ]
        verbose_name = '市场行情数据'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"


class MarketIndexModel(models.Model):
    """市场指数数据"""
    
    index_code = models.CharField(max_length=50, db_index=True, verbose_name='指数代码')
    index_name = models.CharField(max_length=100, verbose_name='指数名称')
    timestamp = models.DateTimeField(db_index=True, verbose_name='时间戳')
    
    value = models.DecimalField(max_digits=20, decimal_places=4, verbose_name='指数值')
    change_pct = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='涨跌幅')
    
    # 市场统计
    rise_count = models.IntegerField(null=True, blank=True, verbose_name='上涨家数')
    fall_count = models.IntegerField(null=True, blank=True, verbose_name='下跌家数')
    limit_up_count = models.IntegerField(null=True, blank=True, verbose_name='涨停家数')
    limit_down_count = models.IntegerField(null=True, blank=True, verbose_name='跌停家数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'market_index'
        ordering = ['-timestamp']
        unique_together = [['index_code', 'timestamp']]
        verbose_name = '市场指数'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.index_name} - {self.timestamp}"


class MarketSentimentModel(models.Model):
    """市场情绪指标"""
    
    timestamp = models.DateTimeField(db_index=True, verbose_name='时间戳')
    
    # 情绪指标
    vix = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='VIX指数')
    fear_greed_index = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='恐慌贪婪指数')
    put_call_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='看跌看涨比')
    
    # 资金流向
    north_money_flow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='北向资金流入')
    main_force_flow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='主力资金流入')
    
    # 社交媒体情绪
    social_sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='社交媒体情绪分数')
    social_sentiment_data = JSONField(default=dict, blank=True, verbose_name='社交媒体情绪详情')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'market_sentiment'
        ordering = ['-timestamp']
        verbose_name = '市场情绪'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"Market Sentiment - {self.timestamp}"


class NewsEventModel(models.Model):
    """新闻事件数据"""
    
    EVENT_LEVEL_CHOICES = [
        (1, '低'),
        (2, '较低'),
        (3, '一般'),
        (4, '较高'),
        (5, '高'),
        (6, '很高'),
        (7, '极高'),
        (8, '重大'),
        (9, '特重大'),
        (10, '黑天鹅'),
    ]
    
    title = models.CharField(max_length=500, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    source = models.CharField(max_length=100, verbose_name='来源')
    url = models.URLField(max_length=1000, null=True, blank=True, verbose_name='链接')
    
    published_at = models.DateTimeField(db_index=True, verbose_name='发布时间')
    
    # AI分析结果
    event_level = models.IntegerField(choices=EVENT_LEVEL_CHOICES, null=True, blank=True, verbose_name='事件等级')
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='情绪分数(-100到100)')
    impact_analysis = models.TextField(null=True, blank=True, verbose_name='影响分析')
    related_symbols = JSONField(default=list, blank=True, verbose_name='相关标的')
    
    # 元数据
    tags = JSONField(default=list, blank=True, verbose_name='标签')
    raw_data = JSONField(default=dict, blank=True, verbose_name='原始数据')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'news_event'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['event_level', '-published_at']),
        ]
        verbose_name = '新闻事件'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.title[:50]}..."


class StockInfoModel(models.Model):
    """股票基本信息"""
    
    symbol = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='标的代码')
    name = models.CharField(max_length=200, verbose_name='名称')
    market = models.CharField(max_length=20, verbose_name='市场')
    
    # 基本信息
    industry = models.CharField(max_length=100, null=True, blank=True, verbose_name='行业')
    sector = models.CharField(max_length=100, null=True, blank=True, verbose_name='板块')
    list_date = models.DateField(null=True, blank=True, verbose_name='上市日期')
    
    # 财务指标
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='市值')
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市盈率')
    pb_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市净率')
    
    # 元数据
    metadata = JSONField(default=dict, blank=True, verbose_name='元数据')
    
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'stock_info'
        verbose_name = '股票信息'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
