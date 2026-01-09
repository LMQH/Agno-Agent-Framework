"""
Database Tools Module
数据库相关工具定义（使用业务数据库）
"""

from agno.tools import tool
from src.database.business_query_tools import get_business_query_tools
from src.database.business_db import list_business_databases


@tool
def list_databases_and_tables() -> str:
    """
    返回当前连接的所有业务数据库及其对应的表名列表

    Returns:
        数据库和表名的字符串表示，格式为每个数据库及其表名的列表
    """
    try:
        databases = list_business_databases()
        
        if not databases:
            return "未配置业务数据库（BUSINESS_MYSQL_DATABASES）"
        
        result_parts = []
        result_parts.append(f"业务数据库列表（共 {len(databases)} 个）：\n")
        
        for db_name in databases:
            try:
                query_tools = get_business_query_tools(default_database=db_name)
                tables = query_tools.list_tables(database_name=db_name)
                
                result_parts.append(f"数据库: {db_name}")
                if not tables:
                    result_parts.append("  表: （无）")
                else:
                    result_parts.append(f"  表 ({len(tables)} 个): {', '.join(tables)}")
                result_parts.append("")  # 空行分隔
            except Exception as e:
                result_parts.append(f"数据库: {db_name}")
                result_parts.append(f"  错误: 获取表列表失败 - {str(e)}")
                result_parts.append("")  # 空行分隔
        
        return "\n".join(result_parts)
    
    except Exception as e:
        return f"获取数据库和表列表失败: {str(e)}"


# 导出工具列表
database_tools = [
    list_databases_and_tables,
]

