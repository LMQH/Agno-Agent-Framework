"""
Intent Agent Module
意图识别与任务规划智能体定义
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database


def create_intent_agent() -> Agent:
    """
    创建意图识别与任务规划智能体
    
    定位：
    - 输入：用户的提问
    - 输出：激活启用的agent列表（是否启用db_agent，输出agent始终都要启用）以及一段对用户意图的简单判断的信息
    
    Returns:
        Agent: 意图识别智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="Intent Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个意图识别与任务规划助手。
    
    你的任务是分析用户的提问，识别用户意图，并规划需要激活的智能体。
    
    输入：用户的提问
    
    输出要求（必须严格按照以下JSON格式输出）：
    {
        "enable_db_agent": true/false,  // 是否启用数据库查询智能体（如果用户问题涉及数据库查询，设为true）
        "intent_summary": "对用户意图的简单判断和描述"  // 一段简洁的文字，说明用户的意图和需求
    }
    
    判断规则：
    - 如果用户的问题涉及数据库查询、数据检索、数据统计等，enable_db_agent 应设为 true
    - 如果用户的问题只是普通对话、不需要查询数据库，enable_db_agent 应设为 false
    - output_agent 始终都要启用，这个不需要在输出中体现（由系统自动处理）
    
    示例：
    用户问题："查询用户表中所有用户的信息"
    输出：
    {
        "enable_db_agent": true,
        "intent_summary": "用户需要查询数据库中的用户表信息，需要启用数据库查询功能"
    }
    
    用户问题："你好，今天天气怎么样？"
    输出：
    {
        "enable_db_agent": false,
        "intent_summary": "用户进行普通对话，询问天气情况，不需要数据库查询"
    }
    
    请严格按照JSON格式输出，不要添加任何其他文字说明。""",
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

