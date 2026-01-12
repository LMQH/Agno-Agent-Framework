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
    如果默认集合不存在，会自动创建默认集合 agno_knowledge_default。

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


@tool
def get_collection_info(collection_name: str) -> str:
    """
    获取指定集合的详细信息，包括字段信息、实体数量等
    
    Args:
        collection_name: 集合名称
    
    Returns:
        集合信息的字符串表示
    """
    try:
        # 确保连接已建立
        try:
            get_milvus_client()
        except Exception as conn_error:
            return f"无法连接到知识库（Milvus向量数据库）: {str(conn_error)}。请检查配置是否正确。"
        
        vector_tools = get_vector_tools()
        
        # 检查集合是否存在
        if not vector_tools.collection_exists(collection_name):
            return f"集合 '{collection_name}' 不存在。"
        
        # 获取集合信息
        info = vector_tools.get_collection_info(collection_name)
        count = vector_tools.get_collection_count(collection_name)
        
        result_parts = []
        result_parts.append(f"集合名称: {info['name']}")
        result_parts.append(f"实体数量: {count}")
        result_parts.append(f"\n字段信息:")
        
        for field in info['fields']:
            field_desc = f"  - {field['name']}: {field['type']}"
            if field.get('is_primary'):
                field_desc += " (主键)"
            if field.get('auto_id'):
                field_desc += " (自动ID)"
            result_parts.append(field_desc)
        
        return "\n".join(result_parts)
        
    except Exception as e:
        logger.error(f"获取集合信息失败: {e}", exc_info=True)
        return f"获取集合信息失败: {str(e)}"


@tool
def search_knowledge(collection_name: str, query_text: str, limit: int = 5) -> str:
    """
    在指定集合中搜索相似的知识内容
    
    注意：此工具需要先使用嵌入模型将查询文本转换为向量，然后进行向量搜索。
    当前版本返回提示信息，实际向量搜索功能需要配合嵌入模型使用。
    
    Args:
        collection_name: 集合名称
        query_text: 查询文本
        limit: 返回结果数量（默认5）
    
    Returns:
        搜索结果或提示信息
    """
    try:
        # 确保连接已建立
        try:
            get_milvus_client()
        except Exception as conn_error:
            return f"无法连接到知识库（Milvus向量数据库）: {str(conn_error)}。请检查配置是否正确。"
        
        vector_tools = get_vector_tools()
        
        # 检查集合是否存在
        if not vector_tools.collection_exists(collection_name):
            return f"集合 '{collection_name}' 不存在。请先创建集合或使用 list_collections 查看可用集合。"
        
        # 获取集合信息
        count = vector_tools.get_collection_count(collection_name)
        
        if count == 0:
            return f"集合 '{collection_name}' 中没有任何数据。请先向集合中插入数据。"
        
        # 注意：实际的向量搜索需要：
        # 1. 使用嵌入模型将 query_text 转换为向量
        # 2. 调用 vector_tools.search_vectors() 进行搜索
        # 这里返回提示信息，实际实现需要配合嵌入模型
        return f"""集合 '{collection_name}' 中有 {count} 条数据。

注意：向量搜索功能需要先将查询文本转换为向量。
当前查询文本: "{query_text}"
建议使用嵌入模型（如 text-embedding-v2）将文本转换为向量后，再调用向量搜索功能。

如需使用完整的向量搜索功能，请确保：
1. 已配置嵌入模型（EMBEDDING_API_KEY）
2. 集合中已插入向量数据
3. 使用嵌入模型将查询文本转换为向量维度匹配的向量"""
        
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}", exc_info=True)
        return f"搜索知识库失败: {str(e)}"


# 导出工具列表
vector_tools_list = [
    list_collections,
    get_collection_info,
    search_knowledge,
]

