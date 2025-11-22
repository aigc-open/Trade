from django.db import models
from django.db.models import JSONField


class ReviewReportModel(models.Model):
    """复盘报告模型"""
    
    REPORT_TYPE_CHOICES = [
        ('daily', '日报'),
        ('weekly', '周报'),
        ('monthly', '月报'),
        ('quarterly', '季报'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, db_index=True, verbose_name='报告类型')
    report_date = models.DateField(db_index=True, verbose_name='报告日期')
    
    # 报告内容
    title = models.CharField(max_length=500, verbose_name='标题')
    summary = models.TextField(verbose_name='摘要')
    report_data = JSONField(default=dict, verbose_name='报告数据')
    
    # 业绩概览
    performance_overview = JSONField(default=dict, verbose_name='业绩概览')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='总收益率')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='胜率')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最大回撤')
    
    # 交易统计
    trade_count = models.IntegerField(default=0, verbose_name='交易次数')
    win_count = models.IntegerField(default=0, verbose_name='盈利次数')
    lose_count = models.IntegerField(default=0, verbose_name='亏损次数')
    
    # 最佳和最差交易
    best_trades = JSONField(default=list, blank=True, verbose_name='最佳交易')
    worst_trades = JSONField(default=list, blank=True, verbose_name='最差交易')
    
    # 经验总结
    lessons_learned = JSONField(default=list, blank=True, verbose_name='经验总结')
    success_cases = JSONField(default=list, blank=True, verbose_name='成功案例')
    failure_cases = JSONField(default=list, blank=True, verbose_name='失败案例')
    
    # 策略分析
    strategy_analysis = JSONField(default=dict, blank=True, verbose_name='策略分析')
    best_strategies = JSONField(default=list, blank=True, verbose_name='最佳策略')
    worst_strategies = JSONField(default=list, blank=True, verbose_name='最差策略')
    
    # 市场洞察
    market_insights = JSONField(default=dict, blank=True, verbose_name='市场洞察')
    
    # 改进建议
    improvement_suggestions = JSONField(default=list, blank=True, verbose_name='改进建议')
    action_items = JSONField(default=list, blank=True, verbose_name='行动项')
    
    # 进化报告
    evolution_summary = JSONField(default=dict, blank=True, verbose_name='进化摘要')
    
    # 认知偏见分析
    cognitive_bias_analysis = JSONField(default=dict, blank=True, verbose_name='认知偏见分析')
    
    # 生成信息
    generated_by = models.CharField(max_length=50, default='AI', verbose_name='生成者')
    is_published = models.BooleanField(default=False, verbose_name='是否已发布')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'review_report'
        ordering = ['-report_date']
        unique_together = [['report_type', 'report_date']]
        indexes = [
            models.Index(fields=['report_type', '-report_date']),
            models.Index(fields=['is_published', '-report_date']),
        ]
        verbose_name = '复盘报告'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.report_date}"


class EvolutionReportModel(models.Model):
    """进化报告模型"""
    
    report_date = models.DateField(db_index=True, verbose_name='报告日期')
    
    # 进化概览
    summary = models.TextField(verbose_name='摘要')
    
    # 策略进化
    strategy_evolution = JSONField(default=dict, verbose_name='策略进化')
    new_strategies_count = models.IntegerField(default=0, verbose_name='新增策略数')
    retired_strategies_count = models.IntegerField(default=0, verbose_name='淘汰策略数')
    strategy_pool_size = models.IntegerField(default=0, verbose_name='策略池规模')
    
    # 决策进化
    decision_evolution = JSONField(default=dict, verbose_name='决策进化')
    decision_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='决策准确率')
    confidence_calibration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='置信度校准')
    
    # 执行进化
    execution_evolution = JSONField(default=dict, verbose_name='执行进化')
    avg_slippage = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name='平均滑点')
    execution_success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='执行成功率')
    
    # 记忆进化
    memory_evolution = JSONField(default=dict, verbose_name='记忆进化')
    memory_count = models.IntegerField(default=0, verbose_name='记忆总数')
    knowledge_nodes = models.IntegerField(default=0, verbose_name='知识节点数')
    
    # 学习曲线
    learning_curve = JSONField(default=list, blank=True, verbose_name='学习曲线')
    
    # 进化速度
    evolution_speed = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='进化速度')
    
    # 改进点
    improvements = JSONField(default=list, blank=True, verbose_name='改进点')
    bottlenecks = JSONField(default=list, blank=True, verbose_name='瓶颈')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'evolution_report'
        ordering = ['-report_date']
        verbose_name = '进化报告'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"Evolution Report - {self.report_date}"


class PerformanceMetricsModel(models.Model):
    """性能指标（时序数据）"""
    
    METRIC_TYPE_CHOICES = [
        ('portfolio', '组合'),
        ('strategy', '策略'),
        ('agent', '智能体'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES, db_index=True, verbose_name='指标类型')
    metric_date = models.DateField(db_index=True, verbose_name='指标日期')
    
    # 对象标识
    object_id = models.CharField(max_length=200, db_index=True, verbose_name='对象ID')
    object_name = models.CharField(max_length=200, verbose_name='对象名称')
    
    # 收益指标
    daily_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='日收益率')
    cumulative_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='累计收益率')
    
    # 风险指标
    volatility = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='波动率')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最大回撤')
    
    # 交易指标
    trade_count = models.IntegerField(default=0, verbose_name='交易次数')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='胜率')
    avg_win = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='平均盈利')
    avg_loss = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='平均亏损')
    profit_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='盈利因子')
    
    # 仓位指标
    position_count = models.IntegerField(default=0, verbose_name='持仓数量')
    position_utilization = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='仓位利用率')
    
    # 详细数据
    detailed_metrics = JSONField(default=dict, blank=True, verbose_name='详细指标')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'performance_metrics'
        ordering = ['-metric_date']
        unique_together = [['metric_type', 'object_id', 'metric_date']]
        indexes = [
            models.Index(fields=['metric_type', 'object_id', '-metric_date']),
            models.Index(fields=['metric_type', '-metric_date']),
        ]
        verbose_name = '性能指标'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.object_name} - {self.metric_date}"


class AlertModel(models.Model):
    """告警模型"""
    
    ALERT_LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]
    
    ALERT_TYPE_CHOICES = [
        ('risk', '风险告警'),
        ('performance', '性能告警'),
        ('system', '系统告警'),
        ('market', '市场告警'),
        ('decision', '决策告警'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('acknowledged', '已确认'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES, db_index=True, verbose_name='告警级别')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES, db_index=True, verbose_name='告警类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    
    # 告警内容
    title = models.CharField(max_length=500, verbose_name='标题')
    message = models.TextField(verbose_name='消息')
    details = JSONField(default=dict, blank=True, verbose_name='详细信息')
    
    # 触发信息
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='触发时间')
    trigger_value = models.CharField(max_length=200, null=True, blank=True, verbose_name='触发值')
    threshold = models.CharField(max_length=200, null=True, blank=True, verbose_name='阈值')
    
    # 关联对象
    related_object_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='关联对象类型')
    related_object_id = models.CharField(max_length=200, null=True, blank=True, verbose_name='关联对象ID')
    
    # 处理信息
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    acknowledged_by = models.CharField(max_length=100, null=True, blank=True, verbose_name='确认人')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    resolution_notes = models.TextField(null=True, blank=True, verbose_name='解决备注')
    
    # 通知
    is_notified = models.BooleanField(default=False, verbose_name='是否已通知')
    notification_channels = JSONField(default=list, blank=True, verbose_name='通知渠道')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'alert'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status', '-triggered_at']),
            models.Index(fields=['alert_level', 'status', '-triggered_at']),
            models.Index(fields=['alert_type', '-triggered_at']),
        ]
        verbose_name = '告警'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_alert_level_display()} - {self.title}"


class SimulationComparisonModel(models.Model):
    """模拟盘对比记录"""
    
    comparison_date = models.DateField(db_index=True, verbose_name='对比日期')
    
    # 三种策略的表现
    aggressive_performance = JSONField(default=dict, verbose_name='激进策略表现')
    conservative_performance = JSONField(default=dict, verbose_name='保守策略表现')
    ai_综合_performance = JSONField(default=dict, verbose_name='AI综合策略表现')
    
    # 对比结果
    best_strategy = models.CharField(max_length=50, verbose_name='最佳策略')
    comparison_summary = models.TextField(verbose_name='对比摘要')
    
    # 评分
    aggressive_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='激进策略评分')
    conservative_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='保守策略评分')
    ai_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='AI综合评分')
    
    # 关键发现
    key_findings = JSONField(default=list, blank=True, verbose_name='关键发现')
    
    # 改进建议
    improvement_recommendations = JSONField(default=list, blank=True, verbose_name='改进建议')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'simulation_comparison'
        ordering = ['-comparison_date']
        verbose_name = '模拟盘对比'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"Simulation Comparison - {self.comparison_date}"
