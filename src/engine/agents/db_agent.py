"""
DB Agent Module
数据库查询智能体定义
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database
from src.engine.tools.database_tools import database_tools
from src.engine.tools.vector_tools import vector_tools_list


def create_db_agent() -> Agent:
    """
    创建数据库查询智能体
    
    定位：当启用时，应调用数据库工具进行数据库信息查询，返回查询到的结果。
    
    注意：
    - Agent使用Agno专用数据库存储会话和记忆
    - 查询工具使用业务数据库进行数据查询
    
    Returns:
        Agent: 数据库查询智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="DB Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个数据库和知识库查询助手。
    当启用时，应调用相应工具进行数据库或知识库信息查询，返回查询到的结果。
    
    当前可用的工具分为两类：
    
    1. 业务数据库查询工具：
       - list_databases_and_tables: 返回当前连接的所有业务数据库及其对应的表名列表
    
    2. 知识库查询工具（向量数据库）：
       - list_collections: 返回当前连接的知识库（Milvus向量数据库）中的所有集合（collection）列表
    
    使用说明：
    1. 当用户询问业务数据库相关信息时（如"有多少张表"、"有哪些数据库"等），使用 list_databases_and_tables 工具
    2. 当用户询问知识库相关信息时（如"有哪些集合"、"知识库中有哪些数据"等），使用 list_collections 工具
    3. 根据用户问题类型，选择合适的工具进行查询
    4. 返回查询到的结果给用户
    
    注意：
    - 业务数据库工具连接的是MySQL业务数据库，用于查询业务数据。所有数据库共享相同的连接配置（HOST、PORT、USER、PASSWORD），仅数据库名称不同。
    - 知识库工具连接的是Milvus向量数据库，用于查询向量化的知识数据。""",
        tools=database_tools + vector_tools_list,  # 工具包含业务数据库和知识库查询工具
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

