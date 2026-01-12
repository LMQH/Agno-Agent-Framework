"""
AgentOS Module
AgentOS 配置模块
"""

import os
import logging
from agno.os import AgentOS

logger = logging.getLogger(__name__)


def create_agentos(base_app=None, **kwargs) -> AgentOS:
    """
    创建 AgentOS 实例
    
    Args:
        base_app: FastAPI 应用实例（可选）
        **kwargs: 其他 AgentOS 参数
    """
    # 设置默认值
    kwargs.setdefault('teams', [])
    
    # 如果没有提供 tracing_db，使用 Agno 专用数据库（用于追踪和知识库存储）
    if 'tracing_db' not in kwargs:
        from src.database.connection import get_agent_database
        kwargs['tracing_db'] = get_agent_database()
        logger.info("已配置 AgentOS 追踪数据库（用于追踪和知识库存储）")
    
    # 确保自动配置数据库（AgentOS 会自动从环境变量读取数据库配置）
    if 'auto_provision_dbs' not in kwargs:
        kwargs['auto_provision_dbs'] = True
    
    # 如果没有提供 agents，默认添加所有智能体
    if 'agents' not in kwargs or not kwargs['agents']:
        from src.engine.agents import (
            create_intent_agent,
            create_db_agent,
            create_output_agent,
        )
        intent_agent = create_intent_agent()
        db_agent = create_db_agent()
        output_agent = create_output_agent()
        kwargs['agents'] = [intent_agent, db_agent, output_agent]
        logger.info("已自动注册所有智能体: Intent Agent, DB Agent, Output Agent")
    
    # 如果没有提供 workflows，默认添加主工作流
    if 'workflows' not in kwargs:
        from src.engine.workflows.workflow import create_main_workflow
        main_workflow = create_main_workflow()
        kwargs['workflows'] = [main_workflow]
        logger.info("已自动注册主工作流")
    
    # 从环境变量读取 tracing
    if 'tracing' not in kwargs:
        kwargs['tracing'] = os.getenv("AGENTOS_TRACING", "true").lower() == "true"
    
    # 传入 base_app
    if base_app is not None:
        kwargs['base_app'] = base_app
    
    return AgentOS(**kwargs)

