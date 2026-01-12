"""
Knowledge Configuration Module
知识库配置模块 - 配置 Milvus 向量数据库和 MySQL 内容数据库
"""

import os
import logging
from typing import Optional
from agno.db.mysql import MySQLDb
from agno.knowledge import Knowledge
from agno.vectordb.milvus import Milvus
from agno.knowledge.embedder.openai import OpenAIEmbedder
from src.vector.connection import get_milvus_client

logger = logging.getLogger(__name__)


def get_knowledge_contents_db() -> MySQLDb:
    """
    获取知识库内容数据库实例（MySQL）
    
    用于存储知识库的元数据和内容信息
    
    Returns:
        MySQLDb: 知识库内容数据库实例
    """
    # 从环境变量获取Agno专用数据库配置
    host = os.getenv("AGNO_MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost"))
    port = int(os.getenv("AGNO_MYSQL_PORT", os.getenv("MYSQL_PORT", "3306")))
    user = os.getenv("AGNO_MYSQL_USER", os.getenv("MYSQL_USER", "root"))
    password = os.getenv("AGNO_MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "password"))
    db_schema = os.getenv("AGNO_MYSQL_DB_SCHEMA", os.getenv("AGNO_MYSQL_DATABASE", os.getenv("MYSQL_DATABASE", "agno_backend")))
    
    # 构建数据库URL（不包含数据库名）
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    
    # 从环境变量获取知识表名
    knowledge_table = os.getenv("AGNO_KNOWLEDGE_TABLE", "agno_knowledge")
    
    # 创建MySQL数据库连接（专门用于知识库内容存储）
    contents_db = MySQLDb(
        db_url=db_url,
        db_schema=db_schema,
        knowledge_table=knowledge_table,  # 指定知识表名
    )
    
    logger.debug(f"创建知识库内容数据库连接: {db_schema}, 表: {knowledge_table}")
    return contents_db


def get_knowledge_embedder() -> OpenAIEmbedder:
    """
    获取知识库嵌入模型实例
    
    用于将文本转换为向量
    
    Returns:
        OpenAIEmbedder: 嵌入模型实例
    """
    # 从环境变量获取嵌入模型配置
    api_key = os.getenv("EMBEDDING_API_KEY", "")
    base_url = os.getenv("EMBEDDING_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_id = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v2")
    
    # 根据模型设置维度
    # text-embedding-v2: 1536
    # text-embedding-3-small: 1536
    # text-embedding-3-large: 3072
    dimensions_map = {
        "text-embedding-v2": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    }
    dimensions = dimensions_map.get(model_id, 1536)  # 默认1536
    
    # 创建 OpenAI 兼容的嵌入模型实例（用于DashScope）
    embedder = OpenAIEmbedder(
        id=model_id,
        base_url=base_url,
        api_key=api_key,
        dimensions=dimensions,
    )
    
    logger.debug(f"创建嵌入模型: {model_id}, 维度: {dimensions}, API地址: {base_url}")
    return embedder


def get_knowledge_vector_db() -> Milvus:
    """
    获取知识库向量数据库实例（Milvus）
    
    用于存储知识库的向量数据
    
    Returns:
        Milvus: Milvus 向量数据库对象
    """
    # 确保 Milvus 连接已建立
    get_milvus_client()
    
    # 从环境变量获取 Milvus 配置
    host = os.getenv("MILVUS_HOST", "localhost")
    port = int(os.getenv("MILVUS_PORT", "19530"))
    collection_name = os.getenv("MILVUS_DEFAULT_COLLECTION", "agno_knowledge_default")
    
    # 构建 Milvus URI (格式: http://host:port)
    milvus_uri = f"http://{host}:{port}"
    
    # 获取嵌入模型
    embedder = get_knowledge_embedder()
    
    # 创建 Milvus 向量数据库对象
    # 注意：必须使用 Milvus 对象，不能使用字符串 URI
    vector_db = Milvus(
        collection=collection_name,  # 集合名称
        uri=milvus_uri,  # Milvus URI (http://host:port 或本地文件路径)
        embedder=embedder,  # 嵌入模型
    )
    
    logger.debug(f"创建知识库向量数据库对象: {milvus_uri}, 集合: {collection_name}")
    return vector_db


def create_knowledge() -> Knowledge:
    """
    创建知识库实例
    
    配置了 Milvus 向量数据库和 MySQL 内容数据库
    
    Returns:
        Knowledge: 知识库实例
    """
    # 获取向量数据库对象（必须是 Milvus 对象，不能是字符串）
    vector_db = get_knowledge_vector_db()
    
    # 获取内容数据库
    contents_db = get_knowledge_contents_db()
    
    # 创建知识库实例
    # 注意：vector_db 必须是 Milvus 对象（有 exists() 方法），不能是字符串 URI
    # embedder 在 Milvus 对象中配置
    knowledge = Knowledge(
        vector_db=vector_db,  # Milvus 向量数据库对象
        contents_db=contents_db,  # 必须提供 MySQL 数据库
    )
    
    logger.info("知识库实例创建成功（Milvus向量数据库 + MySQL内容数据库）")
    return knowledge

