"""
Database Query Tools Module
数据库查询工具，提供常用的数据库操作方法
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy import text, MetaData, Table, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.exc import SQLAlchemyError
import logging
from .connection import get_database, get_db_session

logger = logging.getLogger(__name__)


class DatabaseQueryTools:
    """数据库查询工具类"""

    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        """延迟获取数据库连接"""
        if self._db is None:
            self._db = get_database()
        return self._db

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表

        Raises:
            SQLAlchemyError: 查询执行失败
        """
        try:
            with self.db.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                # 获取列名
                columns = result.keys()
                # 返回字典列表
                return [dict(zip(columns, row)) for row in result.fetchall()]

        except SQLAlchemyError as e:
            logger.error(f"查询执行失败: {query}, 错误: {e}")
            raise

    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        执行更新操作（INSERT、UPDATE、DELETE）

        Args:
            query: SQL语句
            params: 参数

        Returns:
            影响的行数

        Raises:
            SQLAlchemyError: 执行失败
        """
        try:
            with self.db.engine.connect() as conn:
                with conn.begin():
                    if params:
                        result = conn.execute(text(query), params)
                    else:
                        result = conn.execute(text(query))
                    return result.rowcount

        except SQLAlchemyError as e:
            logger.error(f"更新操作失败: {query}, 错误: {e}")
            raise

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息

        Args:
            table_name: 表名

        Returns:
            表信息字典
        """
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.db.engine)

            return {
                "name": table.name,
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
            logger.error(f"获取表信息失败: {table_name}, 错误: {e}")
            raise

    def list_tables(self) -> List[str]:
        """
        列出数据库中的所有表

        Returns:
            表名列表
        """
        try:
            metadata = MetaData()
            metadata.reflect(bind=self.db.engine)
            return list(metadata.tables.keys())

        except SQLAlchemyError as e:
            logger.error(f"列出表失败: {e}")
            raise

    def get_table_count(self, table_name: str) -> int:
        """
        获取表的记录数

        Args:
            table_name: 表名

        Returns:
            记录数
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def search_records(self, table_name: str, conditions: Dict[str, Any],
                      limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        条件查询记录

        Args:
            table_name: 表名
            conditions: 查询条件字典
            limit: 限制返回记录数
            offset: 偏移量

        Returns:
            查询结果
        """
        where_clauses = []
        params = {}

        for key, value in conditions.items():
            where_clauses.append(f"{key} = :{key}")
            params[key] = value

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"SELECT * FROM {table_name} WHERE {where_clause}"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return self.execute_query(query, params)

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        插入记录

        Args:
            table_name: 表名
            data: 要插入的数据

        Returns:
            插入的记录ID（如果有自增主键）
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{key}" for key in data.keys())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # 执行插入
        self.execute_update(query, data)

        # 获取最后插入的ID（适用于自增主键）
        result = self.execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]["id"] if result else 0

    def update_record(self, table_name: str, data: Dict[str, Any],
                     conditions: Dict[str, Any]) -> int:
        """
        更新记录

        Args:
            table_name: 表名
            data: 要更新的数据
            conditions: 更新条件

        Returns:
            影响的行数
        """
        set_clauses = []
        where_clauses = []
        params = {}

        # 构建SET子句
        for key, value in data.items():
            set_clauses.append(f"{key} = :set_{key}")
            params[f"set_{key}"] = value

        # 构建WHERE子句
        for key, value in conditions.items():
            where_clauses.append(f"{key} = :where_{key}")
            params[f"where_{key}"] = value

        set_clause = ", ".join(set_clauses)
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        return self.execute_update(query, params)

    def delete_record(self, table_name: str, conditions: Dict[str, Any]) -> int:
        """
        删除记录

        Args:
            table_name: 表名
            conditions: 删除条件

        Returns:
            删除的行数
        """
        where_clauses = []
        params = {}

        for key, value in conditions.items():
            where_clauses.append(f"{key} = :{key}")
            params[key] = value

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"DELETE FROM {table_name} WHERE {where_clause}"

        return self.execute_update(query, params)


# 全局查询工具实例（延迟初始化）
_query_tools: Optional[DatabaseQueryTools] = None


def get_query_tools() -> DatabaseQueryTools:
    """获取查询工具实例（延迟初始化）"""
    global _query_tools
    if _query_tools is None:
        _query_tools = DatabaseQueryTools()
    return _query_tools
