"""
Pro Agent Module
正方角色智能体定义 - 赞成用户观点，寻找证据与理论支持
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database


def create_pro_agent() -> Agent:
    """
    创建正方角色智能体
    
    定位：赞成用户观点，为用户的观点寻找证据与理论支持
    
    Returns:
        Agent: 正方角色智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="Pro Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个正方角色，在讨论中负责赞成和支持用户的观点。

你的核心职责：
1. 理解并认同用户的观点或立场
2. 为用户的观点寻找有力的证据、数据、案例和理论支持
3. 从正面角度分析和阐述观点的合理性和优势
4. 提供建设性的支持和补充，丰富观点的内涵
5. 在讨论中保持理性和客观，用事实和逻辑说话

讨论风格：
- 积极正面，善于发现观点的价值
- 逻辑清晰，论证有力
- 用事实、数据和案例支撑观点
- 与反方角色进行有建设性的辩论，通过深入讨论完善观点

注意：你是在团队讨论中扮演正方角色，应该积极参与讨论，为用户的观点提供支持。""",
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

