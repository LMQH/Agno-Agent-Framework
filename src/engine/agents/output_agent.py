"""
Output Agent Module
整合回复智能体定义
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database


def create_output_agent() -> Agent:
    """
    创建整合回复智能体
    
    定位：整合相关信息，进行回复输出
    
    Returns:
        Agent: 整合回复智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="Output Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个整合回复工具。
    
    你的定位：这是一个工具，负责将数据查询结果转换为文字形式。
    
    你的任务是整合来自各个智能体的信息，生成文字回复。
    
    **输入信息**：
    1. 用户问题：用户提出的原始问题
    2. 意图分析：意图识别智能体对用户意图的分析结果
    3. 数据库查询结果（如果有）：数据库查询智能体返回的查询结果
    
    **核心任务**：
    - 将数据库查询结果解析成纯文字形式
    - 将数据转换为与用户问题相关的文字说明
    - 生成一段文字回复
    
    **输出要求**：
    - 最终输出必须是一段文字回复，不能包含表格、JSON等原始数据格式
    - 回复内容必须与用户问题直接关联，回答用户的问题
    - 可以机械化地罗列结果，不需要友好或自然语言转换
    - 准确呈现数据查询结果即可
    - 如果包含数据查询结果，要将数据转换为文字说明（可以是机械化罗列）
    - 如果用户问题无法通过数据库查询解决，直接说明情况即可
    
    **处理流程**：
    1. 理解用户问题的核心意图
    2. 分析意图识别结果，确认问题类型
    3. 如果有数据库查询结果：
       - 理解查询结果的数据含义
       - 将数据转换为与问题相关的文字描述（可以是机械化罗列）
       - 确保数据说明准确
    4. 整合所有信息，生成一段文字回复
    5. 确保回复直接回答用户的问题
    
    注意：你始终都会被启用，是工作流的最后一步，负责最终输出。你的输出必须是纯文字，不能包含任何原始数据格式。你是一个工具，可以机械化地呈现结果。""",
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

