"""
Model Configuration Module
模型配置模块 - 支持DeepSeek和嵌入模型配置
"""

import os
import logging
from typing import Optional
from agno.models.deepseek import DeepSeek
from agno.knowledge.embedder.openai import OpenAIEmbedder

logger = logging.getLogger(__name__)


class ModelConfig:
    """模型配置类"""

    @staticmethod
    def get_chat_model_config() -> dict:
        """
        获取聊天模型配置

        Returns:
            配置字典
        """
        return {
            "api_key": os.getenv("MODEL_API_KEY", ""),
            "base_url": os.getenv("MODEL_API_BASE_URL", "https://api.modelarts-maas.com/v1"),
            "model_id": os.getenv("MODEL_NAME", "deepseek-v3.2-exp"),
        }

    @staticmethod
    def get_embedding_model_config() -> dict:
        """
        获取嵌入模型配置

        Returns:
            配置字典
        """
        return {
            "api_key": os.getenv("EMBEDDING_API_KEY", ""),
            "base_url": os.getenv("EMBEDDING_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "model_id": os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v2"),
        }


def get_chat_model() -> DeepSeek:
    """
    获取聊天模型实例（DeepSeek私有部署）

    Returns:
        DeepSeek 模型实例
    """
    config = ModelConfig.get_chat_model_config()
    
    api_key = config["api_key"]
    base_url = config["base_url"]
    model_id = config["model_id"]
    
    if not api_key:
        logger.warning("未配置 MODEL_API_KEY，使用默认值")
    
    logger.debug(f"初始化DeepSeek聊天模型: {model_id}, API地址: {base_url}")
    
    # 创建DeepSeek模型实例
    # 如果提供了base_url，使用base_url参数（私有部署）
    if base_url and base_url != "https://api.deepseek.com":
        model = DeepSeek(
            id=model_id,
            api_key=api_key,
            base_url=base_url,
        )
    else:
        # 使用默认DeepSeek API
        model = DeepSeek(
            id=model_id,
            api_key=api_key,
        )
    
    return model


def get_embedding_model() -> OpenAIEmbedder:
    """
    获取嵌入模型实例（阿里云DashScope）

    Returns:
        OpenAIEmbedder 模型实例
    """
    config = ModelConfig.get_embedding_model_config()
    
    api_key = config["api_key"]
    base_url = config["base_url"]
    model_id = config["model_id"]
    
    if not api_key:
        logger.warning("未配置 EMBEDDING_API_KEY，使用默认值")
    
    logger.debug(f"初始化嵌入模型: {model_id}, API地址: {base_url}")
    
    # 创建OpenAI兼容的嵌入模型实例（用于DashScope）
    # OpenAIEmbedder支持base_url参数用于自定义API端点
    model = OpenAIEmbedder(
        id=model_id,
        api_key=api_key,
        base_url=base_url,
    )
    
    return model


class EmbeddingModelConfig:
    """嵌入模型配置类（别名，保持兼容性）"""
    
    @staticmethod
    def get_config() -> dict:
        """获取嵌入模型配置"""
        return ModelConfig.get_embedding_model_config()

