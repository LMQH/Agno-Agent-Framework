"""
Judge Agent Module
评判智能体定义 - 评估Team讨论输出质量
"""

import os
import logging
from agno.eval.agent_as_judge import AgentAsJudgeEval
from src.models.model_config import get_chat_model
from src.database.connection import get_team_database

logger = logging.getLogger(__name__)


def create_discussion_judge(
    score_threshold: float = None,
    criteria: str = None
) -> AgentAsJudgeEval:
    """
    创建讨论团队评判智能体
    
    用于评估讨论团队输出质量的评估器，使用numeric评分策略。
    
    Args:
        score_threshold: 评估分数阈值（默认7），分数达到此阈值视为达标
        criteria: 评估标准描述（可选，默认使用通用标准）
    
    Returns:
        AgentAsJudgeEval: 讨论评判评估器实例
    """
    # 获取模型
    chat_model = get_chat_model()
    
    # 获取数据库
    db = get_team_database()
    
    # 默认阈值
    if score_threshold is None:
        score_threshold = float(os.getenv("DISCUSSION_SCORE_THRESHOLD", "7.0"))
    
    # 默认评估标准
    if criteria is None:
        criteria = """讨论结果应该具备以下特点：
1. 观点清晰明确，逻辑严谨
2. 论证充分，有有力的证据和理论支持
3. 考虑了多角度和多方面的因素
4. 讨论深入，体现了正反方的充分辩论
5. 结论合理，有建设性
6. 整体质量高，能够有效回答用户问题"""
    
    evaluation = AgentAsJudgeEval(
        name="Discussion Quality Judge",
        model=chat_model,
        criteria=criteria,
        scoring_strategy="numeric",  # 使用numeric评分策略（0-10分）
        threshold=score_threshold,  # 分数阈值，低于此分数视为不达标
        db=db,  # 使用Team专用数据库
    )
    
    logger.debug(f"创建讨论评判评估器，阈值: {score_threshold}")
    
    return evaluation

