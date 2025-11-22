"""
决策层：多智能体辩论与策略生成
Multi-Agent Debate and Decision Making
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.agents.models import (
    AgentStatusModel, DecisionRecordModel, MarketOpportunityModel
)
from apps.market_data.models import MarketDataModel
from apps.strategies.models import StrategyModel
from utils.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)


class MultiAgentDebate:
    """多智能体辩论系统"""
    
    def __init__(self):
        self.openai_client = get_openai_client()
    
    def aggressive_analysis(self, symbol: str, market_data: Dict) -> Dict:
        """激进派分析 - 追求高收益"""
        try:
            prompt = f"""
            你是一位激进的交易员，追求高收益和高风险机会。
            
            标的: {symbol}
            当前价格: {market_data.get('current_price')}
            涨跌幅: {market_data.get('change_pct')}%
            成交量: {market_data.get('volume')}
            
            请从激进的角度分析：
            1. 这是否是一个高收益机会？
            2. 预期收益率是多少？
            3. 为什么现在应该进场？
            4. 建议的仓位比例（1-10%）
            
            以JSON格式返回：
            {{
                "recommendation": "buy/sell/hold",
                "confidence": 0-100,
                "expected_return": 预期收益率,
                "position_pct": 建议仓位,
                "rationale": "理由说明（50字以内）"
            }}
            """
            
            messages = [
                {"role": "system", "content": "你是激进派交易智能体，追求高收益。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.fast_completion(
                messages, 
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Aggressive analysis failed: {e}")
            return {
                "recommendation": "hold",
                "confidence": 0,
                "expected_return": 0,
                "position_pct": 0,
                "rationale": f"分析失败: {str(e)}"
            }
    
    def conservative_analysis(self, symbol: str, market_data: Dict, aggressive_view: Dict) -> Dict:
        """保守派分析 - 关注风险"""
        try:
            prompt = f"""
            你是一位保守的交易员，关注风险控制。
            
            标的: {symbol}
            当前价格: {market_data.get('current_price')}
            涨跌幅: {market_data.get('change_pct')}%
            
            激进派建议: {aggressive_view.get('recommendation')} 
            理由: {aggressive_view.get('rationale')}
            预期收益: {aggressive_view.get('expected_return')}%
            
            请从保守的角度分析：
            1. 这个建议有什么风险？
            2. 最坏情况会如何？
            3. 你的风险评估（1-10分）
            4. 你会如何调整这个建议？
            
            以JSON格式返回：
            {{
                "agreement": true/false,
                "risk_score": 1-10,
                "concerns": ["担忧1", "担忧2"],
                "alternative": "替代建议",
                "adjusted_position": 调整后的仓位
            }}
            """
            
            messages = [
                {"role": "system", "content": "你是保守派交易智能体，关注风险。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.fast_completion(
                messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Conservative analysis failed: {e}")
            return {
                "agreement": False,
                "risk_score": 10,
                "concerns": [f"分析失败: {str(e)}"],
                "alternative": "hold",
                "adjusted_position": 0
            }
    
    def quant_validation(self, symbol: str, market_data: Dict) -> Dict:
        """量化派验证 - 数据驱动"""
        try:
            # 获取历史数据
            recent_data = MarketDataModel.objects.filter(
                symbol=symbol
            ).order_by('-timestamp')[:20]
            
            if not recent_data:
                return {
                    "validation": "insufficient_data",
                    "win_rate": 0,
                    "avg_return": 0,
                    "statistical_significance": False
                }
            
            # 简单的统计分析
            prices = [float(d.close) for d in recent_data]
            returns = [(prices[i] - prices[i+1]) / prices[i+1] * 100 
                      for i in range(len(prices)-1)]
            
            positive_returns = [r for r in returns if r > 0]
            win_rate = len(positive_returns) / len(returns) * 100 if returns else 0
            avg_return = sum(returns) / len(returns) if returns else 0
            
            prompt = f"""
            量化数据验证：
            
            标的: {symbol}
            近20日数据:
            - 胜率: {win_rate:.1f}%
            - 平均收益: {avg_return:.2f}%
            - 当前价格: {market_data.get('current_price')}
            - 近期趋势: {"上涨" if avg_return > 0 else "下跌"}
            
            请从量化角度评估：
            1. 这个标的的历史表现如何？
            2. 当前时机是否合适？
            3. 建议的持仓时长
            
            以JSON格式返回：
            {{
                "validation": "positive/negative/neutral",
                "win_rate": {win_rate},
                "avg_return": {avg_return},
                "statistical_significance": true/false,
                "recommended_holding_days": 天数
            }}
            """
            
            messages = [
                {"role": "system", "content": "你是量化派交易智能体，基于数据分析。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.fast_completion(
                messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response)
            result['win_rate'] = win_rate
            result['avg_return'] = avg_return
            
            return result
            
        except Exception as e:
            logger.error(f"Quant validation failed: {e}")
            return {
                "validation": "error",
                "win_rate": 0,
                "avg_return": 0,
                "statistical_significance": False,
                "error": str(e)
            }
    
    def judge_decision(
        self, 
        symbol: str,
        aggressive_view: Dict,
        conservative_view: Dict,
        quant_view: Dict,
        market_data: Dict
    ) -> Dict:
        """裁判综合判断"""
        try:
            prompt = f"""
            作为裁判，你需要综合三方意见做出最终决策。
            
            标的: {symbol}
            当前价格: {market_data.get('current_price')}
            
            【激进派】
            建议: {aggressive_view.get('recommendation')}
            置信度: {aggressive_view.get('confidence')}%
            预期收益: {aggressive_view.get('expected_return')}%
            理由: {aggressive_view.get('rationale')}
            
            【保守派】
            是否同意: {conservative_view.get('agreement')}
            风险评分: {conservative_view.get('risk_score')}/10
            担忧: {', '.join(conservative_view.get('concerns', []))}
            替代建议: {conservative_view.get('alternative')}
            
            【量化派】
            验证结果: {quant_view.get('validation')}
            历史胜率: {quant_view.get('win_rate', 0):.1f}%
            平均收益: {quant_view.get('avg_return', 0):.2f}%
            
            请做出最终决策：
            1. 是否执行交易？
            2. 具体操作（buy/sell/hold）
            3. 仓位大小（考虑风险）
            4. 置信度（0-100）
            5. 决策理由
            
            以JSON格式返回：
            {{
                "final_decision": "buy/sell/hold",
                "action_type": "开仓/加仓/减仓/平仓/观望",
                "position_pct": 实际仓位比例,
                "confidence": 0-100,
                "reasoning": "决策理由（100字以内）",
                "stop_loss_pct": 止损比例,
                "take_profit_pct": 止盈比例
            }}
            """
            
            messages = [
                {"role": "system", "content": "你是裁判智能体，综合判断并做出最终决策。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.chat_completion(
                messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Judge decision failed: {e}")
            return {
                "final_decision": "hold",
                "action_type": "观望",
                "position_pct": 0,
                "confidence": 0,
                "reasoning": f"决策失败: {str(e)}",
                "stop_loss_pct": 3,
                "take_profit_pct": 8
            }


class DecisionAgent:
    """决策智能体"""
    
    def __init__(self):
        self.agent_type = 'decision'
        self.debate_system = MultiAgentDebate()
        self._update_status('running', 'Decision agent initialized')
    
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
    
    def make_decision(self, opportunity: MarketOpportunityModel) -> Optional[DecisionRecordModel]:
        """
        对市场机会进行决策
        
        Args:
            opportunity: 市场机会对象
            
        Returns:
            DecisionRecordModel: 决策记录
        """
        try:
            symbol = opportunity.symbol
            self._update_status('running', f'Making decision for {symbol}', f'Analyzing {symbol}')
            
            # 获取最新市场数据
            latest_data = MarketDataModel.objects.filter(
                symbol=symbol
            ).order_by('-timestamp').first()
            
            if not latest_data:
                logger.warning(f"No market data for {symbol}")
                return None
            
            market_data = {
                'current_price': float(latest_data.close),
                'change_pct': float(latest_data.change_pct) if latest_data.change_pct else 0,
                'volume': int(latest_data.volume),
                'high': float(latest_data.high),
                'low': float(latest_data.low),
            }
            
            logger.info(f"Starting multi-agent debate for {symbol}")
            
            # 1. 激进派分析
            aggressive_view = self.debate_system.aggressive_analysis(symbol, market_data)
            logger.info(f"Aggressive view: {aggressive_view.get('recommendation')}")
            
            # 2. 保守派分析
            conservative_view = self.debate_system.conservative_analysis(
                symbol, market_data, aggressive_view
            )
            logger.info(f"Conservative agreement: {conservative_view.get('agreement')}")
            
            # 3. 量化派验证
            quant_view = self.debate_system.quant_validation(symbol, market_data)
            logger.info(f"Quant validation: {quant_view.get('validation')}")
            
            # 4. 裁判决策
            final_decision = self.debate_system.judge_decision(
                symbol, aggressive_view, conservative_view, quant_view, market_data
            )
            logger.info(f"Final decision: {final_decision.get('final_decision')}")
            
            # 5. 保存决策记录
            decision = self._save_decision(
                symbol=symbol,
                opportunity=opportunity,
                aggressive_view=aggressive_view,
                conservative_view=conservative_view,
                quant_view=quant_view,
                final_decision=final_decision,
                market_data=market_data
            )
            
            self._update_status('running', f'Decision made for {symbol}', 'Idle')
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision making failed for {opportunity.symbol}: {e}")
            self._update_status('error', f'Decision failed: {e}')
            return None
    
    def _save_decision(
        self,
        symbol: str,
        opportunity: MarketOpportunityModel,
        aggressive_view: Dict,
        conservative_view: Dict,
        quant_view: Dict,
        final_decision: Dict,
        market_data: Dict
    ) -> DecisionRecordModel:
        """保存决策记录"""
        try:
            # 确定决策类型
            decision_type_map = {
                'buy': 'buy',
                'sell': 'sell',
                'hold': 'hold'
            }
            decision_type = decision_type_map.get(
                final_decision.get('final_decision', 'hold'),
                'hold'
            )
            
            # 确定置信度等级
            confidence_score = final_decision.get('confidence', 50)
            if confidence_score >= 80:
                confidence_level = 'very_high'
            elif confidence_score >= 60:
                confidence_level = 'high'
            elif confidence_score >= 40:
                confidence_level = 'medium'
            elif confidence_score >= 20:
                confidence_level = 'low'
            else:
                confidence_level = 'very_low'
            
            # 计算目标价格和止损止盈
            current_price = Decimal(str(market_data['current_price']))
            stop_loss_pct = Decimal(str(final_decision.get('stop_loss_pct', 3)))
            take_profit_pct = Decimal(str(final_decision.get('take_profit_pct', 8)))
            
            if decision_type == 'buy':
                stop_loss = current_price * (1 - stop_loss_pct / 100)
                take_profit = current_price * (1 + take_profit_pct / 100)
            elif decision_type == 'sell':
                stop_loss = current_price * (1 + stop_loss_pct / 100)
                take_profit = current_price * (1 - take_profit_pct / 100)
            else:
                stop_loss = None
                take_profit = None
            
            # 生成辩论摘要
            debate_summary = f"""
            激进派（{aggressive_view.get('confidence', 0)}%置信）: {aggressive_view.get('rationale', 'N/A')}
            保守派（风险{conservative_view.get('risk_score', 0)}/10）: {', '.join(conservative_view.get('concerns', ['无']))}
            量化派（胜率{quant_view.get('win_rate', 0):.1f}%）: {quant_view.get('validation', 'N/A')}
            最终决策: {final_decision.get('reasoning', 'N/A')}
            """
            
            # 创建决策记录
            decision = DecisionRecordModel.objects.create(
                symbol=symbol,
                decision_type=decision_type,
                
                # 提案内容
                proposal={
                    'opportunity_id': opportunity.id,
                    'opportunity_type': opportunity.opportunity_type,
                    'current_price': float(current_price),
                },
                target_price=current_price,
                target_position_pct=Decimal(str(final_decision.get('position_pct', 0))),
                
                # 多智能体观点
                aggressive_view=aggressive_view.get('rationale', ''),
                conservative_view=str(conservative_view.get('concerns', [])),
                quant_analysis=quant_view,
                debate_summary=debate_summary.strip(),
                
                # 最终决策
                final_decision=final_decision.get('reasoning', ''),
                confidence_level=confidence_level,
                confidence_score=Decimal(str(confidence_score)),
                
                # 风控
                stop_loss=stop_loss,
                take_profit=take_profit,
                max_loss_amount=None,  # 执行层会计算
                
                # 执行状态
                is_executed=False,
            )
            
            # 更新机会状态
            opportunity.decision = decision
            opportunity.status = 'validated' if decision_type != 'hold' else 'invalid'
            opportunity.save()
            
            logger.info(f"Decision saved: {decision.id} for {symbol}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to save decision: {e}")
            raise
    
    def batch_decide(self, opportunities: List[MarketOpportunityModel]) -> List[DecisionRecordModel]:
        """批量决策"""
        decisions = []
        for opportunity in opportunities:
            decision = self.make_decision(opportunity)
            if decision:
                decisions.append(decision)
        
        return decisions
    
    def run(self):
        """运行决策智能体"""
        logger.info("Decision agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 获取待决策的机会
            opportunities = MarketOpportunityModel.objects.filter(
                status__in=['identified', 'analyzing']
            ).order_by('-identified_at')[:5]  # 限制数量
            
            if not opportunities:
                logger.info("No opportunities to decide")
                self._update_status('running', 'No opportunities found', 'Idle')
                return []
            
            logger.info(f"Found {len(opportunities)} opportunities to analyze")
            
            # 批量决策
            decisions = self.batch_decide(opportunities)
            
            logger.info(f"Made {len(decisions)} decisions")
            self._update_status('running', f'Made {len(decisions)} decisions', 'Idle')
            
            return decisions
            
        except Exception as e:
            logger.error(f"Decision agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise

