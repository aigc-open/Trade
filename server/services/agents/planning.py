"""
规划层：策略规划与多步推理
Planning Layer: Strategy Planning and Multi-step Reasoning
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q

from apps.agents.models import AgentStatusModel, TradingPlanModel, MarketOpportunityModel, DecisionRecordModel
from apps.strategies.models import StrategyModel, StrategyBacktestModel
from apps.trades.models import PortfolioModel, PositionModel
from apps.market_data.models import MarketDataModel, MarketSentimentModel
from utils.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)


class PlanningAgent:
    """规划智能体"""
    
    def __init__(self):
        self.agent_type = 'planning'
        self.openai_client = get_openai_client()
        self._update_status('running', 'Planning agent initialized')
    
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
    
    def create_trading_plan(
        self,
        market_context: Dict,
        portfolio: PortfolioModel,
        time_horizon: str = 'daily'
    ) -> Optional[TradingPlanModel]:
        """
        创建交易计划
        
        Args:
            market_context: 市场环境
            portfolio: 投资组合
            time_horizon: 计划周期 (intraday/daily/weekly/monthly)
            
        Returns:
            TradingPlanModel: 交易计划
        """
        try:
            self._update_status('running', 'Creating trading plan', f'Planning for {time_horizon}')
            
            # 1. 获取市场机会
            opportunities = self._get_market_opportunities()
            
            # 2. 获取最佳策略
            best_strategies = self._select_strategies(market_context, opportunities)
            
            # 3. 生成计划内容
            plan_content = self._generate_plan_content(
                market_context,
                opportunities,
                best_strategies,
                portfolio
            )
            
            # 4. 使用 LLM 优化计划
            optimized_plan = self._optimize_plan_with_llm(
                plan_content,
                market_context,
                time_horizon
            )
            
            # 5. 创建交易计划
            plan = TradingPlanModel.objects.create(
                plan_type=time_horizon,
                agent_type=self.agent_type,
                
                # 市场环境
                market_conditions=market_context,
                
                # 目标
                target_symbols=[opp.symbol for opp in opportunities[:10]],
                target_sectors=self._extract_sectors(opportunities),
                position_allocation=optimized_plan.get('allocation', {}),
                
                # 策略
                strategies=best_strategies,
                entry_conditions=optimized_plan.get('entry_conditions', []),
                exit_conditions=optimized_plan.get('exit_conditions', []),
                
                # 风控
                risk_limits={
                    'max_position_per_symbol': 0.05,
                    'max_sector_exposure': 0.30,
                    'max_daily_loss': 0.03,
                    'stop_loss_pct': 0.05,
                },
                
                # 计划
                action_steps=optimized_plan.get('action_steps', []),
                expected_return=optimized_plan.get('expected_return'),
                confidence_score=optimized_plan.get('confidence', 0.5),
                
                # 时间
                plan_start=timezone.now(),
                plan_end=self._calculate_plan_end(time_horizon),
                
                # 状态
                status='active',
                priority='medium' if len(opportunities) < 5 else 'high'
            )
            
            logger.info(f"Trading plan created: {plan.id}")
            self._update_status('running', f'Plan created: {plan.id}')
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create trading plan: {e}")
            self._update_status('error', f'Planning failed: {e}')
            return None
    
    def _get_market_opportunities(self) -> List[MarketOpportunityModel]:
        """获取市场机会"""
        # 获取最近识别的机会
        opportunities = MarketOpportunityModel.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
            confidence_score__gte=0.6
        ).order_by('-confidence_score')[:20]
        
        return list(opportunities)
    
    def _select_strategies(
        self,
        market_context: Dict,
        opportunities: List[MarketOpportunityModel]
    ) -> List[Dict]:
        """选择最佳策略"""
        try:
            # 获取活跃且表现良好的策略
            strategies = StrategyModel.objects.filter(
                is_active=True,
                total_return__gte=0  # 收益为正
            ).order_by('-sharpe_ratio')[:5]
            
            selected = []
            for strategy in strategies:
                # 检查策略是否适合当前市场
                if self._is_strategy_suitable(strategy, market_context):
                    selected.append({
                        'id': strategy.strategy_id,
                        'name': strategy.name,
                        'type': strategy.strategy_type,
                        'parameters': strategy.parameters,
                        'performance': {
                            'return': float(strategy.total_return or 0),
                            'sharpe': float(strategy.sharpe_ratio or 0),
                            'win_rate': float(strategy.win_rate or 0),
                        }
                    })
            
            return selected
            
        except Exception as e:
            logger.error(f"Strategy selection failed: {e}")
            return []
    
    def _is_strategy_suitable(self, strategy: StrategyModel, market_context: Dict) -> bool:
        """判断策略是否适合当前市场"""
        # 简单规则：根据市场状态选择策略类型
        market_trend = market_context.get('trend', 'neutral')
        
        if market_trend == 'bullish' and strategy.strategy_type in ['trend_following', 'momentum']:
            return True
        elif market_trend == 'bearish' and strategy.strategy_type in ['mean_reversion', 'defensive']:
            return True
        elif market_trend == 'neutral' and strategy.strategy_type in ['arbitrage', 'market_neutral']:
            return True
        
        return False
    
    def _generate_plan_content(
        self,
        market_context: Dict,
        opportunities: List[MarketOpportunityModel],
        strategies: List[Dict],
        portfolio: PortfolioModel
    ) -> Dict:
        """生成计划内容"""
        return {
            'market_summary': market_context,
            'opportunities': [
                {
                    'symbol': opp.symbol,
                    'type': opp.opportunity_type,
                    'confidence': float(opp.confidence_score),
                    'reason': opp.reason
                }
                for opp in opportunities[:10]
            ],
            'strategies': strategies,
            'portfolio_status': {
                'total_asset': float(portfolio.total_asset),
                'cash': float(portfolio.cash),
                'positions': PositionModel.objects.filter(
                    account_name=portfolio.account_name,
                    is_closed=False
                ).count()
            }
        }
    
    def _optimize_plan_with_llm(
        self,
        plan_content: Dict,
        market_context: Dict,
        time_horizon: str
    ) -> Dict:
        """使用 LLM 优化计划"""
        try:
            system_prompt = """你是一个专业的交易规划专家。
根据市场环境、机会和策略，制定详细的交易计划。

请返回 JSON 格式的计划，包括：
1. allocation: 资金分配方案 {symbol: percentage}
2. entry_conditions: 入场条件列表
3. exit_conditions: 出场条件列表
4. action_steps: 具体执行步骤
5. expected_return: 预期收益率
6. confidence: 信心评分 (0-1)
"""
            
            user_prompt = f"""
时间周期：{time_horizon}

市场环境：
{json.dumps(market_context, ensure_ascii=False, indent=2)}

交易机会：
{json.dumps(plan_content['opportunities'][:5], ensure_ascii=False, indent=2)}

可用策略：
{json.dumps(plan_content['strategies'], ensure_ascii=False, indent=2)}

组合状态：
{json.dumps(plan_content['portfolio_status'], ensure_ascii=False, indent=2)}

请制定一个{time_horizon}的交易计划。
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
            logger.info("Plan optimized by LLM")
            return result
            
        except Exception as e:
            logger.error(f"LLM optimization failed: {e}")
            # 返回默认计划
            return {
                'allocation': {},
                'entry_conditions': ['价格突破关键阻力位', '成交量放大'],
                'exit_conditions': ['止损触发', '止盈触发', '策略信号反转'],
                'action_steps': ['监控标的', '等待入场信号', '分批建仓', '动态调整'],
                'expected_return': 0.05,
                'confidence': 0.5
            }
    
    def _extract_sectors(self, opportunities: List[MarketOpportunityModel]) -> List[str]:
        """提取行业分布"""
        sectors = set()
        for opp in opportunities:
            if opp.reason:
                # 简单提取，实际应该从股票信息中获取
                sectors.add('technology')  # 占位
        return list(sectors)
    
    def _calculate_plan_end(self, time_horizon: str) -> datetime:
        """计算计划结束时间"""
        now = timezone.now()
        if time_horizon == 'intraday':
            return now + timedelta(hours=6)
        elif time_horizon == 'daily':
            return now + timedelta(days=1)
        elif time_horizon == 'weekly':
            return now + timedelta(weeks=1)
        elif time_horizon == 'monthly':
            return now + timedelta(days=30)
        return now + timedelta(days=1)
    
    def monitor_plan_execution(self, plan: TradingPlanModel) -> Dict:
        """监控计划执行"""
        try:
            # 1. 检查执行进度
            target_symbols = plan.target_symbols or []
            executed_decisions = DecisionRecordModel.objects.filter(
                symbol__in=target_symbols,
                is_executed=True,
                decision_time__gte=plan.plan_start
            ).count()
            
            # 2. 检查是否需要调整
            actual_performance = self._calculate_plan_performance(plan)
            
            # 3. 更新计划状态
            plan.actual_return = actual_performance.get('return')
            plan.completion_rate = (executed_decisions / len(target_symbols) * 100) if target_symbols else 0
            
            if plan.plan_end and timezone.now() > plan.plan_end:
                plan.status = 'completed'
            elif actual_performance.get('needs_adjustment'):
                plan.status = 'adjusting'
            
            plan.save()
            
            return {
                'plan_id': plan.id,
                'status': plan.status,
                'completion': plan.completion_rate,
                'performance': actual_performance
            }
            
        except Exception as e:
            logger.error(f"Plan monitoring failed: {e}")
            return {}
    
    def _calculate_plan_performance(self, plan: TradingPlanModel) -> Dict:
        """计算计划执行表现"""
        try:
            target_symbols = plan.target_symbols or []
            
            # 获取相关持仓
            positions = PositionModel.objects.filter(
                symbol__in=target_symbols,
                opened_at__gte=plan.plan_start,
                is_closed=False
            )
            
            total_pnl = sum([float(p.unrealized_pnl or 0) for p in positions])
            total_investment = sum([float(p.total_cost or 0) for p in positions])
            
            actual_return = (total_pnl / total_investment) if total_investment > 0 else 0
            
            # 判断是否需要调整
            expected_return = float(plan.expected_return or 0.05)
            needs_adjustment = actual_return < (expected_return * -0.5)  # 如果亏损超过预期的一半
            
            return {
                'return': actual_return,
                'pnl': total_pnl,
                'investment': total_investment,
                'positions': len(positions),
                'needs_adjustment': needs_adjustment
            }
            
        except Exception as e:
            logger.error(f"Performance calculation failed: {e}")
            return {'return': 0, 'needs_adjustment': False}
    
    def run(self):
        """运行规划智能体"""
        logger.info("Planning agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 1. 获取市场环境
            market_context = self._get_market_context()
            
            # 2. 获取主组合
            portfolio = PortfolioModel.objects.filter(
                account_name='simulation_main',
                is_active=True
            ).first()
            
            if not portfolio:
                logger.warning("No active portfolio found")
                return None
            
            # 3. 检查是否需要创建新计划
            active_plans = TradingPlanModel.objects.filter(
                status='active',
                plan_end__gte=timezone.now()
            ).count()
            
            if active_plans < 1:
                # 创建日度计划
                plan = self.create_trading_plan(
                    market_context=market_context,
                    portfolio=portfolio,
                    time_horizon='daily'
                )
                logger.info(f"New plan created: {plan.id if plan else 'None'}")
            
            # 4. 监控现有计划
            plans_to_monitor = TradingPlanModel.objects.filter(
                status__in=['active', 'adjusting']
            )
            
            monitored = []
            for plan in plans_to_monitor:
                result = self.monitor_plan_execution(plan)
                monitored.append(result)
            
            logger.info(f"Monitored {len(monitored)} plans")
            
            self._update_status(
                'running',
                f'Monitored {len(monitored)} plans',
                'Idle'
            )
            
            return {
                'plans_monitored': len(monitored),
                'active_plans': active_plans
            }
            
        except Exception as e:
            logger.error(f"Planning agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise
    
    def _get_market_context(self) -> Dict:
        """获取市场环境"""
        try:
            # 获取最新市场情绪
            sentiment = MarketSentimentModel.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            ).order_by('-created_at').first()
            
            context = {
                'timestamp': timezone.now().isoformat(),
                'trend': 'neutral',
                'volatility': 'medium',
                'sentiment': sentiment.sentiment if sentiment else 'neutral'
            }
            
            if sentiment:
                if sentiment.fear_greed_index:
                    if sentiment.fear_greed_index > 60:
                        context['trend'] = 'bullish'
                    elif sentiment.fear_greed_index < 40:
                        context['trend'] = 'bearish'
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            return {'timestamp': timezone.now().isoformat(), 'trend': 'neutral'}

