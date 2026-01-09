"""
Main Application Entry Point
主应用入口文件，基于 AgentOS 提供完整的 API 服务
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 环境配置加载（日志系统已在start.py中初始化）
from src.utils.config_loader import get_config_loader
get_config_loader().load_config(auto_detect_ip=True, project_root=Path(__file__).parent.parent)

# 创建 base_app 并注册自定义路由
base_app = FastAPI(title="Agno Multi Agent Framework", description="Multi Agent Framework based on Agno", version="0.1.0")
base_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from src.api import api_router, root_router
base_app.include_router(root_router)
base_app.include_router(api_router)

# 创建 AgentOS 实例并获取应用
from src.agentos import create_agentos
agent_os = create_agentos(base_app=base_app)
app = agent_os.get_app()

