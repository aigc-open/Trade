"""OpenAI 客户端封装"""
import os
from typing import List, Dict, Optional, Any
from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API 客户端"""
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        config = settings.AI_TRADER_CONFIG
        self.api_key = config.get('OPENAI_API_KEY')
        self.base_url = config.get('OPENAI_BASE_URL')
        self.model = config.get('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.fast_model = config.get('OPENAI_FAST_MODEL', 'gpt-3.5-turbo')
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url != 'https://api.openai.com/v1' else None
        )
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """
        调用 ChatCompletion API
        
        Args:
            messages: 消息列表
            model: 模型名称，默认使用配置的模型
            temperature: 温度参数
            max_tokens: 最大tokens数
            response_format: 响应格式（如 {"type": "json_object"}）
            **kwargs: 其他参数
            
        Returns:
            str: 模型响应文本
        """
        try:
            model = model or self.model
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def fast_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        使用快速模型进行推理
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            str: 模型响应文本
        """
        return self.chat_completion(messages, model=self.fast_model, **kwargs)
    
    def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型名称
            
        Returns:
            List[float]: 嵌入向量
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def batch_generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """
        批量生成嵌入向量
        
        Args:
            texts: 文本列表
            model: 嵌入模型名称
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise


# 全局单例
_openai_client = None


def get_openai_client() -> OpenAIClient:
    """获取 OpenAI 客户端单例"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client

