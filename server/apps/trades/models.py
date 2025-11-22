from django.db import models
from django.db.models import JSONField
from apps.strategies.models import StrategyModel
from apps.agents.models import DecisionRecordModel


class TradeModel(models.Model):
    """交易记录模型"""
    
    ACTION_CHOICES = [
        ('BUY', '买入'),
        ('SELL', '卖出'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('submitted', '已提交'),
        ('partial_filled', '部分成交'),
        ('filled', '已成交'),
        ('cancelled', '已取消'),
        ('failed', '失败'),
    ]
    
    ACCOUNT_TYPE_CHOICES = [
        ('real', '实盘'),
        ('simulation', '模拟盘'),
    ]
    
    # 基本信息
    trade_id = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='交易ID')
    symbol = models.CharField(max_length=50, db_index=True, verbose_name='标的代码')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='操作')
    
    # 账户类型
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='simulation', verbose_name='账户类型')
    account_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='账户名称')
    
    # 价格和数量
    order_price = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='委托价格')
    order_quantity = models.IntegerField(verbose_name='委托数量')
    filled_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='成交价格')
    filled_quantity = models.IntegerField(default=0, verbose_name='成交数量')
    
    # 执行信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    order_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='委托时间')
    filled_time = models.DateTimeField(null=True, blank=True, verbose_name='成交时间')
    
    # 成本信息
    commission = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='手续费')
    slippage = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='滑点')
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总金额')
    
    # 关联关系
    strategy = models.ForeignKey(StrategyModel, null=True, blank=True, on_delete=models.SET_NULL, 
                                related_name='trades', verbose_name='策略')
    decision = models.ForeignKey(DecisionRecordModel, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='trades', verbose_name='决策记录')
    
    # 决策过程（冗余存储，便于查询）
    decision_process = JSONField(default=dict, blank=True, verbose_name='决策过程')
    reason = models.TextField(verbose_name='交易原因')
    
    # 风控信息
    stop_loss = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止损价')
    take_profit = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止盈价')
    
    # 执行质量
    execution_quality = JSONField(default=dict, blank=True, verbose_name='执行质量')
    execution_time_ms = models.IntegerField(null=True, blank=True, verbose_name='执行耗时(毫秒)')
    
    # 盈亏（针对平仓）
    pnl = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='盈亏金额')
    pnl_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='盈亏比例')
    holding_period_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='持有时长(小时)')
    
    # 市场信息（交易时的市场状态）
    market_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='市场价')
    market_vix = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='VIX指数')
    market_sentiment = models.CharField(max_length=50, null=True, blank=True, verbose_name='市场情绪')
    
    # 事后评估
    outcome = models.CharField(max_length=50, null=True, blank=True, verbose_name='结果评价')
    lessons_learned = JSONField(default=list, blank=True, verbose_name='教训总结')
    
    # 外部订单ID（如券商返回的订单号）
    external_order_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='外部订单ID')
    
    # 错误信息
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'trade'
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['symbol', '-order_time']),
            models.Index(fields=['status', '-order_time']),
            models.Index(fields=['account_type', '-order_time']),
            models.Index(fields=['-order_time']),
        ]
        verbose_name = '交易记录'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.trade_id} - {self.symbol} {self.action}"


class PositionModel(models.Model):
    """持仓模型"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('real', '实盘'),
        ('simulation', '模拟盘'),
    ]
    
    symbol = models.CharField(max_length=50, db_index=True, verbose_name='标的代码')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='simulation', verbose_name='账户类型')
    account_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='账户名称')
    
    # 持仓信息
    quantity = models.IntegerField(verbose_name='持仓数量')
    available_quantity = models.IntegerField(verbose_name='可用数量')
    frozen_quantity = models.IntegerField(default=0, verbose_name='冻结数量')
    
    # 成本信息
    avg_cost = models.DecimalField(max_digits=20, decimal_places=6, verbose_name='平均成本')
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总成本')
    
    # 当前市值
    current_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='当前价格')
    market_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='市值')
    
    # 盈亏
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='浮动盈亏')
    unrealized_pnl_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='浮动盈亏比例')
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='已实现盈亏')
    
    # 关联策略
    strategy = models.ForeignKey(StrategyModel, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='positions', verbose_name='策略')
    
    # 风控信息
    stop_loss = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止损价')
    take_profit = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止盈价')
    
    # 持仓时间
    opened_at = models.DateTimeField(verbose_name='开仓时间')
    holding_days = models.IntegerField(default=0, verbose_name='持有天数')
    
    # 相关交易
    open_trade = models.ForeignKey(TradeModel, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='opened_positions', verbose_name='开仓交易')
    
    # 元数据
    metadata = JSONField(default=dict, blank=True, verbose_name='元数据')
    
    is_closed = models.BooleanField(default=False, verbose_name='是否已平仓')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='平仓时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'position'
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['symbol', 'account_type', 'is_closed']),
            models.Index(fields=['account_type', 'is_closed']),
        ]
        verbose_name = '持仓'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.symbol} - {self.quantity}股"


class PortfolioModel(models.Model):
    """投资组合（账户）模型"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('real', '实盘'),
        ('simulation', '模拟盘'),
    ]
    
    account_name = models.CharField(max_length=100, unique=True, verbose_name='账户名称')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='simulation', verbose_name='账户类型')
    
    # 资金信息
    initial_capital = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='初始资金')
    total_asset = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总资产')
    cash = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='现金')
    market_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='持仓市值')
    
    # 可用资金和冻结资金
    available_cash = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='可用资金')
    frozen_cash = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='冻结资金')
    
    # 盈亏
    total_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='总盈亏')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='总收益率')
    
    # 今日数据
    today_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='今日盈亏')
    today_return = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='今日收益率')
    
    # 统计信息
    total_trades = models.IntegerField(default=0, verbose_name='总交易次数')
    win_trades = models.IntegerField(default=0, verbose_name='盈利交易次数')
    lose_trades = models.IntegerField(default=0, verbose_name='亏损交易次数')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='胜率')
    
    # 风险指标
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='最大回撤')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    volatility = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='波动率')
    
    # 配置
    risk_preference = models.CharField(max_length=50, default='balanced', verbose_name='风险偏好')
    max_position_pct = models.DecimalField(max_digits=5, decimal_places=2, default=30, verbose_name='最大单仓位比例')
    
    # 权益曲线
    equity_curve = JSONField(default=list, blank=True, verbose_name='权益曲线')
    
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'portfolio'
        verbose_name = '投资组合'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.account_name} - {self.total_asset}"


class RiskControlLogModel(models.Model):
    """风控日志"""
    
    RISK_TYPE_CHOICES = [
        ('pre_trade', '交易前风控'),
        ('in_trade', '交易中风控'),
        ('post_trade', '交易后风控'),
        ('system', '系统性风控'),
    ]
    
    ACTION_CHOICES = [
        ('allow', '允许'),
        ('reject', '拒绝'),
        ('adjust', '调整'),
        ('alert', '告警'),
        ('pause', '暂停'),
    ]
    
    risk_type = models.CharField(max_length=20, choices=RISK_TYPE_CHOICES, verbose_name='风控类型')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作')
    
    # 相关对象
    trade = models.ForeignKey(TradeModel, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name='risk_logs', verbose_name='交易')
    portfolio = models.ForeignKey(PortfolioModel, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='risk_logs', verbose_name='投资组合')
    
    # 风控详情
    risk_indicators = JSONField(default=dict, verbose_name='风险指标')
    trigger_rules = JSONField(default=list, verbose_name='触发规则')
    description = models.TextField(verbose_name='描述')
    
    # 建议和执行
    recommendation = models.TextField(verbose_name='建议')
    executed = models.BooleanField(default=False, verbose_name='是否已执行')
    execution_result = models.TextField(null=True, blank=True, verbose_name='执行结果')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'risk_control_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['risk_type', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
        verbose_name = '风控日志'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_risk_type_display()} - {self.get_action_display()}"
