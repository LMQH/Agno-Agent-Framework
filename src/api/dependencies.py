"""
API Dependencies
API 依赖注入定义
"""

from functools import lru_cache
from src.database.query_tools import get_query_tools, DatabaseQueryTools


@lru_cache()
def get_query_tools_dependency() -> DatabaseQueryTools:
    """
    获取查询工具实例（依赖注入）
    
    使用 lru_cache 确保在同一个请求中返回同一个实例
    """
    return get_query_tools()

