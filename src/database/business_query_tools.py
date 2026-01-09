"""
Business Database Query Tools Module
业务数据库查询工具，提供业务数据库的查询操作方法
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
import logging
from .business_db import get_business_db_manager, list_business_databases

logger = logging.getLogger(__name__)


class BusinessDatabaseQueryTools:
    """业务数据库查询工具类"""

    def __init__(self, default_database: Optional[str] = None):
        """
        初始化业务数据库查询工具

        Args:
            default_database: 默认使用的业务数据库名称，如果为None则使用第一个配置的数据库
        """
        self.manager = get_business_db_manager()
        self._default_database = default_database

    def _get_database_name(self, database_name: Optional[str] = None) -> str:
        """
        获取要使用的数据库名称

        Args:
            database_name: 指定的数据库名称

        Returns:
            数据库名称
        """
        if database_name:
            return database_name

        if self._default_database:
            return self._default_database

        # 使用第一个配置的业务数据库
        databases = list_business_databases()
        if not databases:
            raise ValueError("未配置业务数据库（BUSINESS_MYSQL_DATABASES）")
        return databases[0]

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None,
                     database_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数
            database_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            查询结果列表

        Raises:
            SQLAlchemyError: 查询执行失败
        """
        db_name = self._get_database_name(database_name)
        return self.manager.execute_query(db_name, query, params)

    def get_table_info(self, table_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取表信息

        Args:
            table_name: 表名
            database_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            表信息字典
        """
        db_name = self._get_database_name(database_name)
        engine = self.manager.get_engine(db_name)
        if not engine:
            raise ValueError(f"业务数据库 {db_name} 不存在或未配置")

        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)

            return {
                "name": table.name,
                "database": db_name,
                "columns": [
                    {
                        "name": column.name,
                        "type": str(column.type),
                        "nullable": column.nullable,
                        "primary_key": column.primary_key,
                    }
                    for column in table.columns
                ],
                "primary_keys": [col.name for col in table.primary_key.columns],
            }

        except SQLAlchemyError as e:
            logger.error(f"获取表信息失败: {table_name}, 数据库: {db_name}, 错误: {e}")
            raise

    def list_tables(self, database_name: Optional[str] = None) -> List[str]:
        """
        列出数据库中的所有表

        Args:
            database_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            表名列表
        """
        db_name = self._get_database_name(database_name)
        engine = self.manager.get_engine(db_name)
        if not engine:
            raise ValueError(f"业务数据库 {db_name} 不存在或未配置")

        try:
            metadata = MetaData()
            metadata.reflect(bind=engine)
            return list(metadata.tables.keys())

        except SQLAlchemyError as e:
            logger.error(f"列出表失败，数据库: {db_name}, 错误: {e}")
            raise

    def get_table_count(self, table_name: str, database_name: Optional[str] = None) -> int:
        """
        获取表的记录数

        Args:
            table_name: 表名
            database_name: 数据库名称，如果为None则使用默认数据库

        Returns:
            记录数
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query, database_name=database_name)
        return result[0]["count"] if result else 0

    def list_databases(self) -> List[str]:
        """
        列出所有已配置的业务数据库

        Returns:
            数据库名称列表
        """
        return list_business_databases()


# 全局业务数据库查询工具实例（使用第一个配置的数据库作为默认）
business_query_tools = BusinessDatabaseQueryTools()


def get_business_query_tools(default_database: Optional[str] = None) -> BusinessDatabaseQueryTools:
    """
    获取业务数据库查询工具实例

    Args:
        default_database: 默认使用的业务数据库名称

    Returns:
        BusinessDatabaseQueryTools 实例
    """
    if default_database:
        return BusinessDatabaseQueryTools(default_database)
    return business_query_tools

