"""
Business Database Connection Module
业务数据库连接管理模块 - 支持同主机地址的多个业务数据库
"""

import os
from typing import Dict, Optional, List
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
import logging

logger = logging.getLogger(__name__)


class BusinessDatabaseManager:
    """业务数据库连接管理器"""

    def __init__(self):
        self._engines: Dict[str, Engine] = {}
        self._sessions: Dict[str, sessionmaker] = {}
        self._initialized = False

    def _get_base_url(self) -> str:
        """获取基础数据库URL（不包含数据库名）"""
        host = os.getenv("BUSINESS_MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost"))
        port = int(os.getenv("BUSINESS_MYSQL_PORT", os.getenv("MYSQL_PORT", "3306")))
        user = os.getenv("BUSINESS_MYSQL_USER", os.getenv("MYSQL_USER", "root"))
        password = os.getenv("BUSINESS_MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "password"))
        return f"mysql+pymysql://{user}:{password}@{host}:{port}"

    def _initialize_databases(self):
        """初始化所有业务数据库连接"""
        if self._initialized:
            return

        # 获取业务数据库列表
        databases_str = os.getenv("BUSINESS_MYSQL_DATABASES", "")
        if not databases_str:
            logger.debug("未配置业务数据库（BUSINESS_MYSQL_DATABASES）")
            self._initialized = True
            return

        # 解析数据库列表（支持逗号分隔）
        database_names = [db.strip() for db in databases_str.split(",") if db.strip()]

        if not database_names:
            logger.debug("业务数据库列表为空")
            self._initialized = True
            return

        base_url = self._get_base_url()
        pool_size = int(os.getenv("MYSQL_POOL_SIZE", "20"))
        pool_recycle = int(os.getenv("MYSQL_POOL_RECYCLE", "3600"))

        # 为每个数据库创建连接
        for db_name in database_names:
            try:
                db_url = f"{base_url}/{db_name}?charset=utf8mb4"
                engine = create_engine(
                    db_url,
                    pool_size=pool_size,
                    pool_recycle=pool_recycle,
                    echo=os.getenv("MYSQL_ECHO", "false").lower() == "true",
                )
                session_maker = sessionmaker(bind=engine)

                self._engines[db_name] = engine
                self._sessions[db_name] = session_maker

                logger.debug(f"成功初始化业务数据库连接: {db_name}")
            except Exception as e:
                logger.error(f"初始化业务数据库 {db_name} 失败: {e}")

        self._initialized = True

    def get_engine(self, database_name: str) -> Optional[Engine]:
        """
        获取指定数据库的引擎

        Args:
            database_name: 数据库名称

        Returns:
            Engine 实例，如果数据库不存在返回 None
        """
        self._initialize_databases()
        return self._engines.get(database_name)

    def get_session(self, database_name: str) -> Optional[Session]:
        """
        获取指定数据库的会话

        Args:
            database_name: 数据库名称

        Returns:
            Session 实例，如果数据库不存在返回 None
        """
        self._initialize_databases()
        session_maker = self._sessions.get(database_name)
        if session_maker:
            return session_maker()
        return None

    def execute_query(self, database_name: str, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        在指定数据库中执行查询

        Args:
            database_name: 数据库名称
            sql: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        engine = self.get_engine(database_name)
        if not engine:
            raise ValueError(f"业务数据库 {database_name} 不存在或未配置")

        try:
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(sql), params)
                else:
                    result = conn.execute(text(sql))

                # 获取列名
                columns = result.keys()
                # 返回字典列表
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"业务数据库查询失败 [{database_name}]: {sql}, 错误: {e}")
            raise

    def list_databases(self) -> List[str]:
        """
        列出所有已配置的业务数据库

        Returns:
            数据库名称列表
        """
        self._initialize_databases()
        return list(self._engines.keys())

    def database_exists(self, database_name: str) -> bool:
        """
        检查数据库是否存在

        Args:
            database_name: 数据库名称

        Returns:
            bool: 数据库是否存在
        """
        self._initialize_databases()
        return database_name in self._engines

    def health_check(self, database_name: Optional[str] = None) -> bool:
        """
        健康检查

        Args:
            database_name: 数据库名称，如果为 None 则检查所有数据库

        Returns:
            bool: 连接是否正常
        """
        self._initialize_databases()

        if database_name:
            # 检查指定数据库
            engine = self._engines.get(database_name)
            if not engine:
                return False
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True
            except Exception as e:
                logger.error(f"业务数据库 {database_name} 健康检查失败: {e}")
                return False
        else:
            # 检查所有数据库
            if not self._engines:
                return True  # 如果没有配置数据库，认为健康
            all_healthy = True
            for db_name in self._engines.keys():
                if not self.health_check(db_name):
                    all_healthy = False
            return all_healthy

    def close_all(self):
        """关闭所有数据库连接"""
        for db_name, engine in self._engines.items():
            try:
                engine.dispose()
                logger.debug(f"已关闭业务数据库连接: {db_name}")
            except Exception as e:
                logger.error(f"关闭业务数据库 {db_name} 连接失败: {e}")
        self._engines.clear()
        self._sessions.clear()
        self._initialized = False


# 全局业务数据库管理器实例
business_db_manager = BusinessDatabaseManager()


def get_business_db_manager() -> BusinessDatabaseManager:
    """获取业务数据库管理器实例"""
    return business_db_manager


def get_business_engine(database_name: str) -> Optional[Engine]:
    """
    获取指定业务数据库的引擎

    Args:
        database_name: 数据库名称

    Returns:
        Engine 实例
    """
    return business_db_manager.get_engine(database_name)


def get_business_session(database_name: str) -> Optional[Session]:
    """
    获取指定业务数据库的会话

    Args:
        database_name: 数据库名称

    Returns:
        Session 实例
    """
    return business_db_manager.get_session(database_name)


def list_business_databases() -> List[str]:
    """列出所有已配置的业务数据库"""
    return business_db_manager.list_databases()


def execute_business_query(database_name: str, sql: str, params: Optional[Dict] = None) -> List[Dict]:
    """
    在指定业务数据库中执行查询

    Args:
        database_name: 数据库名称
        sql: SQL查询语句
        params: 查询参数

    Returns:
        查询结果列表
    """
    return business_db_manager.execute_query(database_name, sql, params)

