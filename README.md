# Agno Multi Agent Framework

## 文件架构

```
ai/
├── bin/                      # Linux 服务管理脚本
│   ├── start.sh              # 启动服务
│   ├── stop.sh               # 停止服务
│   └── status.sh             # 查看服务状态
├── config/                   # 配置文件
│   ├── agents.yaml           # Agent 配置
│   ├── teams.yaml            # Team 配置
│   └── workflows.yaml        # Workflow 配置
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
│   │   │   └── output_agent.py  # 输出整合 Agent
│   │   ├── tools/            # 自定义工具
│   │   │   ├── __init__.py
│   │   │   ├── database_tools.py  # 数据库工具（Agno Tools）
│   │   │   └── vector_tools.py    # 向量数据库工具（Agno Tools）
│   │   └── teams/            # Team 定义（预留）
│   │       └── __init__.py
│   ├── agentos/              # AgentOS 配置
│   │   └── __init__.py
│   ├── database/             # 数据库模块
│   │   ├── __init__.py
│   │   ├── connection.py     # Agno 专用数据库连接
│   │   ├── config.py         # 数据库配置
│   │   ├── models.py         # 数据模型
│   │   ├── query_tools.py    # Agno 数据库查询工具
│   │   ├── business_db.py    # 业务数据库管理器
│   │   └── business_query_tools.py  # 业务数据库查询工具
│   ├── models/                # 模型配置
│   │   ├── __init__.py
│   │   └── model_config.py   # 模型配置（DeepSeek、Embedding）
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── config_loader.py  # 配置加载器
│   │   ├── ip_env_mapping.py # IP 环境映射
│   │   └── yaml_agent_loader.py  # YAML Agent 加载器
│   └── vector/                # 向量数据库模块
│       ├── __init__.py
│       ├── connection.py      # Milvus 连接
│       └── query_tools.py     # Milvus 查询工具
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── test_database.py       # 数据库测试
│   ├── test_ip_detection.py   # IP 检测测试
│   └── test_milvus.py         # Milvus 连接测试
├── scripts/                   # 脚本工具
│   └── create_env_files.py    # 环境文件创建脚本
├── document/                  # 文档目录
│   ├── ENV_SETUP.md          # 环境配置说明
│   └── AGNO_MD/              # Agno 框架文档
├── main.py                    # 应用入口
├── requirements.txt           # Python 依赖
├── pyproject.toml             # 项目配置
├── env.template               # 环境变量配置模板
├── env.dev                    # 开发环境配置（可提交）
├── env.show                   # 展示环境配置（可提交）
├── env.prod                   # 生产环境配置（可提交）
└── README.md                  # 项目说明
```

## 环境配置模式

项目支持三种环境：**dev**（开发）、**show**（展示/预发布）、**prod**（生产）。

### 环境配置文件

项目包含三个环境配置文件，这些文件**可以提交到版本控制系统**：

- `env.dev` - 开发环境配置
- `env.show` - 展示/预发布环境配置  
- `env.prod` - 生产环境配置

**注意**：如果需要本地覆盖配置，可以创建 `.env` 文件（此文件会被忽略，不会提交到版本控制）。

### 创建环境配置文件

```bash
# 方法1：使用脚本自动创建（推荐）
python scripts/create_env_files.py

# 方法2：手动创建
cp env.template env.dev
cp env.template env.show
cp env.template env.prod

# 编辑对应的环境文件，设置实际的配置值
```

### 环境切换

#### 方式1：命令行参数

```bash
# 使用开发环境
python main.py dev

# 使用展示环境
python main.py show

# 使用生产环境
python main.py prod
```

#### 方式2：环境变量

```bash
# Linux/Mac
export APP_ENV_TYPE=dev
python main.py

# Windows
set APP_ENV_TYPE=dev
python main.py
```

#### 方式3：IP 自动检测

系统会根据本机 IP 地址自动选择环境（需要在 `src/utils/ip_env_mapping.py` 中配置生产服务器 IP 列表）。

### 配置优先级

配置加载优先级（从高到低）：

1. **`.env`** - 本地覆盖配置（如果存在，不会被提交到版本控制）
2. **`env.{ENV}`** - 环境特定配置（env.dev, env.show, env.prod）
3. **系统环境变量** - 系统级环境变量

### 主要配置项

所有配置项都在 `env.template` 文件中有详细说明，主要包括：

- **应用配置**: `APP_ENV`, `APP_HOST`, `APP_PORT`
- **Milvus 配置**: `MILVUS_HOST`, `MILVUS_PORT`, `MILVUS_DATABASE`
- **模型 API 配置**: `MODEL_API_BASE_URL`, `MODEL_API_KEY`, `MODEL_NAME`
- **嵌入模型配置**: `EMBEDDING_API_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL_NAME`
- **Agno MySQL 配置**: `AGNO_MYSQL_HOST`, `AGNO_MYSQL_PORT`, `AGNO_MYSQL_USER`, `AGNO_MYSQL_PASSWORD`, `AGNO_MYSQL_DB_SCHEMA`
- **业务 MySQL 配置**: `BUSINESS_MYSQL_HOST`, `BUSINESS_MYSQL_PORT`, `BUSINESS_MYSQL_USER`, `BUSINESS_MYSQL_PASSWORD`, `BUSINESS_MYSQL_DATABASES`
- **日志配置**: `LOG_LEVEL`, `LOG_FILE`

**详细说明**：请参考 `env.template` 文件和 [环境配置详细说明](document/ENV_SETUP.md) 获取完整的环境配置说明。
