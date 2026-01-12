"""
Discussion Team Module
讨论团队组合与配置 - 实现讨论循环逻辑和评估控制
"""

import os
import logging
from typing import Dict, Any, Optional
from agno.team.team import Team
from agno.eval.agent_as_judge import AgentAsJudgeResult

from src.models.model_config import get_chat_model
from src.database.connection import get_team_database
from src.engine.teams.pro_agent import create_pro_agent
from src.engine.teams.con_agent import create_con_agent
from src.engine.teams.leader_agent import create_leader_agent
from src.engine.agents.judge_agent import create_discussion_judge

logger = logging.getLogger(__name__)


class DiscussionTeam:
    """
    讨论团队类
    
    封装讨论团队的执行逻辑，包括轮次控制和评估判断。
    支持通过评估分数和轮次双重限制控制讨论流程。
    """
    
    def __init__(
        self,
        max_rounds: int = None,
        score_threshold: float = None,
        team_name: str = "Discussion Team"
    ):
        """
        初始化讨论团队
        
        Args:
            max_rounds: 最大讨论轮次（默认3轮）
            score_threshold: 评估分数阈值（默认7.0）
            team_name: 团队名称
        """
        # 配置参数
        self.max_rounds = max_rounds or int(os.getenv("DISCUSSION_MAX_ROUNDS", "3"))
        self.score_threshold = score_threshold or float(os.getenv("DISCUSSION_SCORE_THRESHOLD", "7.0"))
        self.team_name = team_name
        
        # 创建成员Agent
        self.pro_agent = create_pro_agent()
        self.con_agent = create_con_agent()
        self.leader_agent = create_leader_agent()
        
        # 创建Team实例
        chat_model = get_chat_model()
        db = get_team_database()
        
        self.team = Team(
            name=self.team_name,
            id="discussion_team",
            model=chat_model,
            members=[self.pro_agent, self.con_agent, self.leader_agent],
            instructions=[
                "进行深入的观点讨论。",
                "正方角色应该支持用户观点，寻找证据和理论支持。",
                "反方角色应该进行批判性思考，提出质疑和辩驳。",
                "领导角色应该把控方向，协调讨论节奏，不参与具体讨论。",
                "通过正反双方的充分讨论，形成全面、深入的讨论结果。"
            ],
            db=db,
        )
        
        # 创建评估器
        self.judge = create_discussion_judge(score_threshold=self.score_threshold)
        
        logger.debug(f"初始化讨论团队: {self.team_name}, 最大轮次: {self.max_rounds}, 分数阈值: {self.score_threshold}")
    
    async def run(
        self,
        user_query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行讨论团队讨论
        
        Args:
            user_query: 用户问题
            context: 额外上下文信息（如数据查询结果等）
        
        Returns:
            包含讨论结果和评估信息的字典：
            {
                "discussion_result": str,  # 讨论结果内容
                "evaluation_result": Optional[AgentAsJudgeResult],  # 评估结果
                "final_score": Optional[float],  # 最终评估分数
                "total_rounds": int,  # 总讨论轮次
                "reached_threshold": bool,  # 是否达到阈值
            }
        """
        # 构建讨论输入
        discussion_input = user_query
        if context:
            discussion_input = f"{user_query}\n\n相关信息：\n{context}"
        
        logger.info(f"开始讨论团队讨论，用户问题: {user_query[:50]}...")
        logger.info(f"最大轮次: {self.max_rounds}, 分数阈值: {self.score_threshold}")
        
        final_result = None
        final_evaluation = None
        total_rounds = 0
        reached_threshold = False
        
        # 讨论循环
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"第 {round_num}/{self.max_rounds} 轮讨论开始")
            
            try:
                # 执行讨论
                response = await self.team.arun(discussion_input)
                discussion_result = str(response.content)
                total_rounds = round_num
                
                logger.info(f"第 {round_num} 轮讨论完成")
                
                # 评估讨论结果
                logger.info(f"开始评估第 {round_num} 轮讨论结果")
                evaluation_result = self.judge.run(
                    input=user_query,
                    output=discussion_result,
                    print_results=False,
                    print_summary=False,
                )
                
                # 获取评估分数
                score = None
                if evaluation_result and hasattr(evaluation_result, 'score'):
                    score = evaluation_result.score
                elif evaluation_result and hasattr(evaluation_result, 'result'):
                    # 如果score不在evaluation_result上，尝试从result获取
                    if hasattr(evaluation_result.result, 'score'):
                        score = evaluation_result.result.score
                
                logger.info(f"第 {round_num} 轮评估完成，分数: {score}")
                
                # 保存当前轮次结果
                final_result = discussion_result
                final_evaluation = evaluation_result
                
                # 判断是否达到阈值
                if score is not None and score >= self.score_threshold:
                    reached_threshold = True
                    logger.info(f"讨论达到目标分数 ({score} >= {self.score_threshold})，停止讨论")
                    break
                
                # 如果未达到阈值但已经是最后一轮，继续使用当前结果
                if round_num == self.max_rounds:
                    logger.info(f"已达到最大轮次 ({self.max_rounds})，停止讨论")
                    break
                
                # 准备下一轮讨论（可以基于当前结果进行深入讨论）
                # 这里可以添加基于评估反馈的改进逻辑
                discussion_input = f"{user_query}\n\n基于之前的讨论，请继续深入讨论该问题。\n\n之前的讨论结果：\n{discussion_result}"
                
            except Exception as e:
                logger.error(f"第 {round_num} 轮讨论或评估失败: {e}", exc_info=True)
                # 如果有之前的结果，使用之前的结果
                if final_result is None:
                    raise
                break
        
        # 构建返回结果
        result = {
            "discussion_result": final_result or "",
            "evaluation_result": final_evaluation,
            "final_score": None,
            "total_rounds": total_rounds,
            "reached_threshold": reached_threshold,
        }
        
        # 提取最终分数
        if final_evaluation:
            if hasattr(final_evaluation, 'score'):
                result["final_score"] = final_evaluation.score
            elif hasattr(final_evaluation, 'result'):
                if hasattr(final_evaluation.result, 'score'):
                    result["final_score"] = final_evaluation.result.score
        
        logger.info(f"讨论团队讨论完成，总轮次: {total_rounds}, 最终分数: {result['final_score']}, 达到阈值: {reached_threshold}")
        
        return result


def create_discussion_team(
    max_rounds: int = None,
    score_threshold: float = None,
    team_name: str = "Discussion Team"
) -> DiscussionTeam:
    """
    创建讨论团队实例
    
    Args:
        max_rounds: 最大讨论轮次（默认3轮）
        score_threshold: 评估分数阈值（默认7.0）
        team_name: 团队名称
    
    Returns:
        DiscussionTeam: 讨论团队实例
    """
    return DiscussionTeam(
        max_rounds=max_rounds,
        score_threshold=score_threshold,
        team_name=team_name
    )


def create_discussion_team_for_agentos(team_name: str = "Discussion Team") -> Team:
    """
    创建讨论团队的 Team 对象（用于注册到 AgentOS）
    
    此函数复用 create_discussion_team 的内部实现，返回 Team 对象而不是 DiscussionTeam 包装类。
    这样可以在 AgentOS 控制面板上显示和使用讨论团队。
    
    Args:
        team_name: 团队名称
    
    Returns:
        Team: Team 对象实例，可用于注册到 AgentOS
    """
    # 复用 create_discussion_team 创建 DiscussionTeam，然后返回其内部的 Team 对象
    discussion_team = create_discussion_team(team_name=team_name)
    return discussion_team.team