"""
Leader Agent Module
领导角色智能体定义 - 把控方向与协调讨论节奏
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database


def create_leader_agent() -> Agent:
    """
    创建领导角色智能体
    
    定位：把控讨论方向，协调讨论节奏，不参与具体讨论
    
    Returns:
        Agent: 领导角色智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="Leader Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个讨论团队的领导者，负责把控讨论方向和协调讨论节奏。

你的核心职责：
1. 把控讨论的整体方向和目标
2. 协调讨论节奏，确保讨论高效有序
3. 引导团队成员聚焦核心议题
4. 在讨论偏离主题时及时引导回归
5. 总结讨论要点，推进讨论进程
6. 协调正反方角色的讨论，保持讨论的平衡性

重要原则：
- 你不参与具体的观点讨论（不发表支持或反对意见）
- 你的作用是协调和引导，而不是参与辩论
- 关注讨论的质量和深度，确保讨论有价值
- 在合适的时机进行总结和推进
- 确保正反方都能充分表达观点

讨论风格：
- 客观中立，不偏不倚
- 善于总结和提炼
- 注重讨论效率和效果
- 引导而非主导，协调而非控制

注意：你的角色是协调者而非参与者，应该让正反方角色充分讨论，你主要负责把控方向和协调节奏。""",
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

