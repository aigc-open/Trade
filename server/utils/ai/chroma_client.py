"""ChromaDB 向量数据库客户端"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ChromaClient:
    """ChromaDB 客户端封装"""
    
    def __init__(self):
        """初始化 ChromaDB 客户端"""
        config = settings.AI_TRADER_CONFIG
        persist_dir = config.get('CHROMA_PERSIST_DIR')
        
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir
        ))
        
        logger.info(f"ChromaDB initialized at {persist_dir}")
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict] = None
    ):
        """
        获取或创建集合
        
        Args:
            name: 集合名称
            metadata: 元数据
            
        Returns:
            Collection: ChromaDB 集合对象
        """
        try:
            return self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Failed to get/create collection {name}: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        添加文档到集合
        
        Args:
            collection_name: 集合名称
            documents: 文档列表
            metadatas: 元数据列表
            ids: ID列表
            embeddings: 嵌入向量列表
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # 生成ID（如果没有提供）
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            add_params = {
                "documents": documents,
                "ids": ids
            }
            
            if metadatas:
                add_params["metadatas"] = metadatas
            
            if embeddings:
                add_params["embeddings"] = embeddings
            
            collection.add(**add_params)
            
            logger.info(f"Added {len(documents)} documents to collection {collection_name}")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            raise
    
    def query(
        self,
        collection_name: str,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 10,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        查询文档
        
        Args:
            collection_name: 集合名称
            query_texts: 查询文本列表
            query_embeddings: 查询嵌入向量列表
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档过滤条件
            
        Returns:
            Dict: 查询结果
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            query_params = {
                "n_results": n_results
            }
            
            if query_texts:
                query_params["query_texts"] = query_texts
            elif query_embeddings:
                query_params["query_embeddings"] = query_embeddings
            else:
                raise ValueError("Must provide either query_texts or query_embeddings")
            
            if where:
                query_params["where"] = where
            
            if where_document:
                query_params["where_document"] = where_document
            
            results = collection.query(**query_params)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query collection {collection_name}: {e}")
            raise
    
    def get_by_ids(
        self,
        collection_name: str,
        ids: List[str]
    ) -> Dict:
        """
        根据ID获取文档
        
        Args:
            collection_name: 集合名称
            ids: ID列表
            
        Returns:
            Dict: 文档数据
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.get(ids=ids)
            return results
            
        except Exception as e:
            logger.error(f"Failed to get documents from {collection_name}: {e}")
            raise
    
    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        更新文档
        
        Args:
            collection_name: 集合名称
            ids: ID列表
            documents: 文档列表
            metadatas: 元数据列表
            embeddings: 嵌入向量列表
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            update_params = {"ids": ids}
            
            if documents:
                update_params["documents"] = documents
            if metadatas:
                update_params["metadatas"] = metadatas
            if embeddings:
                update_params["embeddings"] = embeddings
            
            collection.update(**update_params)
            
            logger.info(f"Updated {len(ids)} documents in collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to update documents in {collection_name}: {e}")
            raise
    
    def delete_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict] = None
    ):
        """
        删除文档
        
        Args:
            collection_name: 集合名称
            ids: ID列表
            where: 元数据过滤条件
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            delete_params = {}
            if ids:
                delete_params["ids"] = ids
            if where:
                delete_params["where"] = where
            
            collection.delete(**delete_params)
            
            logger.info(f"Deleted documents from collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete documents from {collection_name}: {e}")
            raise
    
    def count(self, collection_name: str) -> int:
        """
        获取集合中的文档数量
        
        Args:
            collection_name: 集合名称
            
        Returns:
            int: 文档数量
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
            
        except Exception as e:
            logger.error(f"Failed to count documents in {collection_name}: {e}")
            raise
    
    def persist(self):
        """持久化数据"""
        try:
            self.client.persist()
            logger.info("ChromaDB data persisted")
        except Exception as e:
            logger.error(f"Failed to persist ChromaDB data: {e}")


# 全局单例
_chroma_client = None


def get_chroma_client() -> ChromaClient:
    """获取 ChromaDB 客户端单例"""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaClient()
    return _chroma_client

