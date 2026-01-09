"""
YAML Agent Loader
从 YAML 配置创建 Agent

⚠️ 注意：此模块当前未使用
- 当前项目的 Agents、Teams 和 Workflows 直接在代码中定义
- 此模块保留以备后续扩展使用
- 如需启用 YAML 配置加载，请在 `src/agentos/__init__.py` 中恢复相关代码
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from agno.agent import Agent
from src.models.model_config import get_chat_model
from src.database.connection import get_agent_database
from src.engine.tools.database_tools import database_tools
import logging

logger = logging.getLogger(__name__)

# 工具名称映射
TOOL_MAPPING = {
    "database_tools": database_tools,
    "database_query_tool": database_tools,
    # 可以添加更多工具映射
}


def create_agent_from_yaml_config(
    agent_config: Dict[str, Any],
    agent_name: str
) -> Agent:
    """
    从 YAML 配置创建 Agent
    
    Args:
        agent_config: YAML 中的 Agent 配置字典
        agent_name: Agent 名称
    
    Returns:
        Agent 实例
    """
    # 获取模型（始终使用项目配置的模型）
    model = get_chat_model()
    
    # 从 YAML 配置提取参数
    name = agent_config.get("name", agent_name)
    instructions = agent_config.get("instructions", "")
    
    # 处理工具
    tools = []
    if "tools" in agent_config:
        tool_names = agent_config["tools"]
        if isinstance(tool_names, list):
            for tool_name in tool_names:
                if tool_name in TOOL_MAPPING:
                    tool_list = TOOL_MAPPING[tool_name]
                    if isinstance(tool_list, list):
                        tools.extend(tool_list)
                    else:
                        tools.append(tool_list)
                else:
                    logger.warning(f"未找到工具映射: {tool_name}")
    
    # 构建 Agent 参数
    agent_kwargs = {
        "name": name,
        "model": model,
        "instructions": instructions,
    }
    
    # 添加工具（如果有）
    if tools:
        agent_kwargs["tools"] = tools
    
    # 添加历史记录配置
    if agent_config.get("add_history_to_context", False):
        agent_kwargs["add_history_to_context"] = True
    
    # 添加记忆配置
    if agent_config.get("enable_agentic_memory", False):
        agent_kwargs["enable_agentic_memory"] = True
    elif agent_config.get("enable_memory", False):
        # 兼容旧的 enable_memory 配置
        agent_kwargs["enable_agentic_memory"] = True
    
    # 添加数据库配置（如果指定）
    if agent_config.get("use_database", False):
        agent_kwargs["db"] = get_agent_database()
    
    # 创建 Agent
    agent = Agent(**agent_kwargs)
    
    logger.debug(f"从 YAML 创建 Agent '{name}'，使用模型: {model.id}")
    return agent


def load_agents_from_yaml(
    yaml_path: str = "config/agents.yaml"
) -> List[Agent]:
    """
    从 YAML 文件加载并创建所有 Agent
    
    Args:
        yaml_path: YAML 文件路径（相对于项目根目录）
    
    Returns:
        Agent 列表
    """
    project_root = Path(__file__).parent.parent.parent
    full_path = project_root / yaml_path
    
    if not full_path.exists():
        logger.warning(f"YAML 配置文件不存在: {yaml_path}，使用空列表")
        return []
    
    with open(full_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if not config or 'agents' not in config:
        logger.warning(f"YAML 配置文件中没有 agents 配置")
        return []
    
    agents = []
    for agent_name, agent_config in config['agents'].items():
        try:
            agent = create_agent_from_yaml_config(
                agent_config=agent_config,
                agent_name=agent_name
            )
            agents.append(agent)
        except Exception as e:
            logger.error(f"创建 Agent '{agent_name}' 失败: {e}", exc_info=True)
            continue
    
    logger.debug(f"从 YAML 成功创建 {len(agents)} 个 Agent")
    return agents

