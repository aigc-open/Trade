"""
记忆层：长期记忆存储与检索
Memory Layer: Long-term Memory Storage and Retrieval
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db import transaction

from apps.memory.models import AgentMemoryModel, KnowledgeNodeModel, KnowledgeEdgeModel
from apps.agents.models import AgentStatusModel, DecisionRecordModel
from apps.trades.models import TradeModel
from utils.ai.openai_client import get_openai_client
from utils.ai.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


class MemoryAgent:
    """记忆智能体"""
    
    def __init__(self):
        self.agent_type = 'memory'
        self.openai_client = get_openai_client()
        self.chroma_client = get_chroma_client()
        self._update_status('running', 'Memory agent initialized')
        
        # ChromaDB 集合名称
        self.SHORT_TERM_COLLECTION = 'short_term_memory'
        self.LONG_TERM_COLLECTION = 'long_term_memory'
    
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
    
    def store_trade_memory(self, trade: TradeModel) -> Optional[AgentMemoryModel]:
        """
        存储交易记忆
        
        Args:
            trade: 交易记录
            
        Returns:
            AgentMemoryModel: 记忆对象
        """
        try:
            # 构建记忆内容
            content = f"""
            交易: {trade.symbol} {trade.action}
            价格: {trade.filled_price}
            数量: {trade.filled_quantity}
            盈亏: {trade.pnl} ({trade.pnl_pct}%)
            原因: {trade.reason}
            """
            
            # 生成摘要
            summary = f"{trade.symbol} {trade.action} {trade.pnl_pct}%"
            
            # 评估重要性
            importance = self._calculate_importance(trade)
            
            # 确定记忆类型
            memory_type = self._determine_memory_type(trade)
            
            # 生成向量嵌入
            embedding = self.openai_client.generate_embedding(content)
            
            # 保存到数据库
            memory = AgentMemoryModel.objects.create(
                memory_type=memory_type,
                content=content.strip(),
                summary=summary,
                importance_score=importance,
                
                # 5W1H
                when=trade.order_time,
                where=trade.symbol,
                what=f"{trade.action} {trade.filled_quantity}股",
                who='AI',
                why=trade.reason,
                how=f"通过{trade.strategy.name if trade.strategy else '未知策略'}",
                
                # 关联
                related_symbols=[trade.symbol],
                related_trades=[str(trade.trade_id)],
                
                source='trade',
                source_id=str(trade.id),
            )
            
            # 保存到向量数据库
            vector_id = str(uuid.uuid4())
            collection_name = (self.SHORT_TERM_COLLECTION if memory_type == 'short_term' 
                             else self.LONG_TERM_COLLECTION)
            
            self.chroma_client.add_documents(
                collection_name=collection_name,
                documents=[content.strip()],
                metadatas=[{
                    'memory_id': str(memory.id),
                    'symbol': trade.symbol,
                    'importance': float(importance),
                    'timestamp': trade.order_time.isoformat(),
                }],
                ids=[vector_id],
                embeddings=[embedding]
            )
            
            memory.vector_id = vector_id
            memory.save()
            
            logger.info(f"Stored trade memory: {memory.id}")
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to store trade memory: {e}")
            return None
    
    def _calculate_importance(self, trade: TradeModel) -> float:
        """计算记忆重要性（0-10分）"""
        importance = 5.0  # 基础分
        
        # 根据盈亏比例调整
        if trade.pnl_pct:
            pnl_pct = abs(float(trade.pnl_pct))
            if pnl_pct > 10:
                importance += 3
            elif pnl_pct > 5:
                importance += 2
            elif pnl_pct > 2:
                importance += 1
        
        # 根据决策质量调整
        if trade.decision and trade.decision.confidence_score:
            confidence = float(trade.decision.confidence_score)
            if confidence > 80:
                importance += 1
        
        # 限制在0-10范围内
        return min(max(importance, 0), 10)
    
    def _determine_memory_type(self, trade: TradeModel) -> str:
        """确定记忆类型"""
        importance = self._calculate_importance(trade)
        
        if importance >= 8:
            return 'long_term'  # 高重要性进入长期记忆
        elif importance >= 5:
            return 'short_term'  # 中等重要性进入短期记忆
        else:
            return 'working'  # 低重要性进入工作记忆
    
    def search_similar_memories(
        self, 
        query: str, 
        n_results: int = 5,
        memory_type: Optional[str] = None
    ) -> List[AgentMemoryModel]:
        """
        语义搜索相似记忆
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            memory_type: 记忆类型过滤
            
        Returns:
            List[AgentMemoryModel]: 相似记忆列表
        """
        try:
            # 生成查询向量
            query_embedding = self.openai_client.generate_embedding(query)
            
            # 确定搜索的集合
            collections = []
            if memory_type == 'short_term':
                collections = [self.SHORT_TERM_COLLECTION]
            elif memory_type == 'long_term':
                collections = [self.LONG_TERM_COLLECTION]
            else:
                collections = [self.SHORT_TERM_COLLECTION, self.LONG_TERM_COLLECTION]
            
            all_results = []
            
            # 在各个集合中搜索
            for collection_name in collections:
                try:
                    results = self.chroma_client.query(
                        collection_name=collection_name,
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
                    
                    if results and results.get('ids'):
                        for i, memory_id in enumerate(results['metadatas'][0]):
                            memory_id_str = memory_id.get('memory_id')
                            if memory_id_str:
                                all_results.append({
                                    'memory_id': memory_id_str,
                                    'distance': results['distances'][0][i] if 'distances' in results else 0
                                })
                except Exception as e:
                    logger.warning(f"Search in {collection_name} failed: {e}")
                    continue
            
            # 按相似度排序
            all_results.sort(key=lambda x: x['distance'])
            
            # 获取记忆对象
            memory_ids = [r['memory_id'] for r in all_results[:n_results]]
            memories = AgentMemoryModel.objects.filter(id__in=memory_ids)
            
            # 按原始顺序返回
            memory_dict = {str(m.id): m for m in memories}
            ordered_memories = [memory_dict[mid] for mid in memory_ids if mid in memory_dict]
            
            logger.info(f"Found {len(ordered_memories)} similar memories for query: {query[:50]}...")
            
            return ordered_memories
            
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []
    
    def consolidate_memories(self):
        """记忆整理：将重要的短期记忆转为长期记忆"""
        try:
            # 获取高重要性的短期记忆
            important_memories = AgentMemoryModel.objects.filter(
                memory_type='short_term',
                importance_score__gte=8,
                is_forgotten=False
            )
            
            count = 0
            for memory in important_memories:
                memory.memory_type = 'long_term'
                memory.save()
                
                # 移动到长期记忆集合
                if memory.vector_id:
                    try:
                        # 获取原始数据
                        results = self.chroma_client.get_by_ids(
                            self.SHORT_TERM_COLLECTION,
                            [memory.vector_id]
                        )
                        
                        if results and results.get('documents'):
                            # 添加到长期记忆
                            self.chroma_client.add_documents(
                                collection_name=self.LONG_TERM_COLLECTION,
                                documents=results['documents'],
                                metadatas=results.get('metadatas', []),
                                ids=[memory.vector_id],
                                embeddings=results.get('embeddings')
                            )
                            
                            # 从短期记忆删除
                            self.chroma_client.delete_documents(
                                collection_name=self.SHORT_TERM_COLLECTION,
                                ids=[memory.vector_id]
                            )
                    except Exception as e:
                        logger.warning(f"Failed to move memory {memory.id} to long-term: {e}")
                
                count += 1
            
            logger.info(f"Consolidated {count} memories to long-term storage")
            return count
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return 0
    
    def forget_old_memories(self, days: int = 90):
        """遗忘过旧的低价值记忆"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            
            old_memories = AgentMemoryModel.objects.filter(
                memory_type__in=['working', 'short_term'],
                importance_score__lt=5,
                created_at__lt=cutoff_date,
                is_forgotten=False
            )
            
            count = 0
            for memory in old_memories:
                memory.is_forgotten = True
                memory.forgotten_at = timezone.now()
                memory.save()
                
                # 从向量数据库删除
                if memory.vector_id:
                    try:
                        self.chroma_client.delete_documents(
                            collection_name=self.SHORT_TERM_COLLECTION,
                            ids=[memory.vector_id]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to delete vector for memory {memory.id}: {e}")
                
                count += 1
            
            logger.info(f"Forgot {count} old memories")
            return count
            
        except Exception as e:
            logger.error(f"Memory forgetting failed: {e}")
            return 0
    
    def run(self):
        """运行记忆智能体"""
        logger.info("Memory agent started")
        self._update_status('running', 'Agent started')
        
        try:
            # 1. 存储最近的交易记忆
            recent_trades = TradeModel.objects.filter(
                status='filled',
                created_at__gte=timezone.now() - timedelta(days=1)
            ).exclude(
                trade_id__in=AgentMemoryModel.objects.filter(
                    source='trade'
                ).values_list('source_id', flat=True)
            )[:10]
            
            stored_count = 0
            for trade in recent_trades:
                memory = self.store_trade_memory(trade)
                if memory:
                    stored_count += 1
            
            logger.info(f"Stored {stored_count} new trade memories")
            
            # 2. 整理记忆
            consolidated = self.consolidate_memories()
            
            # 3. 遗忘旧记忆
            forgotten = self.forget_old_memories()
            
            self._update_status(
                'running', 
                f'Processed memories: {stored_count} stored, {consolidated} consolidated, {forgotten} forgotten',
                'Idle'
            )
            
            return {
                'stored': stored_count,
                'consolidated': consolidated,
                'forgotten': forgotten
            }
            
        except Exception as e:
            logger.error(f"Memory agent error: {e}")
            self._update_status('error', f'Error: {e}')
            raise

