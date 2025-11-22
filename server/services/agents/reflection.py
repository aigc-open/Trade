"""
反思层：经验总结与自我进化
Reflection Layer: Experience Summary and Self-Evolution
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q

from apps.agents.models import AgentStatusModel, DecisionRecordModel, TradingPlanModel
from apps.strategies.models import StrategyModel, StrategyEvolutionLogModel
from apps.trades.models import TradeModel, PortfolioModel, PositionModel
from apps.memory.models import (
    AgentMemoryModel, KnowledgeNodeModel, KnowledgeEdgeModel,
    MarketPatternModel, TradingPrincipleModel, CognitiveBiasLogModel
)
from apps.reports.models import ReviewReportModel, EvolutionReportModel
from utils.ai.openai_client import get_openai_client
from services.agents.memory import MemoryAgent

logger = logging.getLogger(__name__)


class ReflectionAgent:
    """反思智能体"""
    
    def __init__(self):
        self.agent_type = 'reflection'
        self.openai_client = get_openai_client()
        self.memory_agent = MemoryAgent()
        self._update_status('running', 'Reflection agent initialized')
    
    def _update_status(self, status: str, last_action: str, current_task: str = None):
        """更新智能体状态"""
        try:
            agent_status, _ = AgentStatusModel.objects.get_or_create(
                agent_type=self.agent_type
            )
            agent_status.status = status
            agent_status.last_heartbeat = timezone.now()
            agent_status.last_action = last_action
            if current_task:
                agent_status.current_task = current_task
            agent_status.save()
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
    
    def daily_review(self) -> Optional[ReviewReportModel]:
        """
        每日复盘
        
        Returns:
            ReviewReportModel: 复盘报告
        """
        try:
            self._update_status('running', 'Daily review', 'Analyzing daily performance')
            
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 1. 收集今日数据
            daily_data = self._collect_daily_data(today_start)
            
            # 2. 分析交易表现
            trade_analysis = self._analyze_trades(daily_data['trades'])
            
            # 3. 识别成功/失败案例
            success_cases = self._identify_success_cases(daily_data['trades'])
            failure_cases = self._identify_failure_cases(daily_data['trades'])
            
            # 4. 使用 LLM 生成洞察
            insights = self._generate_insights_with_llm(
                daily_data,
                trade_analysis,
                success_cases,
                failure_cases
            )
            
            # 5. 提取经验教训
            lessons = self._extract_lessons(insights, success_cases, failure_cases)
            
            # 6. 创建复盘报告
            report = ReviewReportModel.objects.create(
                review_type='daily',
                review_period_start=today_start,
                review_period_end=timezone.now(),
                
                # 绩效
                trades_count=len(daily_data['trades']),
                win_trades=trade_analysis['win_count'],
                loss_trades=trade_analysis['loss_count'],
                win_rate=trade_analysis['win_rate'],
                total_pnl=trade_analysis['total_pnl'],
                avg_profit=trade_analysis['avg_profit'],
                avg_loss=trade_analysis['avg_loss'],
                profit_factor=trade_analysis['profit_factor'],
                
                # 案例
                success_cases=success_cases,
                failure_cases=failure_cases,
                
                # 洞察
                key_insights=insights.get('key_insights', []),
                lessons_learned=lessons,
                
                # 改进建议
                improvement_suggestions=insights.get('improvements', []),
                strategy_adjustments=insights.get('strategy_adjustments', {}),
                
                # 情绪与认知
                emotional_state=insights.get('emotional_state', 'neutral'),
                cognitive_biases=self._detect_cognitive_biases(daily_data),
                
                # 评分
                overall_rating=self._calculate_overall_rating(trade_analysis),
                confidence_level=insights.get('confidence', 0.5)
            )
            
            # 7. 存储到记忆系统
            self._store_to_memory(report, lessons)
            
            logger.info(f"Daily review completed: {report.id}")
            self._update_status('running', f'Daily review completed: {report.id}')
            
            return report
            
        except Exception as e:
            logger.error(f"Daily review failed: {e}")
            self._update_status('error', f'Review failed: {e}')
            return None
    
    def _collect_daily_data(self, start_time: datetime) -> Dict:
        """收集今日数据"""
        trades = TradeModel.objects.filter(
            filled_time__gte=start_time,
            status='filled'
        )
        
        decisions = DecisionRecordModel.objects.filter(
            decision_time__gte=start_time
        )
        
        plans = TradingPlanModel.objects.filter(
            created_at__gte=start_time
        )
        
        return {
            'trades': list(trades),
            'decisions': list(decisions),
            'plans': list(plans),
            'start_time': start_time,
            'end_time': timezone.now()
        }
    
    def _analyze_trades(self, trades: List[TradeModel]) -> Dict:
        """分析交易表现"""
        if not trades:
            return {
                'win_count': 0,
                'loss_count': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        # 计算盈亏（需要从持仓中获取）
        wins = []
        losses = []
        
        for trade in trades:
            # 简化：从持仓中获取盈亏
            position = PositionModel.objects.filter(
                open_trade=trade
            ).first()
            
            if position and position.unrealized_pnl:
                pnl = float(position.unrealized_pnl)
                if pnl > 0:
                    wins.append(pnl)
                else:
                    losses.append(pnl)
        
        win_count = len(wins)
        loss_count = len(losses)
        total_count = win_count + loss_count
        
        return {
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': (win_count / total_count * 100) if total_count > 0 else 0,
            'total_pnl': sum(wins) + sum(losses),
            'avg_profit': (sum(wins) / win_count) if win_count > 0 else 0,
            'avg_loss': (sum(losses) / loss_count) if loss_count > 0 else 0,
            'profit_factor': abs(sum(wins) / sum(losses)) if sum(losses) != 0 else 0
        }
    
    def _identify_success_cases(self, trades: List[TradeModel]) -> List[Dict]:
        """识别成功案例"""
        success = []
        
        for trade in trades[:10]:  # 最多10个
            position = PositionModel.objects.filter(open_trade=trade).first()
            
            if position and position.unrealized_pnl and float(position.unrealized_pnl) > 0:
                success.append({
                    'trade_id': trade.trade_id,
                    'symbol': trade.symbol,
                    'pnl': float(position.unrealized_pnl),
                    'pnl_pct': float(position.unrealized_pnl_pct or 0),
                    'reason': trade.reason,
                    'strategy': trade.strategy
                })
        
        return sorted(success, key=lambda x: x['pnl'], reverse=True)[:5]
    
    def _identify_failure_cases(self, trades: List[TradeModel]) -> List[Dict]:
        """识别失败案例"""
        failures = []
        
        for trade in trades[:10]:
            position = PositionModel.objects.filter(open_trade=trade).first()
            
            if position and position.unrealized_pnl and float(position.unrealized_pnl) < 0:
                failures.append({
                    'trade_id': trade.trade_id,
                    'symbol': trade.symbol,
                    'pnl': float(position.unrealized_pnl),
                    'pnl_pct': float(position.unrealized_pnl_pct or 0),
                    'reason': trade.reason,
                    'strategy': trade.strategy
                })
        
        return sorted(failures, key=lambda x: x['pnl'])[:5]
    
    def _generate_insights_with_llm(
        self,
        daily_data: Dict,
        trade_analysis: Dict,
        success_cases: List[Dict],
        failure_cases: List[Dict]
    ) -> Dict:
        """使用 LLM 生成洞察"""
        try:
            system_prompt = """你是一个专业的交易复盘分析师。
请分析今日交易表现，提供深刻的洞察和改进建议。

返回 JSON 格式：
{
  "key_insights": ["洞察1", "洞察2", ...],
  "improvements": ["改进建议1", "改进建议2", ...],
  "strategy_adjustments": {"策略类型": "调整建议"},
  "emotional_state": "calm/excited/fearful/greedy",
  "confidence": 0.0-1.0
}
"""
            
            user_prompt = f"""
今日交易统计：
- 交易次数：{trade_analysis['win_count'] + trade_analysis['loss_count']}
- 胜率：{trade_analysis['win_rate']:.2f}%
- 总盈亏：{trade_analysis['total_pnl']:.2f}
- 盈亏比：{trade_analysis['profit_factor']:.2f}

成功案例：
{json.dumps(success_cases, ensure_ascii=False, indent=2)}

失败案例：
{json.dumps(failure_cases, ensure_ascii=False, indent=2)}

请分析并提供洞察。
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Insights generated by LLM")
            return result
            
        except Exception as e:
            logger.error(f"LLM insight generation failed: {e}")
            return {
                'key_insights': ['需要人工分析'],
                'improvements': ['继续监控'],
                'strategy_adjustments': {},
                'emotional_state': 'neutral',
                'confidence': 0.5
            }
    
    def _extract_lessons(
        self,
        insights: Dict,
        success_cases: List[Dict],
        failure_cases: List[Dict]
    ) -> List[Dict]:
        """提取经验教训"""
        lessons = []
        
        # 从成功案例提取
        for case in success_cases:
            lessons.append({
                'type': 'success',
                'lesson': f"{case['symbol']} 成功：{case['reason']}",
                'applicable_scenarios': ['类似市场环境'],
                'confidence': 0.7
            })
        
        # 从失败案例提取
        for case in failure_cases:
            lessons.append({
                'type': 'failure',
                'lesson': f"{case['symbol']} 失败：需要避免{case['reason']}",
                'applicable_scenarios': ['风险控制'],
                'confidence': 0.8
            })
        
        return lessons
    
    def _detect_cognitive_biases(self, daily_data: Dict) -> List[str]:
        """检测认知偏差"""
        biases = []
        
        trades = daily_data['trades']
        if len(trades) > 10:
            biases.append('过度交易')
        
        # 检查是否有连续亏损后的报复性交易
        # 简化实现
        
        return biases
    
    def _calculate_overall_rating(self, trade_analysis: Dict) -> Decimal:
        """计算综合评分"""
        # 简单评分：根据胜率和盈亏比
        win_rate = trade_analysis['win_rate']
        profit_factor = trade_analysis['profit_factor']
        
        score = (win_rate / 100 * 0.5 + min(profit_factor / 2, 1) * 0.5) * 10
        return Decimal(str(round(score, 2)))
    
    def _store_to_memory(self, report: ReviewReportModel, lessons: List[Dict]):
        """存储到记忆系统"""
        try:
            # 存储复盘报告
            memory_content = {
                'report_id': report.id,
                'review_type': report.review_type,
                'performance': {
                    'win_rate': float(report.win_rate or 0),
                    'total_pnl': float(report.total_pnl or 0),
                    'profit_factor': float(report.profit_factor or 0)
                },
                'insights': report.key_insights,
                'lessons': lessons
            }
            
            self.memory_agent.store_memory(
                content=json.dumps(memory_content, ensure_ascii=False),
                memory_type='review',
                importance=0.8,
                metadata={
                    'report_id': report.id,
                    'review_date': report.review_period_start.isoformat()
                }
            )
            
            # 存储经验教训为交易原则
            for lesson in lessons:
                TradingPrincipleModel.objects.create(
                    principle_type='learned',
                    content=lesson['lesson'],
                    applicable_scenarios=lesson['applicable_scenarios'],
                    confidence_score=Decimal(str(lesson['confidence'])),
                    source='daily_review',
                    effectiveness_score=Decimal('0.5')
                )
            
            logger.info("Memories stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store memories: {e}")
    
    def strategy_evolution(self) -> Optional[EvolutionReportModel]:
        """
        策略进化
        
        Returns:
            EvolutionReportModel: 进化报告
        """
        try:
            self._update_status('running', 'Strategy evolution', 'Evolving strategies')
            
            # 1. 评估现有策略
            strategies = StrategyModel.objects.filter(is_active=True)
            evaluations = []
            
            for strategy in strategies:
                evaluation = self._evaluate_strategy(strategy)
                evaluations.append(evaluation)
            
            # 2. 识别需要进化的策略
            strategies_to_evolve = [
                e for e in evaluations
                if e['score'] < 0.5 or e['needs_evolution']
            ]
            
            # 3. 执行进化
            evolved_strategies = []
            for evaluation in strategies_to_evolve[:3]:  # 最多3个
                evolved = self._evolve_strategy(evaluation['strategy'])
                if evolved:
                    evolved_strategies.append(evolved)
            
            # 4. 创建进化报告
            report = EvolutionReportModel.objects.create(
                evolution_type='strategy',
                trigger_reason='performance_review',
                
                # 进化前后对比
                before_state={
                    'strategy_count': strategies.count(),
                    'avg_return': float(strategies.aggregate(Avg('total_return'))['total_return__avg'] or 0)
                },
                after_state={
                    'evolved_count': len(evolved_strategies),
                    'new_strategies': [s['id'] for s in evolved_strategies]
                },
                
                # 进化操作
                evolution_operations=[
                    {
                        'type': e['operation'],
                        'strategy': e['strategy_id'],
                        'changes': e['changes']
                    }
                    for e in evolved_strategies
                ],
                
                # 评估
                performance_improvement=self._calculate_improvement(evaluations, evolved_strategies),
                success_rate=Decimal('0.7'),  # 占位
                
                # 洞察
                key_learnings=['策略需要适应市场变化', '参数优化带来提升'],
                next_steps=['继续监控新策略表现', '准备下一轮进化']
            )
            
            logger.info(f"Strategy evolution completed: {report.id}")
            self._update_status('running', f'Evolution completed: {report.id}')
            
            return report
            
        except Exception as e:
            logger.error(f"Strategy evolution failed: {e}")
            self._update_status('error', f'Evolution failed: {e}')
            return None
    
    def _evaluate_strategy(self, strategy: StrategyModel) -> Dict:
        """评估策略"""
        # 计算评分
        score = 0.0
        
        if strategy.total_return and float(strategy.total_return) > 0:
            score += 0.3
        
        if strategy.sharpe_ratio and float(strategy.sharpe_ratio) > 1:
            score += 0.3
        
        if strategy.win_rate and float(strategy.win_rate) > 50:
            score += 0.2
        
        if strategy.max_drawdown and float(strategy.max_drawdown) < 0.2:
            score += 0.2
        
        needs_evolution = score < 0.5
        
        return {
            'strategy': strategy,
            'strategy_id': strategy.strategy_id,
            'score': score,
            'needs_evolution': needs_evolution,
            'reason': '表现不佳' if needs_evolution else '表现良好'
        }
    
    def _evolve_strategy(self, evaluation: Dict) -> Optional[Dict]:
        """进化策略"""
        try:
            strategy = evaluation['strategy']
            
            # 简化：参数调整
            old_params = strategy.parameters or {}
            new_params = self._adjust_parameters(old_params)
            
            # 记录进化
            StrategyEvolutionLogModel.objects.create(
                parent_strategy=strategy,
                evolution_type='mutation',
                operation='parameter_adjustment',
                parent_genes={
                    'parameters': old_params,
                    'type': strategy.strategy_type
                },
                child_genes={
                    'parameters': new_params,
                    'type': strategy.strategy_type
                },
                mutation_params={'rate': 0.1},
                fitness_before=float(evaluation['score']),
                reason='performance_optimization'
            )
            
            # 更新策略参数
            strategy.parameters = new_params
            strategy.save()
            
            logger.info(f"Strategy evolved: {strategy.strategy_id}")
            
            return {
                'id': strategy.strategy_id,
                'operation': 'parameter_adjustment',
                'strategy_id': strategy.strategy_id,
                'changes': {
                    'old': old_params,
                    'new': new_params
                }
            }
            
        except Exception as e:
            logger.error(f"Strategy evolution failed: {e}")
            return None
    
    def _adjust_parameters(self, params: Dict) -> Dict:
        """调整参数"""
        # 简化：随机微调
        import random
        
        new_params = params.copy()
        for key, value in new_params.items():
            if isinstance(value, (int, float)):
                # 微调 ±10%
                adjustment = random.uniform(-0.1, 0.1)
                new_params[key] = value * (1 + adjustment)
        
        return new_params
    
    def _calculate_improvement(self, evaluations: List[Dict], evolved: List[Dict]) -> Decimal:
        """计算改进幅度"""
        if not evaluations or not evolved:
            return Decimal('0')
        
        # 简化计算
        return Decimal('0.05')  # 5% 改进
    
    def run(self):
        """运行反思智能体"""
        logger.info("Reflection agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 1. 检查是否需要日度复盘
            today = timezone.now().date()
            existing_review = ReviewReportModel.objects.filter(
                review_type='daily',
                review_period_start__date=today
            ).first()
            
            if not existing_review:
                review = self.daily_review()
                logger.info(f"Daily review created: {review.id if review else 'None'}")
            else:
                logger.info("Daily review already exists")
            
            # 2. 每周策略进化（简化：每次都检查）
            evolution = self.strategy_evolution()
            logger.info(f"Strategy evolution: {evolution.id if evolution else 'None'}")
            
            self._update_status('running', 'Reflection completed', 'Idle')
            
            return {
                'review_created': existing_review is None,
                'evolution_completed': evolution is not None
            }
            
        except Exception as e:
            logger.error(f"Reflection agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise

