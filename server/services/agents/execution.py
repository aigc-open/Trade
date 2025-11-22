"""
执行层：交易执行与风险控制
Execution Layer: Trade Execution and Risk Management
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.agents.models import AgentStatusModel, DecisionRecordModel
from apps.trades.models import TradeModel, PositionModel, PortfolioModel, RiskControlLogModel
from apps.market_data.models import MarketDataModel

logger = logging.getLogger(__name__)


class RiskController:
    """风控系统"""
    
    def __init__(self, portfolio: PortfolioModel):
        self.portfolio = portfolio
    
    def check_pre_trade_risk(self, decision: DecisionRecordModel) -> Dict[str, Any]:
        """
        交易前风控检查
        
        Returns:
            Dict: {
                'passed': bool,
                'action': 'allow/reject/adjust',
                'issues': List[str],
                'adjusted_position': Optional[Decimal]
            }
        """
        issues = []
        action = 'allow'
        adjusted_position = decision.target_position_pct
        
        try:
            # 1. 检查单笔交易风险敞口
            max_single_trade = Decimal('0.05')  # 5%
            if decision.target_position_pct and decision.target_position_pct > max_single_trade:
                issues.append(f"单笔交易超限: {decision.target_position_pct}% > {max_single_trade}%")
                adjusted_position = max_single_trade
                action = 'adjust'
            
            # 2. 检查仓位集中度
            current_positions = PositionModel.objects.filter(
                account_name=self.portfolio.account_name,
                is_closed=False
            )
            
            total_position_value = sum([
                float(p.market_value) for p in current_positions if p.market_value
            ])
            
            max_position = Decimal('0.30')  # 30%
            symbol_position_value = total_position_value * float(decision.target_position_pct or 0)
            
            if symbol_position_value > float(self.portfolio.total_asset) * float(max_position):
                issues.append(f"仓位集中度超限: 目标{decision.target_position_pct}% > 最大{max_position}%")
                action = 'adjust'
            
            # 3. 检查可用资金
            required_cash = float(self.portfolio.total_asset) * float(decision.target_position_pct or 0)
            if required_cash > float(self.portfolio.available_cash):
                issues.append(f"可用资金不足: 需要{required_cash}, 可用{self.portfolio.available_cash}")
                # 调整为可用资金允许的最大仓位
                adjusted_position = Decimal(str(float(self.portfolio.available_cash) / float(self.portfolio.total_asset)))
                action = 'adjust'
            
            # 4. 检查当日亏损
            if self.portfolio.today_pnl and float(self.portfolio.today_pnl) < 0:
                max_daily_loss = Decimal('-0.05')  # -5%
                if self.portfolio.today_return and self.portfolio.today_return < max_daily_loss:
                    issues.append(f"当日亏损达到限额: {self.portfolio.today_return}%")
                    action = 'reject'
            
            # 5. 检查最大回撤
            if self.portfolio.max_drawdown and float(self.portfolio.max_drawdown) > 0.15:
                issues.append(f"最大回撤超限: {self.portfolio.max_drawdown}% > 15%")
                action = 'reject'
            
            passed = (action == 'allow')
            
            # 记录风控日志
            RiskControlLogModel.objects.create(
                risk_type='pre_trade',
                action=action,
                portfolio=self.portfolio,
                risk_indicators={
                    'target_position': float(decision.target_position_pct or 0),
                    'available_cash': float(self.portfolio.available_cash),
                    'today_return': float(self.portfolio.today_return or 0),
                    'max_drawdown': float(self.portfolio.max_drawdown or 0),
                },
                trigger_rules=issues,
                description=f"交易前风控: {decision.symbol}",
                recommendation=f"建议{'执行' if passed else '拒绝'}交易",
                executed=True
            )
            
            return {
                'passed': passed,
                'action': action,
                'issues': issues,
                'adjusted_position': adjusted_position
            }
            
        except Exception as e:
            logger.error(f"Pre-trade risk check failed: {e}")
            return {
                'passed': False,
                'action': 'reject',
                'issues': [f"风控检查失败: {str(e)}"],
                'adjusted_position': None
            }
    
    def check_in_trade_risk(self, position: PositionModel) -> Dict[str, Any]:
        """交易中风控监控"""
        alerts = []
        
        try:
            # 检查单标的亏损
            if position.unrealized_pnl_pct and float(position.unrealized_pnl_pct) < -5:
                alerts.append({
                    'level': 'high',
                    'message': f"{position.symbol} 浮亏{position.unrealized_pnl_pct}%"
                })
            
            # 检查止损触发
            if position.stop_loss and position.current_price:
                if float(position.current_price) <= float(position.stop_loss):
                    alerts.append({
                        'level': 'critical',
                        'message': f"{position.symbol} 触发止损: {position.current_price} <= {position.stop_loss}"
                    })
            
            # 检查止盈触发
            if position.take_profit and position.current_price:
                if float(position.current_price) >= float(position.take_profit):
                    alerts.append({
                        'level': 'info',
                        'message': f"{position.symbol} 触发止盈: {position.current_price} >= {position.take_profit}"
                    })
            
            return {
                'has_alert': len(alerts) > 0,
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"In-trade risk check failed: {e}")
            return {'has_alert': False, 'alerts': []}


class ExecutionAgent:
    """执行智能体"""
    
    def __init__(self, portfolio_name: str = 'simulation_main'):
        self.agent_type = 'execution'
        self.portfolio_name = portfolio_name
        self.portfolio = self._get_or_create_portfolio()
        self.risk_controller = RiskController(self.portfolio)
        self._update_status('running', 'Execution agent initialized')
    
    def _get_or_create_portfolio(self) -> PortfolioModel:
        """获取或创建投资组合"""
        portfolio, created = PortfolioModel.objects.get_or_create(
            account_name=self.portfolio_name,
            defaults={
                'account_type': 'simulation',
                'initial_capital': Decimal('1000000'),
                'total_asset': Decimal('1000000'),
                'cash': Decimal('1000000'),
                'available_cash': Decimal('1000000'),
                'is_active': True
            }
        )
        if created:
            logger.info(f"Created new portfolio: {self.portfolio_name}")
        return portfolio
    
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
    
    def execute_decision(self, decision: DecisionRecordModel) -> Optional[TradeModel]:
        """
        执行决策
        
        Args:
            decision: 决策记录
            
        Returns:
            TradeModel: 交易记录
        """
        try:
            symbol = decision.symbol
            self._update_status('running', f'Executing decision for {symbol}', f'Processing {symbol}')
            
            # 1. 风控检查
            risk_check = self.risk_controller.check_pre_trade_risk(decision)
            
            if risk_check['action'] == 'reject':
                logger.warning(f"Trade rejected for {symbol}: {risk_check['issues']}")
                decision.execution_result = {
                    'status': 'rejected',
                    'reason': risk_check['issues']
                }
                decision.save()
                return None
            
            # 2. 获取当前市场价格
            latest_data = MarketDataModel.objects.filter(
                symbol=symbol
            ).order_by('-timestamp').first()
            
            if not latest_data:
                logger.error(f"No market data for {symbol}")
                return None
            
            current_price = latest_data.close
            
            # 3. 计算交易数量
            if risk_check['action'] == 'adjust':
                position_pct = risk_check['adjusted_position']
            else:
                position_pct = decision.target_position_pct
            
            total_amount = float(self.portfolio.available_cash) * float(position_pct)
            quantity = int(total_amount / float(current_price))
            
            if quantity <= 0:
                logger.warning(f"Invalid quantity for {symbol}: {quantity}")
                return None
            
            # 4. 创建交易记录（模拟执行）
            trade = self._create_trade(
                decision=decision,
                price=current_price,
                quantity=quantity,
                risk_check=risk_check
            )
            
            # 5. 更新决策状态
            decision.is_executed = True
            decision.execution_time = timezone.now()
            decision.execution_result = {
                'trade_id': trade.trade_id,
                'executed_price': float(current_price),
                'executed_quantity': quantity,
                'risk_check': risk_check['issues']
            }
            decision.save()
            
            # 6. 更新或创建持仓
            if trade.action == 'BUY':
                self._update_position(trade, 'open')
            
            logger.info(f"Trade executed: {trade.trade_id}")
            self._update_status('running', f'Executed trade for {symbol}', 'Idle')
            
            return trade
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            self._update_status('error', f'Execution failed: {e}')
            return None
    
    def _create_trade(
        self,
        decision: DecisionRecordModel,
        price: Decimal,
        quantity: int,
        risk_check: Dict
    ) -> TradeModel:
        """创建交易记录"""
        import uuid
        
        action_map = {
            'buy': 'BUY',
            'sell': 'SELL',
            'hold': 'BUY'  # hold 默认为观望，不应该执行
        }
        
        action = action_map.get(decision.decision_type, 'BUY')
        
        trade_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
        
        total_amount = price * quantity
        commission = total_amount * Decimal('0.0003')  # 0.03% 手续费
        
        trade = TradeModel.objects.create(
            trade_id=trade_id,
            symbol=decision.symbol,
            action=action,
            account_type='simulation',
            account_name=self.portfolio_name,
            
            # 价格数量
            order_price=price,
            order_quantity=quantity,
            filled_price=price,  # 模拟盘立即成交
            filled_quantity=quantity,
            
            # 状态
            status='filled',
            filled_time=timezone.now(),
            
            # 成本
            commission=commission,
            slippage=Decimal('0'),
            total_amount=total_amount + commission,
            
            # 关联
            strategy=decision.proposal.get('strategy_id') if decision.proposal else None,
            decision=decision,
            decision_process=decision.debate_summary,
            reason=decision.final_decision,
            
            # 风控
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
            
            # 执行质量
            execution_quality={
                'risk_check': risk_check,
                'execution_time_ms': 100  # 模拟
            }
        )
        
        return trade
    
    def _update_position(self, trade: TradeModel, action: str):
        """更新持仓"""
        try:
            if action == 'open':
                # 开仓
                position, created = PositionModel.objects.get_or_create(
                    symbol=trade.symbol,
                    account_name=self.portfolio_name,
                    is_closed=False,
                    defaults={
                        'account_type': 'simulation',
                        'quantity': trade.filled_quantity,
                        'available_quantity': trade.filled_quantity,
                        'avg_cost': trade.filled_price,
                        'total_cost': trade.total_amount,
                        'current_price': trade.filled_price,
                        'market_value': trade.filled_price * trade.filled_quantity,
                        'stop_loss': trade.stop_loss,
                        'take_profit': trade.take_profit,
                        'opened_at': timezone.now(),
                        'open_trade': trade,
                    }
                )
                
                if not created:
                    # 加仓
                    total_quantity = position.quantity + trade.filled_quantity
                    total_cost = float(position.total_cost) + float(trade.total_amount)
                    position.quantity = total_quantity
                    position.available_quantity = total_quantity
                    position.avg_cost = Decimal(str(total_cost / total_quantity))
                    position.total_cost = Decimal(str(total_cost))
                    position.save()
                
                # 更新组合
                self.portfolio.cash -= trade.total_amount
                self.portfolio.available_cash = self.portfolio.cash
                self.portfolio.save()
                
                logger.info(f"Position updated: {position.symbol}")
                
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
    
    def monitor_positions(self):
        """监控持仓"""
        try:
            positions = PositionModel.objects.filter(
                account_name=self.portfolio_name,
                is_closed=False
            )
            
            alerts = []
            
            for position in positions:
                # 更新当前价格
                latest_data = MarketDataModel.objects.filter(
                    symbol=position.symbol
                ).order_by('-timestamp').first()
                
                if latest_data:
                    position.current_price = latest_data.close
                    position.market_value = position.current_price * position.quantity
                    position.unrealized_pnl = position.market_value - position.total_cost
                    position.unrealized_pnl_pct = (position.unrealized_pnl / position.total_cost) * 100
                    position.save()
                    
                    # 风控检查
                    risk_result = self.risk_controller.check_in_trade_risk(position)
                    if risk_result['has_alert']:
                        alerts.extend(risk_result['alerts'])
            
            logger.info(f"Monitored {len(positions)} positions, {len(alerts)} alerts")
            
            return {'positions': len(positions), 'alerts': alerts}
            
        except Exception as e:
            logger.error(f"Position monitoring failed: {e}")
            return {'positions': 0, 'alerts': []}
    
    def run(self):
        """运行执行智能体"""
        logger.info("Execution agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 1. 执行待执行的决策
            pending_decisions = DecisionRecordModel.objects.filter(
                is_executed=False,
                decision_type__in=['buy', 'sell']
            ).order_by('-decision_time')[:5]
            
            executed_count = 0
            for decision in pending_decisions:
                trade = self.execute_decision(decision)
                if trade:
                    executed_count += 1
            
            logger.info(f"Executed {executed_count} trades")
            
            # 2. 监控现有持仓
            monitor_result = self.monitor_positions()
            
            self._update_status(
                'running',
                f'Executed {executed_count} trades, monitored {monitor_result["positions"]} positions',
                'Idle'
            )
            
            return {
                'executed': executed_count,
                'monitored': monitor_result['positions'],
                'alerts': monitor_result['alerts']
            }
            
        except Exception as e:
            logger.error(f"Execution agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise

