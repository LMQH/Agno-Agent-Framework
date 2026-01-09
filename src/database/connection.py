"""
MySQL Database Connection Module
使用 agno.db.mysql.MySQLDb 进行数据库连接管理
"""

import os
from typing import Optional, Any
from sqlalchemy import create_engine, text
from agno.db.mysql import MySQLDb
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """MySQL数据库连接管理类"""

    def __init__(self, session_table: str = "agno_tags_sessions"):
        """
        初始化数据库连接
        
        Args:
            session_table: 会话表名
        """
        self._db: Optional[MySQLDb] = None
        self._session: Optional[Any] = None
        self._session_table = session_table

    @property
    def db(self) -> MySQLDb:
        """获取数据库实例"""
        if self._db is None:
            self._db = self._create_database_connection()
        return self._db

    @property
    def session(self) -> Any:
        """获取数据库会话"""
        if self._session is None:
            self._session = self.db.Session()
        return self._session

    def _create_database_connection(self) -> MySQLDb:
        """
        创建MySQL数据库连接（Agno专用数据库）
        如果数据库不存在，会自动创建数据库（但不创建表）

        Returns:
            MySQLDb: 配置好的数据库连接实例
        """
        try:
            # 从环境变量获取Agno专用数据库配置
            host = os.getenv("AGNO_MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost"))
            port = int(os.getenv("AGNO_MYSQL_PORT", os.getenv("MYSQL_PORT", "3306")))
            user = os.getenv("AGNO_MYSQL_USER", os.getenv("MYSQL_USER", "root"))
            password = os.getenv("AGNO_MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "password"))
            db_schema = os.getenv("AGNO_MYSQL_DB_SCHEMA", os.getenv("AGNO_MYSQL_DATABASE", os.getenv("MYSQL_DATABASE", "agno_backend")))

            # 先连接到MySQL服务器（不指定数据库）以创建数据库
            # 构建不带数据库名的连接URL
            server_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
            server_engine = create_engine(server_url)
            
            # 检查数据库是否存在，如果不存在则创建
            with server_engine.connect() as conn:
                # MySQL创建数据库的SQL语句（如果不存在）
                create_db_sql = text(f"CREATE DATABASE IF NOT EXISTS `{db_schema}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.execute(create_db_sql)
                conn.commit()
                logger.debug(f"数据库 '{db_schema}' 已确保存在（如不存在则已创建）")
            
            server_engine.dispose()

            # 构建数据库URL（用于MySQLDb）
            db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"

            # 从环境变量获取表名配置（带默认值）
            memory_table = os.getenv("AGNO_MEMORY_TABLE", "agno_tags_memories")
            traces_table = os.getenv("AGNO_TRACES_TABLE", "agno_tags_traces")
            spans_table = os.getenv("AGNO_SPANS_TABLE", "agno_tags_spans")
            metrics_table = os.getenv("AGNO_METRICS_TABLE", "agno_tags_metrics")
            eval_table = os.getenv("AGNO_EVAL_TABLE", "agno_tags_evaluations")
            knowledge_table = os.getenv("AGNO_KNOWLEDGE_TABLE", "agno_tags_knowledge")
            culture_table = os.getenv("AGNO_CULTURE_TABLE", "agno_tags_culture")

            # 创建MySQL数据库连接（推荐方式）
            # 注意：MySQLDb 在首次使用时可能会自动创建表，但我们先不执行任何操作
            db = MySQLDb(
                db_url=db_url,  # 数据库连接（不包含数据库名）
                db_schema=db_schema,  # 数据库名
                # 自定义表名（从环境变量读取，带默认值）
                session_table=self._session_table,  # 会话表名（从配置或参数获取）
                memory_table=memory_table,  # 记忆表名
                traces_table=traces_table,    # 追踪表名
                spans_table=spans_table,      # Span表名
                metrics_table=metrics_table,  # 指标表名
                eval_table=eval_table, # 评估表名
                knowledge_table=knowledge_table,  # 知识表名
                culture_table=culture_table,   # 文化知识表名
            )

            logger.debug(f"成功连接到MySQL数据库: {db_schema}")
            return db

        except Exception as e:
            logger.error(f"MySQL数据库连接失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self._session:
            self._session.close()
            self._session = None
        # MySQLDb 的连接由 SQLAlchemy 管理，通常不需要显式关闭


# 全局数据库连接实例（按类型分别创建）
_workflow_db_connection: Optional[DatabaseConnection] = None
_team_db_connection: Optional[DatabaseConnection] = None
_agent_db_connection: Optional[DatabaseConnection] = None


def _get_session_table_name(table_type: str) -> str:
    """
    从环境变量获取会话表名
    
    Args:
        table_type: 表类型 ('workflow', 'team', 'agent')
    
    Returns:
        表名字符串
    """
    if table_type == 'workflow':
        return os.getenv('WORKFLOW_SESSION_TABLE', 'workflow_sessions')
    elif table_type == 'team':
        return os.getenv('TEAM_SESSION_TABLE', 'team_sessions')
    elif table_type == 'agent':
        return os.getenv('AGENT_SESSION_TABLE', 'agent_sessions')
    else:
        # 默认使用旧的表名（向后兼容）
        return os.getenv('SESSION_TABLE', 'agno_tags_sessions')


def get_workflow_database() -> MySQLDb:
    """
    获取Workflow数据库连接实例

    Returns:
        MySQLDb: Workflow数据库连接实例
    """
    global _workflow_db_connection
    if _workflow_db_connection is None:
        session_table = _get_session_table_name('workflow')
        _workflow_db_connection = DatabaseConnection(session_table=session_table)
    return _workflow_db_connection.db


def get_team_database() -> MySQLDb:
    """
    获取Team数据库连接实例

    Returns:
        MySQLDb: Team数据库连接实例
    """
    global _team_db_connection
    if _team_db_connection is None:
        session_table = _get_session_table_name('team')
        _team_db_connection = DatabaseConnection(session_table=session_table)
    return _team_db_connection.db


def get_agent_database() -> MySQLDb:
    """
    获取Agent数据库连接实例

    Returns:
        MySQLDb: Agent数据库连接实例
    """
    global _agent_db_connection
    if _agent_db_connection is None:
        session_table = _get_session_table_name('agent')
        _agent_db_connection = DatabaseConnection(session_table=session_table)
    return _agent_db_connection.db


def get_database() -> MySQLDb:
    """
    获取数据库连接实例（向后兼容，默认使用agent数据库）

    Returns:
        MySQLDb: 数据库连接实例
    """
    # 为了向后兼容，默认返回agent数据库
    return get_agent_database()


def get_db_session() -> Any:
    """
    获取数据库会话（向后兼容，默认使用agent数据库会话）

    Returns:
        Any: 数据库会话实例
    """
    global _agent_db_connection
    if _agent_db_connection is None:
        session_table = _get_session_table_name('agent')
        _agent_db_connection = DatabaseConnection(session_table=session_table)
    return _agent_db_connection.session


def check_database_connection() -> bool:
    """
    检查数据库连接状态（已禁用健康检查）

    Returns:
        bool: 始终返回 True
    """
    return True


def close_database_connection():
    """关闭所有数据库连接"""
    global _workflow_db_connection, _team_db_connection, _agent_db_connection
    
    if _workflow_db_connection is not None:
        _workflow_db_connection.close()
        _workflow_db_connection = None
    
    if _team_db_connection is not None:
        _team_db_connection.close()
        _team_db_connection = None
    
    if _agent_db_connection is not None:
        _agent_db_connection.close()
        _agent_db_connection = None
