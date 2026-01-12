"""
Milvus Vector Database Connection Module
Milvus 向量数据库连接管理模块
"""

import os
from typing import Optional
from pymilvus import connections, Collection, utility, db
import logging

logger = logging.getLogger(__name__)


class MilvusConnection:
    """Milvus 向量数据库连接管理类"""

    def __init__(self):
        self._client = None
        self._connected = False
        self._database = None
        self._should_create_default_collection = False
        self._default_collection_name = "agno_knowledge_default"

    def _create_connection(self):
        """
        创建 Milvus 连接
        如果数据库不存在，会自动创建数据库（但不创建集合）

        Returns:
            bool: 连接是否成功
        """
        try:
            # 从环境变量获取 Milvus 配置
            host = os.getenv("MILVUS_HOST", "localhost")
            port = os.getenv("MILVUS_PORT", "19530")
            database = os.getenv("MILVUS_DATABASE", "default")
            
            # 连接参数
            alias = "default"
            connect_params = {
                "host": host,
                "port": port,
            }
            
            # 如果提供了用户名和密码
            if os.getenv("MILVUS_USER"):
                connect_params["user"] = os.getenv("MILVUS_USER")
            if os.getenv("MILVUS_PASSWORD"):
                connect_params["password"] = os.getenv("MILVUS_PASSWORD")
            
            # 建立连接到 Milvus 服务器
            connections.connect(alias=alias, **connect_params)
            
            # 检查数据库是否存在，如果不存在则创建
            try:
                databases = db.list_database()
                if database not in databases:
                    db.create_database(database)
                    logger.debug(f"创建 Milvus 数据库: {database}")
                else:
                    logger.debug(f"Milvus 数据库 '{database}' 已存在")
            except Exception as db_error:
                # 某些版本的 Milvus 可能不支持多数据库功能，使用 default 数据库
                if "database" in str(db_error).lower() or "not support" in str(db_error).lower():
                    logger.warning(f"Milvus 版本可能不支持多数据库功能，使用 default 数据库: {db_error}")
                    database = "default"
                else:
                    raise
            
            # 切换到目标数据库（如果支持）
            try:
                db.using_database(database)
                logger.debug(f"已切换到 Milvus 数据库: {database}")
            except Exception as switch_error:
                # 某些版本可能不需要显式切换，或者已经在默认数据库
                logger.debug(f"切换数据库时出现警告（可忽略）: {switch_error}")
            
            self._connected = True
            self._database = database
            
            logger.debug(f"成功连接到 Milvus: {host}:{port}, 数据库: {database}")
            
            # 确保默认集合存在（延迟导入避免循环依赖）
            # 注意：这里延迟创建集合，避免在连接阶段触发循环依赖
            # 集合会在首次使用 query_tools 时自动创建
            self._should_create_default_collection = True
            self._default_collection_name = os.getenv("MILVUS_DEFAULT_COLLECTION", "agno_knowledge_default")
            
            return True

        except Exception as e:
            logger.error(f"Milvus 连接失败: {e}")
            self._connected = False
            raise

    @property
    def database(self) -> str:
        """获取当前使用的数据库名称"""
        if self._database is None:
            self._database = os.getenv("MILVUS_DATABASE", "default")
        return self._database

    @property
    def client(self):
        """获取 Milvus 客户端连接（pymilvus 使用全局连接）"""
        if not self._connected:
            self._create_connection()
        return True  # pymilvus 使用全局连接，返回 True 表示已连接

    def health_check(self) -> bool:
        """
        Milvus 健康检查

        Returns:
            bool: 连接是否正常
        """
        try:
            if not self._connected:
                self._create_connection()
            
            # 尝试列出集合来测试连接
            collections = utility.list_collections()
            return True
        except Exception as e:
            logger.error(f"Milvus 健康检查失败: {e}")
            return False

    def close(self):
        """关闭 Milvus 连接"""
        try:
            if self._connected:
                connections.disconnect("default")
                self._connected = False
                logger.debug("Milvus 连接已关闭")
        except Exception as e:
            logger.error(f"关闭 Milvus 连接失败: {e}")


# 全局 Milvus 连接实例
milvus_connection = MilvusConnection()


def get_milvus_client():
    """
    获取 Milvus 客户端连接（确保连接已建立）

    Returns:
        bool: 连接状态（pymilvus 使用全局连接）
    """
    if not milvus_connection._connected:
        milvus_connection._create_connection()
    return milvus_connection.client


def check_milvus_connection() -> bool:
    """
    检查 Milvus 连接状态

    Returns:
        bool: 连接是否正常
    """
    return milvus_connection.health_check()


def close_milvus_connection():
    """关闭 Milvus 连接"""
    milvus_connection.close()

