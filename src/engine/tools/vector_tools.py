"""
Vector Tools Module
向量数据库相关工具定义（知识库查询工具）
"""

from agno.tools import tool
from src.vector.query_tools import get_vector_tools
from src.vector.connection import get_milvus_client
import logging

logger = logging.getLogger(__name__)


@tool
def list_collections() -> str:
    """
    返回当前连接的知识库（Milvus向量数据库）中的所有集合（collection）列表
    
    如果连接不存在，会自动尝试连接并创建空知识库（如果数据库不存在会自动创建）。

    Returns:
        集合列表的字符串表示
    """
    try:
        # 确保连接已建立（如果不存在会自动创建连接和数据库）
        try:
            get_milvus_client()
        except Exception as conn_error:
            return f"无法连接到知识库（Milvus向量数据库）: {str(conn_error)}。请检查配置是否正确。"
        
        # 获取工具并列出集合
        vector_tools = get_vector_tools()
        collections = vector_tools.list_collections()

        # 如果没有集合，返回友好的提示（空知识库是正常的）
        if not collections:
            return "知识库已连接，但当前没有任何集合（collection）。知识库为空，可以开始创建集合。"

        result_parts = []
        result_parts.append(f"知识库集合列表（共 {len(collections)} 个）：\n")
        
        for collection_name in collections:
            result_parts.append(f"- {collection_name}")
        
        return "\n".join(result_parts)

    except Exception as e:
        logger.error(f"获取知识库集合列表失败: {e}", exc_info=True)
        return f"获取知识库集合列表失败: {str(e)}"


# 导出工具列表
vector_tools_list = [
    list_collections,
]

