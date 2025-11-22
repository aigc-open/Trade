from django.db import models
from django.db.models import JSONField


class StrategyModel(models.Model):
    """策略模型"""
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('testing', '测试中'),
        ('paused', '暂停'),
        ('retired', '已淘汰'),
    ]
    
    STRATEGY_TYPE_CHOICES = [
        ('trend', '趋势策略'),
        ('mean_reversion', '均值回归'),
        ('momentum', '动量策略'),
        ('value', '价值策略'),
        ('sentiment', '情绪策略'),
        ('hybrid', '混合策略'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField(max_length=200, unique=True, verbose_name='策略名称')
    strategy_type = models.CharField(max_length=50, choices=STRATEGY_TYPE_CHOICES, verbose_name='策略类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='testing', verbose_name='状态')
    
    # 策略基因编码
    gene_code = JSONField(default=dict, verbose_name='基因编码')
    parameters = JSONField(default=dict, verbose_name='策略参数')
    
    # 策略描述
    description = models.TextField(verbose_name='策略描述')
    logic = models.TextField(verbose_name='策略逻辑')
    
    # 进化信息
    generation = models.IntegerField(default=1, verbose_name='代数')
    parent_strategies = JSONField(default=list, blank=True, verbose_name='父策略')
    evolution_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='进化类型')  # mutation/crossover/natural
    
    # 性能指标
    performance_metrics = JSONField(default=dict, blank=True, verbose_name='性能指标')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='胜率')
    profit_loss_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='盈亏比')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最大回撤')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='总收益率')
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    success_count = models.IntegerField(default=0, verbose_name='成功次数')
    fail_count = models.IntegerField(default=0, verbose_name='失败次数')
    
    # 评分
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='综合评分(0-100)')
    last_score_update = models.DateTimeField(null=True, blank=True, verbose_name='最后评分更新时间')
    
    # 适用市场条件
    market_conditions = JSONField(default=dict, blank=True, verbose_name='适用市场条件')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    retired_at = models.DateTimeField(null=True, blank=True, verbose_name='淘汰时间')
    
    class Meta:
        db_table = 'strategy'
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['status', '-score']),
            models.Index(fields=['strategy_type', '-score']),
        ]
        verbose_name = '交易策略'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.name} (Gen{self.generation})"


class StrategyGenePoolModel(models.Model):
    """策略基因池"""
    
    gene_type = models.CharField(max_length=100, verbose_name='基因类型')
    gene_name = models.CharField(max_length=200, verbose_name='基因名称')
    gene_value = JSONField(verbose_name='基因值')
    
    # 统计
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='成功率')
    
    # 优先级
    priority = models.IntegerField(default=50, verbose_name='优先级(0-100)')
    
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'strategy_gene_pool'
        unique_together = [['gene_type', 'gene_name']]
        verbose_name = '策略基因池'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.gene_type} - {self.gene_name}"


class StrategyBacktestModel(models.Model):
    """策略回测记录"""
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    strategy = models.ForeignKey(StrategyModel, on_delete=models.CASCADE, related_name='backtests', verbose_name='策略')
    
    # 回测配置
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    initial_capital = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='初始资金')
    symbols = JSONField(default=list, verbose_name='标的列表')
    
    # 执行状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 回测结果
    final_capital = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='最终资金')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='总收益率')
    annualized_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='年化收益率')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最大回撤')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='胜率')
    
    # 详细结果
    detailed_results = JSONField(default=dict, blank=True, verbose_name='详细结果')
    trade_records = JSONField(default=list, blank=True, verbose_name='交易记录')
    equity_curve = JSONField(default=list, blank=True, verbose_name='权益曲线')
    
    # 错误信息
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'strategy_backtest'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['strategy', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = '策略回测'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.strategy.name} - {self.start_date} to {self.end_date}"


class StrategyEvolutionLogModel(models.Model):
    """策略进化日志"""
    
    EVOLUTION_TYPE_CHOICES = [
        ('mutation', '变异'),
        ('crossover', '杂交'),
        ('natural', '自然创建'),
        ('manual', '人工创建'),
    ]
    
    parent_strategies = JSONField(default=list, verbose_name='父策略列表')
    child_strategy = models.ForeignKey(StrategyModel, on_delete=models.CASCADE, related_name='evolution_logs', verbose_name='子策略')
    evolution_type = models.CharField(max_length=50, choices=EVOLUTION_TYPE_CHOICES, verbose_name='进化类型')
    
    # 进化详情
    evolution_details = JSONField(default=dict, verbose_name='进化详情')
    changed_genes = JSONField(default=list, verbose_name='变更的基因')
    
    # 进化原因
    trigger_reason = models.TextField(verbose_name='触发原因')
    expected_improvement = models.TextField(verbose_name='预期改进')
    
    # 验证结果
    validation_completed = models.BooleanField(default=False, verbose_name='是否已验证')
    validation_results = JSONField(default=dict, blank=True, verbose_name='验证结果')
    is_successful = models.BooleanField(null=True, blank=True, verbose_name='是否成功')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'strategy_evolution_log'
        ordering = ['-created_at']
        verbose_name = '策略进化日志'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_evolution_type_display()} - {self.child_strategy.name}"
