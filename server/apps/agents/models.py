from django.db import models
from django.db.models import JSONField


class AgentStatusModel(models.Model):
    """智能体状态模型"""
    
    AGENT_TYPE_CHOICES = [
        ('perception', '感知层'),
        ('memory', '记忆层'),
        ('planning', '规划层'),
        ('decision', '决策层'),
        ('execution', '执行层'),
        ('reflection', '反思层'),
    ]
    
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('error', '错误'),
        ('paused', '已暂停'),
    ]
    
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES, unique=True, verbose_name='智能体类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped', verbose_name='状态')
    
    # 运行信息
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name='最后心跳时间')
    last_action = models.CharField(max_length=500, null=True, blank=True, verbose_name='最后操作')
    current_task = models.TextField(null=True, blank=True, verbose_name='当前任务')
    
    # 性能指标
    metrics = JSONField(default=dict, blank=True, verbose_name='性能指标')
    error_count = models.IntegerField(default=0, verbose_name='错误次数')
    last_error = models.TextField(null=True, blank=True, verbose_name='最后错误')
    
    # 配置
    config = JSONField(default=dict, blank=True, verbose_name='配置')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'agent_status'
        verbose_name = '智能体状态'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_agent_type_display()} - {self.get_status_display()}"


class TradingPlanModel(models.Model):
    """交易计划模型"""
    
    PLAN_TYPE_CHOICES = [
        ('daily', '日度计划'),
        ('weekly', '周度计划'),
        ('monthly', '月度计划'),
        ('quarterly', '季度计划'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, verbose_name='计划类型')
    plan_date = models.DateField(db_index=True, verbose_name='计划日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    # 计划内容
    plan_data = JSONField(default=dict, verbose_name='计划数据')
    objectives = JSONField(default=list, blank=True, verbose_name='目标列表')
    target_symbols = JSONField(default=list, blank=True, verbose_name='目标标的')
    
    # 风险评估
    risk_assessment = JSONField(default=dict, blank=True, verbose_name='风险评估')
    expected_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='预期收益率')
    max_risk_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最大风险比例')
    
    # 执行结果
    actual_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='实际收益率')
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='完成率')
    execution_summary = JSONField(default=dict, blank=True, verbose_name='执行摘要')
    
    created_by = models.CharField(max_length=50, default='AI', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'trading_plan'
        ordering = ['-plan_date']
        indexes = [
            models.Index(fields=['plan_type', '-plan_date']),
            models.Index(fields=['status', '-plan_date']),
        ]
        verbose_name = '交易计划'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_plan_type_display()} - {self.plan_date}"


class DecisionRecordModel(models.Model):
    """决策记录模型（多智能体辩论）"""
    
    DECISION_TYPE_CHOICES = [
        ('buy', '买入'),
        ('sell', '卖出'),
        ('hold', '持有'),
        ('adjust', '调整'),
        ('abandon', '放弃'),
    ]
    
    CONFIDENCE_LEVEL_CHOICES = [
        ('very_low', '很低'),
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('very_high', '很高'),
    ]
    
    symbol = models.CharField(max_length=50, db_index=True, verbose_name='标的代码')
    decision_type = models.CharField(max_length=20, choices=DECISION_TYPE_CHOICES, verbose_name='决策类型')
    decision_time = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='决策时间')
    
    # 决策建议
    proposal = JSONField(default=dict, verbose_name='提案内容')
    target_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='目标价格')
    target_quantity = models.IntegerField(null=True, blank=True, verbose_name='目标数量')
    target_position_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='目标仓位比例')
    
    # 多智能体辩论记录
    aggressive_view = models.TextField(verbose_name='激进派观点')
    conservative_view = models.TextField(verbose_name='保守派观点')
    quant_analysis = JSONField(default=dict, verbose_name='量化分析')
    debate_summary = models.TextField(verbose_name='辩论摘要')
    
    # 最终决策
    final_decision = models.TextField(verbose_name='最终决策')
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVEL_CHOICES, verbose_name='置信度等级')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='置信度分数(0-100)')
    
    # 风险控制
    stop_loss = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止损价')
    take_profit = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='止盈价')
    max_loss_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='最大亏损金额')
    
    # 执行状态
    is_executed = models.BooleanField(default=False, verbose_name='是否已执行')
    execution_time = models.DateTimeField(null=True, blank=True, verbose_name='执行时间')
    execution_result = JSONField(default=dict, blank=True, verbose_name='执行结果')
    
    # 事后评估
    outcome = models.CharField(max_length=20, null=True, blank=True, verbose_name='结果')
    actual_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='实际收益率')
    post_analysis = models.TextField(null=True, blank=True, verbose_name='事后分析')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'decision_record'
        ordering = ['-decision_time']
        indexes = [
            models.Index(fields=['symbol', '-decision_time']),
            models.Index(fields=['decision_type', '-decision_time']),
            models.Index(fields=['is_executed', '-decision_time']),
        ]
        verbose_name = '决策记录'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.symbol} - {self.get_decision_type_display()} - {self.decision_time}"


class MarketOpportunityModel(models.Model):
    """市场机会识别"""
    
    OPPORTUNITY_TYPE_CHOICES = [
        ('breakout', '突破'),
        ('reversal', '反转'),
        ('catalyst', '催化剂'),
        ('valuation', '估值修复'),
        ('momentum', '动量'),
        ('sentiment', '情绪反转'),
        ('event', '事件驱动'),
    ]
    
    STATUS_CHOICES = [
        ('identified', '已识别'),
        ('analyzing', '分析中'),
        ('validated', '已验证'),
        ('executed', '已执行'),
        ('expired', '已过期'),
        ('invalid', '已失效'),
    ]
    
    symbol = models.CharField(max_length=50, db_index=True, verbose_name='标的代码')
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPE_CHOICES, verbose_name='机会类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified', verbose_name='状态')
    
    identified_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='识别时间')
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name='有效期至')
    
    # 机会描述
    description = models.TextField(verbose_name='描述')
    rationale = models.TextField(verbose_name='依据')
    expected_return = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='预期收益率')
    risk_level = models.IntegerField(verbose_name='风险等级(1-10)')
    
    # 触发条件
    trigger_conditions = JSONField(default=dict, verbose_name='触发条件')
    entry_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='入场价格')
    exit_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name='出场价格')
    
    # 相关决策
    decision = models.ForeignKey(DecisionRecordModel, null=True, blank=True, on_delete=models.SET_NULL, 
                                 related_name='opportunities', verbose_name='相关决策')
    
    # 结果追踪
    actual_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='实际收益率')
    success = models.BooleanField(null=True, blank=True, verbose_name='是否成功')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'market_opportunity'
        ordering = ['-identified_at']
        indexes = [
            models.Index(fields=['status', '-identified_at']),
            models.Index(fields=['opportunity_type', '-identified_at']),
        ]
        verbose_name = '市场机会'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.symbol} - {self.get_opportunity_type_display()}"
