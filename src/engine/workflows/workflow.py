"""
Workflow Module
主工作流定义 - 编排意图识别、数据库查询和整合输出
"""

import json
import logging
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from src.engine.agents.intent_agent import create_intent_agent
from src.engine.agents.db_agent import create_db_agent
from src.engine.agents.output_agent import create_output_agent
from src.engine.teams.team import create_discussion_team
from src.database.connection import get_workflow_database

logger = logging.getLogger(__name__)


async def main_workflow_steps(*args, **kwargs):
    """
    主工作流步骤
    
    当使用 Step 对象包装函数时，使用 *args 和 **kwargs 可以避免参数传递冲突
    
    Args:
        *args: 位置参数（可能是 session_state 和 execution_input）
        **kwargs: 关键字参数
    
    Returns:
        最终输出结果
    """
    # 从参数中提取 session_state 和 execution_input
    # Step 对象可能以不同的方式传递参数，需要适配
    session_state = kwargs.get('session_state', {})
    execution_input = kwargs.get('execution_input') or kwargs.get('input')
    
    # 如果没有从 kwargs 获取到，尝试从 args 获取
    if execution_input is None and len(args) >= 1:
        if len(args) == 1:
            # 只有一个参数，可能是 execution_input
            execution_input = args[0]
        elif len(args) >= 2:
            # 多个参数，第一个可能是 session_state，第二个是 execution_input
            session_state = args[0] if isinstance(args[0], dict) else session_state
            execution_input = args[1] if len(args) > 1 else execution_input
    
    # 从 execution_input 提取用户输入
    # execution_input 可能是字符串，也可能是对象，需要适配
    if isinstance(execution_input, str):
        user_input = execution_input
    elif hasattr(execution_input, 'get_input_as_string'):
        user_input = execution_input.get_input_as_string()
    elif hasattr(execution_input, 'input'):
        user_input = execution_input.input
    elif hasattr(execution_input, 'content'):
        user_input = execution_input.content
    elif isinstance(execution_input, dict):
        user_input = execution_input.get('input') or execution_input.get('user_input') or str(execution_input)
    else:
        user_input = str(execution_input)
    
    # 创建智能体实例
    intent_agent = create_intent_agent()
    db_agent = create_db_agent()
    output_agent = create_output_agent()
    
    # 步骤1：意图识别与任务规划
    logger.info(f"开始意图识别，用户输入: {user_input}")
    intent_result = await intent_agent.arun(user_input)
    intent_content = intent_result.content
    
    # 解析意图识别结果
    try:
        # 尝试从内容中提取JSON
        # 如果内容包含JSON，提取它
        json_start = intent_content.find('{')
        json_end = intent_content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = intent_content[json_start:json_end]
            intent_data = json.loads(json_str)
        else:
            # 如果没有找到JSON，尝试直接解析整个内容
            intent_data = json.loads(intent_content)
        
        enable_db_agent = intent_data.get("enable_db_agent", False)
        enable_discussion_team = intent_data.get("enable_discussion_team", False)
        intent_summary = intent_data.get("intent_summary", "未识别到明确意图")
        
        logger.info(f"意图识别结果: enable_db_agent={enable_db_agent}, enable_discussion_team={enable_discussion_team}, intent_summary={intent_summary}")
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"解析意图识别结果失败: {e}，使用默认值")
        enable_db_agent = False
        enable_discussion_team = False
        intent_summary = intent_content  # 使用原始内容作为摘要
    
    # 步骤2：数据库查询（如果启用）
    db_result_content = None
    if enable_db_agent:
        logger.info("开始数据库查询...")
        try:
            # 构建数据库查询的输入，包含用户问题和意图信息
            db_input = f"""用户问题：{user_input}
            
意图分析：{intent_summary}

请根据用户问题执行相应的数据库查询，返回查询结果。"""
            
            db_result = await db_agent.arun(db_input)
            db_result_content = db_result.content
            logger.info("数据库查询完成")
        except Exception as e:
            logger.error(f"数据库查询失败: {e}")
            db_result_content = f"数据库查询过程中出现错误: {str(e)}"
    else:
        logger.info("跳过数据库查询步骤")
    
    # 步骤3：讨论团队（如果启用）
    discussion_result_content = None
    discussion_evaluation_info = None
    if enable_discussion_team:
        logger.info("开始讨论团队讨论...")
        try:
            # 创建讨论团队
            discussion_team = create_discussion_team()
            
            # 构建讨论上下文（包含数据查询结果）
            discussion_context = None
            if enable_db_agent and db_result_content:
                discussion_context = f"数据查询结果：\n{db_result_content}"
            
            # 执行讨论
            discussion_result = await discussion_team.run(
                user_query=user_input,
                context=discussion_context
            )
            
            discussion_result_content = discussion_result.get("discussion_result", "")
            
            # 构建评估信息
            eval_result = discussion_result.get("evaluation_result")
            final_score = discussion_result.get("final_score")
            total_rounds = discussion_result.get("total_rounds", 0)
            reached_threshold = discussion_result.get("reached_threshold", False)
            
            if final_score is not None:
                discussion_evaluation_info = f"讨论评估分数: {final_score}/10, 讨论轮次: {total_rounds}, 达到阈值: {reached_threshold}"
            else:
                discussion_evaluation_info = f"讨论轮次: {total_rounds}, 达到阈值: {reached_threshold}"
            
            logger.info(f"讨论团队讨论完成: {discussion_evaluation_info}")
        except Exception as e:
            logger.error(f"讨论团队讨论失败: {e}", exc_info=True)
            discussion_result_content = f"讨论团队讨论过程中出现错误: {str(e)}"
            discussion_evaluation_info = "讨论评估失败"
    else:
        logger.info("跳过讨论团队步骤")
    
    # 步骤4：整合输出
    logger.info("开始整合输出...")
    
    # 构建整合输出的输入
    output_parts = [
        f"用户问题：{user_input}",
        f"意图分析：{intent_summary}",
    ]
    
    if enable_db_agent and db_result_content:
        output_parts.append(f"数据库查询结果：\n{db_result_content}")
    else:
        output_parts.append("未执行数据库查询")
    
    if enable_discussion_team and discussion_result_content:
        output_parts.append(f"讨论团队讨论结果：\n{discussion_result_content}")
        if discussion_evaluation_info:
            output_parts.append(f"讨论评估信息：{discussion_evaluation_info}")
    else:
        output_parts.append("未执行讨论团队讨论")
    
    output_input = "\n\n".join(output_parts)
    output_input += "\n\n请基于以上信息，生成一个完整、清晰、友好的回复给用户。"
    
    output_result = await output_agent.arun(output_input)
    logger.info("整合输出完成")
    
    return output_result


def create_main_workflow() -> Workflow:
    """
    创建主工作流
    
    根据官方范式，使用 Step 对象包装函数
    
    Returns:
        Workflow: 主工作流实例
    """
    workflow = Workflow(
        name="Main Workflow",
        description="主工作流：意图识别 -> 数据库查询（可选）-> 讨论团队（可选）-> 整合输出",
        steps=[
            Step(name="main_workflow", executor=main_workflow_steps),
        ],
        db=get_workflow_database(),  # 使用Workflow专用数据库存储工作流数据
        add_workflow_history_to_steps=True,
    )
    
    return workflow

