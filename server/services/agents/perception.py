"""
感知层：市场数据采集和实时监控
Market Perception and Real-time Monitoring
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from apps.market_data.models import (
    MarketDataModel, MarketIndexModel, 
    MarketSentimentModel, NewsEventModel
)
from apps.agents.models import AgentStatusModel
from utils.ai.openai_client import get_openai_client
import json

logger = logging.getLogger(__name__)


class PerceptionAgent:
    """感知智能体"""
    
    def __init__(self):
        self.agent_type = 'perception'
        self.openai_client = get_openai_client()
        self._update_status('running', 'Perception agent initialized')
    
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
    
    def perceive_market(self) -> Dict[str, Any]:
        """
        全面感知市场状态
        
        Returns:
            Dict: 市场感知结果
        """
        try:
            self._update_status('running', 'Perceiving market', 'Market state analysis')
            
            perception_result = {
                'timestamp': timezone.now().isoformat(),
                'market_overview': self._get_market_overview(),
                'sentiment': self._analyze_market_sentiment(),
                'anomalies': self._detect_anomalies(),
                'opportunities': self._scan_opportunities(),
                'risk_signals': self._detect_risk_signals(),
            }
            
            logger.info("Market perception completed")
            return perception_result
            
        except Exception as e:
            logger.error(f"Market perception failed: {e}")
            self._update_status('error', f'Perception failed: {e}')
            raise
    
    def _get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        try:
            # 获取主要指数最新数据
            recent_indices = MarketIndexModel.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).order_by('index_code', '-timestamp').distinct('index_code')[:5]
            
            overview = {
                'indices': [],
                'market_breadth': {},
                'volume_profile': {}
            }
            
            for index in recent_indices:
                overview['indices'].append({
                    'code': index.index_code,
                    'name': index.index_name,
                    'value': float(index.value),
                    'change_pct': float(index.change_pct),
                    'rise_count': index.rise_count,
                    'fall_count': index.fall_count,
                })
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get market overview: {e}")
            return {}
    
    def _analyze_market_sentiment(self) -> Dict[str, Any]:
        """分析市场情绪"""
        try:
            # 获取最新情绪数据
            latest_sentiment = MarketSentimentModel.objects.order_by('-timestamp').first()
            
            if not latest_sentiment:
                return {'status': 'no_data'}
            
            sentiment_data = {
                'vix': float(latest_sentiment.vix) if latest_sentiment.vix else None,
                'fear_greed_index': float(latest_sentiment.fear_greed_index) if latest_sentiment.fear_greed_index else None,
                'put_call_ratio': float(latest_sentiment.put_call_ratio) if latest_sentiment.put_call_ratio else None,
                'social_sentiment': float(latest_sentiment.social_sentiment_score) if latest_sentiment.social_sentiment_score else None,
                'interpretation': self._interpret_sentiment(latest_sentiment)
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return {}
    
    def _interpret_sentiment(self, sentiment: MarketSentimentModel) -> str:
        """
        使用AI解读市场情绪
        
        Args:
            sentiment: 市场情绪数据
            
        Returns:
            str: 情绪解读
        """
        try:
            prompt = f"""
            请分析以下市场情绪指标，给出简洁的解读（50字以内）：
            
            VIX指数: {sentiment.vix}
            恐慌贪婪指数: {sentiment.fear_greed_index}
            看跌看涨比: {sentiment.put_call_ratio}
            社交媒体情绪: {sentiment.social_sentiment_score}
            
            当前市场情绪如何？应该采取什么策略？
            """
            
            messages = [
                {"role": "system", "content": "你是一位专业的市场分析师，擅长解读市场情绪指标。"},
                {"role": "user", "content": prompt}
            ]
            
            interpretation = self.openai_client.fast_completion(messages, temperature=0.3)
            return interpretation.strip()
            
        except Exception as e:
            logger.error(f"Failed to interpret sentiment: {e}")
            return "情绪解读失败"
    
    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """检测市场异常"""
        anomalies = []
        
        try:
            # 检测价格异常波动
            recent_data = MarketDataModel.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).select_related('symbol')
            
            for data in recent_data:
                if data.change_pct and abs(float(data.change_pct)) > 5:  # 涨跌幅超过5%
                    anomalies.append({
                        'type': 'price_spike',
                        'symbol': data.symbol,
                        'change_pct': float(data.change_pct),
                        'timestamp': data.timestamp.isoformat(),
                        'severity': 'high' if abs(float(data.change_pct)) > 10 else 'medium'
                    })
            
            # 检测成交量异常
            # TODO: 实现成交量异常检测逻辑
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def _scan_opportunities(self) -> List[Dict[str, Any]]:
        """扫描交易机会"""
        opportunities = []
        
        try:
            # 获取最近价格数据
            symbols = MarketDataModel.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).values_list('symbol', flat=True).distinct()[:20]  # 限制扫描数量
            
            for symbol in symbols:
                # 简单的机会识别逻辑（实际应该更复杂）
                recent_data = MarketDataModel.objects.filter(
                    symbol=symbol,
                    timestamp__gte=timezone.now() - timedelta(days=5)
                ).order_by('-timestamp')[:5]
                
                if len(recent_data) >= 5:
                    # 检测趋势突破
                    if self._check_breakout(recent_data):
                        opportunities.append({
                            'type': 'breakout',
                            'symbol': symbol,
                            'description': f'{symbol} 价格突破关键阻力位',
                            'confidence': 0.7
                        })
            
            logger.info(f"Found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to scan opportunities: {e}")
            return []
    
    def _check_breakout(self, data_list) -> bool:
        """检查是否突破（简化版）"""
        if len(data_list) < 5:
            return False
        
        # 简单逻辑：最新价格高于过去4天最高价
        latest = data_list[0]
        past_high = max([float(d.high) for d in data_list[1:]])
        
        return float(latest.close) > past_high * 1.02  # 超过2%视为突破
    
    def _detect_risk_signals(self) -> List[Dict[str, Any]]:
        """检测风险信号"""
        risk_signals = []
        
        try:
            # 检测高VIX
            latest_sentiment = MarketSentimentModel.objects.order_by('-timestamp').first()
            if latest_sentiment and latest_sentiment.vix:
                vix_value = float(latest_sentiment.vix)
                if vix_value > 30:
                    risk_signals.append({
                        'type': 'high_vix',
                        'value': vix_value,
                        'threshold': 30,
                        'severity': 'high' if vix_value > 40 else 'medium',
                        'description': f'VIX指数达到{vix_value}，市场波动性较高'
                    })
            
            # 检测高等级新闻事件
            high_level_news = NewsEventModel.objects.filter(
                published_at__gte=timezone.now() - timedelta(hours=24),
                event_level__gte=7  # 等级7以上的重大事件
            )
            
            for news in high_level_news:
                risk_signals.append({
                    'type': 'major_event',
                    'event_level': news.event_level,
                    'title': news.title,
                    'timestamp': news.published_at.isoformat(),
                    'severity': 'critical' if news.event_level >= 9 else 'high'
                })
            
            logger.info(f"Detected {len(risk_signals)} risk signals")
            return risk_signals
            
        except Exception as e:
            logger.error(f"Failed to detect risk signals: {e}")
            return []
    
    def analyze_news_sentiment(self, news_id: int) -> Dict[str, Any]:
        """
        分析新闻情绪和影响
        
        Args:
            news_id: 新闻ID
            
        Returns:
            Dict: 分析结果
        """
        try:
            news = NewsEventModel.objects.get(id=news_id)
            
            prompt = f"""
            请分析以下新闻的市场影响：
            
            标题：{news.title}
            内容：{news.content[:500]}...
            
            请评估：
            1. 事件等级（1-10分，10分为黑天鹅事件）
            2. 情绪分数（-100到100，负数为负面，正数为正面）
            3. 可能影响的股票类型或行业
            4. 简短的影响分析（100字以内）
            
            以JSON格式返回：
            {{
                "event_level": 数字,
                "sentiment_score": 数字,
                "affected_sectors": ["行业1", "行业2"],
                "impact_analysis": "分析文本"
            }}
            """
            
            messages = [
                {"role": "system", "content": "你是一位专业的财经新闻分析师。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.openai_client.fast_completion(
                messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response)
            
            # 更新新闻记录
            news.event_level = analysis.get('event_level')
            news.sentiment_score = analysis.get('sentiment_score')
            news.impact_analysis = analysis.get('impact_analysis')
            news.save()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze news sentiment: {e}")
            return {}
    
    def run(self):
        """运行感知智能体"""
        logger.info("Perception agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 执行市场感知
            result = self.perceive_market()
            
            self._update_status('running', 'Perception completed', 'Idle')
            return result
            
        except Exception as e:
            logger.error(f"Perception agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise

