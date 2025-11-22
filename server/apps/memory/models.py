from django.db import models
from django.db.models import JSONField


class AgentMemoryModel(models.Model):
    """智能体记忆模型"""
    
    MEMORY_TYPE_CHOICES = [
        ('working', '工作记忆'),
        ('short_term', '短期记忆'),
        ('long_term', '长期记忆'),
        ('episodic', '情景记忆'),
    ]
    
    memory_type = models.CharField(max_length=20, choices=MEMORY_TYPE_CHOICES, db_index=True, verbose_name='记忆类型')
    
    # 记忆内容
    content = models.TextField(verbose_name='记忆内容')
    summary = models.CharField(max_length=500, null=True, blank=True, verbose_name='摘要')
    
    # 记忆重要性
    importance_score = models.DecimalField(max_digits=5, decimal_places=2, db_index=True, verbose_name='重要性分数(0-10)')
    
    # 记忆元数据
    metadata = JSONField(default=dict, verbose_name='元数据')
    tags = JSONField(default=list, blank=True, verbose_name='标签')
    
    # 5W1H结构
    when = models.DateTimeField(null=True, blank=True, verbose_name='何时')
    where = models.CharField(max_length=200, null=True, blank=True, verbose_name='何地')
    what = models.CharField(max_length=500, null=True, blank=True, verbose_name='何事')
    who = models.CharField(max_length=200, null=True, blank=True, verbose_name='何人')
    why = models.TextField(null=True, blank=True, verbose_name='为何')
    how = models.TextField(null=True, blank=True, verbose_name='如何')
    
    # 关联对象
    related_symbols = JSONField(default=list, blank=True, verbose_name='相关标的')
    related_strategies = JSONField(default=list, blank=True, verbose_name='相关策略')
    related_trades = JSONField(default=list, blank=True, verbose_name='相关交易')
    
    # 向量嵌入ID（在ChromaDB中的ID）
    vector_id = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name='向量ID')
    
    # 记忆来源
    source = models.CharField(max_length=100, verbose_name='来源')
    source_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='来源ID')
    
    # 访问统计
    access_count = models.IntegerField(default=0, verbose_name='访问次数')
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name='最后访问时间')
    
    # 记忆评价
    is_valuable = models.BooleanField(null=True, blank=True, verbose_name='是否有价值')
    value_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='价值分数')
    
    # 遗忘机制
    is_forgotten = models.BooleanField(default=False, verbose_name='是否已遗忘')
    forgotten_at = models.DateTimeField(null=True, blank=True, verbose_name='遗忘时间')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'agent_memory'
        ordering = ['-importance_score', '-created_at']
        indexes = [
            models.Index(fields=['memory_type', '-importance_score']),
            models.Index(fields=['is_forgotten', '-created_at']),
            models.Index(fields=['-importance_score', '-created_at']),
        ]
        verbose_name = '智能体记忆'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_memory_type_display()} - {self.summary or self.content[:50]}"


class KnowledgeNodeModel(models.Model):
    """知识图谱节点"""
    
    NODE_TYPE_CHOICES = [
        ('concept', '概念'),
        ('pattern', '模式'),
        ('rule', '规则'),
        ('symbol', '标的'),
        ('event', '事件'),
        ('strategy', '策略'),
        ('indicator', '指标'),
    ]
    
    node_id = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='节点ID')
    node_type = models.CharField(max_length=50, choices=NODE_TYPE_CHOICES, db_index=True, verbose_name='节点类型')
    
    # 节点信息
    name = models.CharField(max_length=200, verbose_name='名称')
    description = models.TextField(verbose_name='描述')
    
    # 节点属性
    properties = JSONField(default=dict, verbose_name='属性')
    
    # 重要性
    importance = models.IntegerField(default=50, verbose_name='重要性(0-100)')
    
    # 统计
    reference_count = models.IntegerField(default=0, verbose_name='引用次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'knowledge_node'
        verbose_name = '知识节点'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_node_type_display()} - {self.name}"


class KnowledgeEdgeModel(models.Model):
    """知识图谱关系"""
    
    RELATIONSHIP_TYPE_CHOICES = [
        ('leads_to', '导致'),
        ('correlates_with', '相关'),
        ('opposes', '对立'),
        ('contains', '包含'),
        ('part_of', '属于'),
        ('precedes', '先于'),
        ('follows', '后于'),
        ('causes', '引起'),
        ('similar_to', '相似'),
    ]
    
    from_node = models.ForeignKey(KnowledgeNodeModel, on_delete=models.CASCADE, 
                                  related_name='outgoing_edges', verbose_name='源节点')
    to_node = models.ForeignKey(KnowledgeNodeModel, on_delete=models.CASCADE,
                                related_name='incoming_edges', verbose_name='目标节点')
    
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_TYPE_CHOICES, verbose_name='关系类型')
    
    # 关系强度
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name='权重(0-1)')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.5, verbose_name='置信度(0-1)')
    
    # 关系属性
    properties = JSONField(default=dict, blank=True, verbose_name='属性')
    
    # 证据
    evidence_count = models.IntegerField(default=0, verbose_name='证据数量')
    evidence = JSONField(default=list, blank=True, verbose_name='证据列表')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'knowledge_edge'
        unique_together = [['from_node', 'to_node', 'relationship']]
        indexes = [
            models.Index(fields=['from_node', 'relationship']),
            models.Index(fields=['to_node', 'relationship']),
        ]
        verbose_name = '知识关系'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.from_node.name} {self.get_relationship_display()} {self.to_node.name}"


class TradingPrincipleModel(models.Model):
    """交易原则库"""
    
    PRINCIPLE_TYPE_CHOICES = [
        ('entry', '入场原则'),
        ('exit', '出场原则'),
        ('risk', '风控原则'),
        ('position', '仓位管理'),
        ('market', '市场判断'),
        ('general', '通用原则'),
    ]
    
    SOURCE_CHOICES = [
        ('learned', 'AI学习'),
        ('manual', '人工添加'),
        ('evolved', '进化生成'),
    ]
    
    principle_type = models.CharField(max_length=50, choices=PRINCIPLE_TYPE_CHOICES, db_index=True, verbose_name='原则类型')
    
    # 原则内容
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    
    # 条件和场景
    conditions = JSONField(default=dict, blank=True, verbose_name='适用条件')
    applicable_scenarios = JSONField(default=list, blank=True, verbose_name='适用场景')
    
    # 来源
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, verbose_name='来源')
    derived_from = JSONField(default=list, blank=True, verbose_name='衍生自（记忆ID列表）')
    
    # 验证
    validation_count = models.IntegerField(default=0, verbose_name='验证次数')
    success_count = models.IntegerField(default=0, verbose_name='成功次数')
    fail_count = models.IntegerField(default=0, verbose_name='失败次数')
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='成功率')
    
    # 优先级和激活
    priority = models.IntegerField(default=50, verbose_name='优先级(0-100)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'trading_principle'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['principle_type', 'is_active']),
            models.Index(fields=['-priority', 'is_active']),
        ]
        verbose_name = '交易原则'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_principle_type_display()} - {self.title}"


class MarketPatternModel(models.Model):
    """市场模式识别"""
    
    PATTERN_TYPE_CHOICES = [
        ('technical', '技术形态'),
        ('sentiment', '情绪模式'),
        ('cycle', '周期模式'),
        ('correlation', '相关性模式'),
        ('anomaly', '异常模式'),
    ]
    
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPE_CHOICES, db_index=True, verbose_name='模式类型')
    
    # 模式信息
    name = models.CharField(max_length=200, verbose_name='模式名称')
    description = models.TextField(verbose_name='描述')
    
    # 模式特征
    features = JSONField(default=dict, verbose_name='特征')
    detection_rules = JSONField(default=dict, verbose_name='检测规则')
    
    # 历史表现
    occurrence_count = models.IntegerField(default=0, verbose_name='出现次数')
    success_count = models.IntegerField(default=0, verbose_name='成功次数')
    avg_return = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='平均收益率')
    
    # 适用市场
    applicable_markets = JSONField(default=list, blank=True, verbose_name='适用市场')
    applicable_symbols = JSONField(default=list, blank=True, verbose_name='适用标的')
    
    # 可信度
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.5, verbose_name='置信度')
    
    # 最后检测
    last_detected = models.DateTimeField(null=True, blank=True, verbose_name='最后检测到')
    last_detection_symbols = JSONField(default=list, blank=True, verbose_name='最后检测标的')
    
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'market_pattern'
        ordering = ['-confidence', '-occurrence_count']
        verbose_name = '市场模式'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_pattern_type_display()} - {self.name}"


class CognitiveBiasLogModel(models.Model):
    """认知偏见日志"""
    
    BIAS_TYPE_CHOICES = [
        ('overtrading', '过度交易'),
        ('anchoring', '锚定效应'),
        ('confirmation', '确认偏差'),
        ('loss_aversion', '损失厌恶'),
        ('recency', '近因效应'),
        ('overconfidence', '过度自信'),
        ('herding', '羊群效应'),
    ]
    
    bias_type = models.CharField(max_length=50, choices=BIAS_TYPE_CHOICES, db_index=True, verbose_name='偏见类型')
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='检测时间')
    
    # 偏见描述
    description = models.TextField(verbose_name='描述')
    evidence = JSONField(default=dict, verbose_name='证据')
    
    # 影响
    impact_level = models.IntegerField(verbose_name='影响等级(1-10)')
    affected_decisions = JSONField(default=list, blank=True, verbose_name='受影响的决策')
    
    # 纠正措施
    correction_measures = JSONField(default=list, blank=True, verbose_name='纠正措施')
    is_corrected = models.BooleanField(default=False, verbose_name='是否已纠正')
    corrected_at = models.DateTimeField(null=True, blank=True, verbose_name='纠正时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'cognitive_bias_log'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['bias_type', '-detected_at']),
            models.Index(fields=['is_corrected', '-detected_at']),
        ]
        verbose_name = '认知偏见日志'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.get_bias_type_display()} - {self.detected_at}"
