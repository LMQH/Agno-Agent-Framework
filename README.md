# Agno Multi Agent Framework

## 环境要求

- **Python**: 3.12.0+
- **操作系统**: Linux, macOS, Windows
- **数据库**: MySQL 8.0+, Milvus 2.3+

## 文件架构

```
project_agno_base/
├── bin/                      # 服务管理脚本
│   ├── start.sh              # 启动服务（Linux/Mac）
│   ├── stop.sh               # 停止服务（Linux/Mac）
│   ├── status.sh             # 查看服务状态（Linux/Mac）
│   ├── setup_conda_env.sh    # Conda 环境设置脚本（Linux/Mac）
│   └── setup_conda_env.bat   # Conda 环境设置脚本（Windows）
├── src/                      # 源代码
│   ├── engine/               # Engine 引擎模块
│   │   ├── __init__.py
│   │   ├── workflows/        # 工作流定义
│   │   │   ├── __init__.py
│   │   │   └── workflow.py   # 主工作流定义
│   │   ├── agents/           # Agent 定义
│   │   │   ├── __init__.py
│   │   │   ├── db_agent.py   # 数据库查询 Agent
│   │   │   ├── intent_agent.py  # 意图识别 Agent
│   │   │   ├── judge_agent.py   # 讨论评估 Agent
│   │   │   └── output_agent.py  # 输出整合 Agent
│   │   ├── tools/            # 自定义工具
│   │   │   ├── __init__.py
│   │   │   ├── database_tools.py  # 数据库工具（Agno Tools）
│   │   │   └── vector_tools.py    # 向量数据库工具（Agno Tools）
│   │   └── teams/            # Team 定义
│   │       ├── __init__.py
│   │       ├── team.py          # 讨论团队主类
│   │       ├── pro_agent.py      # 正方角色 Agent
│   │       ├── con_agent.py      # 反方角色 Agent
│   │       └── leader_agent.py   # 领导角色 Agent
│   ├── agentos/              # AgentOS 配置
│   │   └── __init__.py
│   ├── api/                   # API 接口模块
│   │   ├── __init__.py
│   │   ├── router.py         # API 路由定义
│   │   ├── models.py         # API 数据模型
│   │   └── dependencies.py  # API 依赖注入
│   ├── database/             # 数据库模块
│   │   ├── __init__.py
│   │   ├── connection.py     # Agno 专用数据库连接
│   │   ├── config.py         # 数据库配置
│   │   ├── models.py         # 数据模型
│   │   ├── query_tools.py    # Agno 数据库查询工具
│   │   ├── business_db.py    # 业务数据库管理器
│   │   └── business_query_tools.py  # 业务数据库查询工具
│   ├── knowledge/            # 知识库模块
│   │   ├── __init__.py
│   │   └── config.py         # 知识库配置（Milvus + MySQL）
│   ├── models/               # 模型配置
│   │   ├── __init__.py
│   │   └── model_config.py   # 模型配置（DeepSeek、Embedding）
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   ├── config_loader.py  # 配置加载器
│   │   ├── ip_env_mapping.py # IP 环境映射
│   │   ├── logger_config.py  # 日志配置
│   │   └── yaml_agent_loader.py  # YAML Agent 加载器
│   ├── vector/               # 向量数据库模块
│   │   ├── __init__.py
│   │   ├── connection.py     # Milvus 连接
│   │   └── query_tools.py    # Milvus 查询工具
│   └── main.py               # 应用入口
├── tests/                    # 测试代码
│   ├── __init__.py
│   ├── test_database.py      # 数据库测试
│   ├── test_ip_detection.py  # IP 检测测试
│   └── test_milvus.py        # Milvus 连接测试
├── scripts/                  # 脚本工具
│   └── create_env_files.py   # 环境文件创建脚本
├── document/                 # 文档目录
│   ├── DEVELOPMENT_RECORD.md # 开发记录文档
│   └── AGNO_MD/             # Agno 框架文档
├── requirements.txt          # Python 依赖
├── pyproject.toml            # 项目配置
├── env.template              # 环境变量配置模板
└── README.md                 # 项目说明
```
