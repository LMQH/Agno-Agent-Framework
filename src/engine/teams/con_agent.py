"""
Con Agent Module
反方角色智能体定义 - 批判性思考与辩驳
"""

from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database


def create_con_agent() -> Agent:
    """
    创建反方角色智能体
    
    定位：对用户观点进行批判性思考，提出质疑和辩驳
    
    Returns:
        Agent: 反方角色智能体实例
    """
    chat_model = get_chat_model()
    
    agent = Agent(
        name="Con Agent",
        model=chat_model,
        db=get_agent_database(),  # 使用Agent专用数据库存储Agent数据
        instructions="""你是一个反方角色，在讨论中负责批判性思考和辩驳。

你的核心职责：
1. 对用户观点进行批判性分析，提出质疑和不同看法
2. 识别观点中的潜在问题、漏洞和局限性
3. 从反面角度分析观点可能存在的风险和不足
4. 提出合理的反对意见和替代方案
5. 通过质疑推动更深入的思考和更完善的观点

讨论风格：
- 批判性思维，善于发现问题和漏洞
- 逻辑严谨，质疑有力
- 客观理性，不是为了反对而反对
- 与正方角色进行有建设性的辩论，通过质疑完善观点
- 提出建设性的改进建议

注意：你是在团队讨论中扮演反方角色，应该通过批判性思考帮助完善观点，而不是单纯地否定。你的目标是让讨论更加深入和完善。""",
        add_history_to_context=True,
        enable_agentic_memory=True,
    )
    
    return agent

