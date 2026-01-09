"""
启动脚本
使用 AgentOS.serve() 方法启动服务
"""

import os
import sys
import argparse
from pathlib import Path

# 初始化日志系统（最先执行）
from src.utils.logger_config import setup_logging
setup_logging(project_root=Path(__file__).parent)

parser = argparse.ArgumentParser(description='启动 Agno Multi Agent Framework')
parser.add_argument('env', nargs='?', choices=['dev', 'show', 'prod'], default=None)
parser.add_argument('--host', type=str, default=None)
parser.add_argument('--port', type=int, default=None)
parser.add_argument('--reload', action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()
    
    if args.env:
        os.environ['APP_ENV_TYPE'] = args.env
    
    host = args.host or os.getenv('APP_HOST', '0.0.0.0')
    port = args.port or int(os.getenv('APP_PORT', '8564'))
    
    print(f"\n启动服务: http://{host}:{port}\n")
    
    from src.main import agent_os, app
    agent_os.serve(app=app, host=host, port=port, reload=args.reload)

