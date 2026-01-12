# Agno 多智能体框架开发记录

## 项目概述

本项目基于 Agno 框架构建的多智能体开发脚手架，实现了 MySQL 与 Milvus 向量数据库的集成，通过外部工作流定义和内部团队协作模式，提供高自由度、可扩展的智能体开发平台。

## 架构设计

### 核心架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Agno Multi Agent Framework             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  外部接口   │  │  AgentOS    │  │    工作流引擎       │  │
│  │   Layer     │  │ Management │  │   Workflow Engine   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Team      │  │   Agent     │  │     Tools           │  │
│  │  协作层     │  │   智能体    │  │    工具层           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   MySQL     │  │   Milvus    │  │    模型服务         │  │
│  │  关系数据库 │  │ 向量数据库  │  │  Model Services     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

### 核心框架
- **Agno**: 多智能体框架核心，提供 AgentOS、工作流、团队协作等能力
- **FastAPI**: 高性能异步 Web 框架，提供 REST API 接口
- **AgentOS**: Agno 的操作系统层，提供智能体生命周期管理

### 数据存储
- **MySQL**: 关系型数据库，支持业务数据存储和 Agno 系统数据
- **Milvus**: 向量数据库，支持知识库和语义搜索

### AI 模型
- **DeepSeek**: 主要大语言模型 (DeepSeek v3.2-exp)
- **DashScope**: 嵌入模型服务 (text-embedding-v2)

## 模块架构

### 1. 数据库模块 (`src/database/`)

#### 连接管理
```python
# Agno 专用数据库连接 (session, memory, traces等)
from src.database.connection import get_agno_database, get_workflow_database

# 业务数据库连接 (多数据库支持)
from src.database.business_db import get_business_connection, list_business_databases
```

#### 查询工具
```python
# Agno 系统数据库查询
from src.database.query_tools import DatabaseQueryTools

# 业务数据库查询
from src.database.business_query_tools import get_business_query_tools
```

### 2. 向量数据库模块 (`src/vector/`)

#### 连接管理
```python
from src.vector.connection import get_milvus_client, create_milvus_client
```

#### 查询工具
```python
from src.vector.query_tools import get_vector_tools, VectorQueryTools
```

### 3. 工具层 (`src/engine/tools/`)

#### 数据库工具
- `list_databases_and_tables()`: 列出所有业务数据库及其表结构

#### 向量工具
- `list_collections()`: 列出知识库中的所有集合

### 4. 智能体层 (`src/engine/agents/`)

#### 核心智能体
- **Intent Agent**: 意图识别和任务规划，决定是否启用数据库查询和讨论团队
- **DB Agent**: 数据库查询执行，支持业务数据库和知识库查询
- **Output Agent**: 结果整合和输出，整合所有信息生成最终回复
- **Judge Agent**: 讨论团队评估器，评估讨论结果质量

#### 智能体创建模式
```python
from src.engine.agents import (
    create_intent_agent,
    create_db_agent,
    create_output_agent,
    create_discussion_judge,
)

# 创建智能体实例
intent_agent = create_intent_agent()
db_agent = create_db_agent()
output_agent = create_output_agent()
judge_agent = create_discussion_judge()
```

### 5. 工作流层 (`src/engine/workflows/`)

#### 主工作流架构
```python
def create_main_workflow() -> Workflow:
    workflow = Workflow(
        name="Main Workflow",
        description="意图识别 -> 数据库查询（可选）-> 讨论团队（可选）-> 整合输出",
        steps=[Step(name="main_workflow", executor=main_workflow_steps)],
        db=get_workflow_database(),
        add_workflow_history_to_steps=True,
    )
    return workflow
```

#### 工作流执行流程
1. **意图识别**: 分析用户输入，判断是否需要数据库查询和讨论团队
2. **数据库查询**: 根据意图执行相应的数据库操作 (可选)
3. **讨论团队**: 进行多轮讨论，形成深入的分析结果 (可选)
4. **结果整合**: 整合所有信息生成最终回复

### 6. AgentOS 管理系统 (`src/agentos/`)

#### AgentOS 初始化
```python
from src.agentos import create_agentos

agent_os = create_agentos(
    base_app=base_app,      # FastAPI 应用
    agents=[...],           # 智能体列表
    workflows=[...],        # 工作流列表
    teams=[],               # 团队列表 (预留)
    tracing=True            # 启用追踪
)
```

#### 自动注册机制
- 自动注册所有智能体 (Intent, DB, Output, Judge)
- 自动注册主工作流
- 自动注册讨论团队
- 支持通过环境变量控制追踪
- 自动配置知识库和数据库连接

### 7. 配置系统 (`src/utils/config_loader.py`)

#### 多环境支持
- **dev**: 开发环境
- **show**: 展示/预发布环境
- **prod**: 生产环境

#### 配置优先级
1. `.env` (本地覆盖配置)
2. `env.{ENV}` (环境特定配置)
3. 系统环境变量

#### IP 自动检测
支持根据服务器 IP 地址自动选择环境配置。

## 核心功能实现

### 1. 数据库集成

#### MySQL 多库架构
```python
# Agno 系统库 - 存储 session, memory, traces 等
AGNO_MYSQL_DB_SCHEMA=agno_backend

# 业务数据库 - 支持多数据库配置
BUSINESS_MYSQL_DATABASES=db1,db2,db3

# 知识库内容数据库 - 存储知识库元数据和内容
AGNO_KNOWLEDGE_TABLE=agno_knowledge
```

#### 连接池管理
```python
# 数据库连接池配置
MYSQL_POOL_SIZE=20
MYSQL_POOL_RECYCLE=3600
MYSQL_ECHO=false
```

#### 数据库分类
- **Agno 系统数据库**: 存储会话、记忆、追踪、评估等系统数据
- **业务数据库**: 存储业务数据，支持多数据库查询
- **知识库内容数据库**: 存储知识库的元数据和原始内容

### 2. 向量数据库集成

#### Milvus 连接配置
```python
# 向量数据库配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_DATABASE=default
MILVUS_USER=root          # 可选，如果启用认证
MILVUS_PASSWORD=password  # 可选，如果启用认证
MILVUS_DEFAULT_COLLECTION=agno_knowledge_default
MILVUS_DEFAULT_COLLECTION_DIMENSION=1536
```

#### 自动连接管理
- 连接失败时自动重试
- 数据库不存在时自动创建
- 集合不存在时自动创建（使用配置的维度）
- 支持认证配置
- 支持多数据库切换

### 3. 知识库集成 (`src/knowledge/`)

#### 知识库架构
采用双数据库架构：
- **Milvus**: 存储向量化的知识内容，支持相似度搜索
- **MySQL**: 存储知识库的元数据和原始内容

#### 嵌入模型配置
```python
from agno.knowledge.embedder.openai import OpenAIEmbedder

# 创建嵌入模型（支持 OpenAI 兼容 API）
embedder = OpenAIEmbedder(
    id="text-embedding-v2",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="your-api-key",
    dimensions=1536,  # 根据模型设置维度
)
```

#### 知识库创建
```python
from src.knowledge import create_knowledge

# 创建知识库实例
knowledge = create_knowledge()

# 在 Agent 中使用
agent = Agent(
    name="Knowledge Agent",
    knowledge=knowledge,
)
```

#### 配置说明
- 向量维度必须与嵌入模型匹配
- 支持多种嵌入模型（text-embedding-v2, text-embedding-3-small, text-embedding-3-large）
- 自动根据模型名称设置维度
- 支持自定义 API 端点（用于 DashScope、私有部署等）

### 4. 工具操作实现

#### 数据库查询工具 (`src/engine/tools/database_tools.py`)
- `list_databases_and_tables()`: 列出所有业务数据库及其表结构

#### 知识库查询工具 (`src/engine/tools/vector_tools.py`)
- `list_collections()`: 列出知识库中的所有集合
- `get_collection_info(collection_name)`: 获取指定集合的详细信息
- `search_knowledge(collection_name, query_text, limit)`: 在指定集合中搜索相似知识（需要嵌入模型支持）

#### 工具集成
```python
from src.engine.tools.database_tools import database_tools
from src.engine.tools.vector_tools import vector_tools_list

# 在 Agent 中使用工具
agent = Agent(
    name="DB Agent",
    tools=database_tools + vector_tools_list,
)
```

### 5. AgentOS 管理架构

#### 智能体生命周期
- **创建**: 通过工厂函数创建智能体实例
- **注册**: 自动注册到 AgentOS
- **执行**: 通过工作流编排执行
- **销毁**: 随应用关闭自动清理

#### 工作流管理
- **定义**: 通过 YAML 或代码定义工作流
- **执行**: 基于用户输入触发执行
- **追踪**: 支持完整的执行追踪和历史记录

### 6. 团队协作模式 (`src/engine/teams/`)

> 以一个简单的正反辩论团队为例。

#### 讨论团队实现
实现了完整的讨论团队功能，支持多轮讨论和自动评估控制。

**团队成员**：
- **Pro Agent**: 正方角色，支持用户观点，寻找证据和理论支持
- **Con Agent**: 反方角色，进行批判性思考，提出质疑和辩驳
- **Leader Agent**: 领导角色，把控方向，协调讨论节奏，不参与具体讨论

**讨论流程**：
1. 根据用户问题和上下文进行讨论
2. 每轮讨论后进行评估
3. 如果评估分数达到阈值或达到最大轮次，停止讨论
4. 返回讨论结果和评估信息

**配置参数**：
- `DISCUSSION_MAX_ROUNDS`: 最大讨论轮次（默认3轮）
- `DISCUSSION_SCORE_THRESHOLD`: 评估分数阈值（默认7.0）

```python
from src.engine.teams import create_discussion_team

# 创建讨论团队
discussion_team = create_discussion_team(
    max_rounds=3,           # 最大轮次
    score_threshold=7.0,    # 分数阈值
)

# 执行讨论
result = await discussion_team.run(
    user_query="如何看待人工智能的发展？",
    context="数据查询结果：..."
)

# 返回结果包含：
# - discussion_result: 讨论结果内容
# - evaluation_result: 评估结果
# - final_score: 最终评估分数
# - total_rounds: 总讨论轮次
# - reached_threshold: 是否达到阈值
```

#### 评估系统
使用 `AgentAsJudgeEval` 实现讨论质量评估：
- 使用 `numeric` 评分策略（0-10分）
- 可配置评估标准和阈值
- 自动判断是否达到目标分数

#### 扩展性设计
- 支持动态添加新的智能体
- 支持自定义团队配置
- 支持工作流间的依赖关系
- 支持自定义评估标准和阈值

## Agno 特性利用

### 1. 内存管理系统
```python
# 自动管理会话记忆
AGNO_MEMORY_TABLE=agno_tags_memories

# 支持长期记忆和短期记忆
# 智能体可访问历史对话记录
```

### 2. 追踪系统
```python
# 完整的执行追踪
AGNO_TRACES_TABLE=agno_tags_traces
AGNO_SPANS_TABLE=agno_tags_spans

# 支持性能监控和调试
AGENTOS_TRACING=true
```

### 3. 评估系统
```python
# 智能体性能评估
AGNO_EVAL_TABLE=agno_tags_evaluations

# 支持自动化评估和反馈
```

### 4. 工具集成
```python
# 基于装饰器的工具定义
@tool
def custom_database_query(sql: str) -> str:
    """自定义数据库查询工具"""
    # 实现具体的查询逻辑
    pass
```

## 扩展性设计

### 1. 配置驱动开发

#### YAML 配置系统
```yaml
# config/agents.yaml
agents:
  - name: "custom_agent"
    type: "CustomAgent"
    model: "deepseek-v3.2-exp"
    tools: ["database_tools", "vector_tools"]
    instructions: "自定义指令"

# config/workflows.yaml
workflows:
  - name: "custom_workflow"
    steps:
      - name: "step1"
        agent: "custom_agent"
      - name: "step2"
        agent: "another_agent"
```

#### 动态加载机制
```python
# 支持运行时动态加载配置
from src.utils.yaml_agent_loader import load_agents_from_yaml

agents = load_agents_from_yaml("config/agents.yaml")
workflows = load_workflows_from_yaml("config/workflows.yaml")
```

### 2. 插件化架构

#### 工具插件
```python
# tools/custom_tools.py
from agno.tools import tool

@tool
def custom_business_logic(param: str) -> str:
    """自定义业务逻辑工具"""
    # 实现具体业务逻辑
    return result

# 在配置中注册
database_tools.append(custom_business_logic)
```

#### 智能体插件
```python
# agents/custom_agent.py
from agno.agent import Agent

class CustomAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Custom Agent",
            model=get_model_config(),
            tools=[custom_business_logic],
            instructions="自定义智能体指令"
        )
```

### 3. API 扩展

#### REST API 接口
```python
# src/api/router.py
@api_router.post("/custom/endpoint")
async def custom_endpoint(request: CustomRequest):
    """自定义 API 端点"""
    # 调用工作流或智能体
    result = await agent_os.run_workflow("custom_workflow", request.data)
    return result
```

#### WebSocket 支持 (预留)
```python
# 支持实时通信
# 可扩展为实时智能体交互
```

## 开发模式

### 1. 快速启动

#### 环境配置脚本
```bash
# Linux/Mac 环境
./bin/setup_conda_env.sh

# Windows 环境 (推荐)
.\bin\setup_conda_env.bat

# Windows Git Bash/WSL
./bin/setup_conda_env.sh

# 功能：
# - 创建 agno_multi_agent_play conda 环境
# - 配置 Python 3.12
# - 自动安装所有依赖包
# - 验证环境配置
```

#### 服务管理脚本
```bash
# Linux 服务管理
./bin/start.sh    # 启动服务
./bin/stop.sh     # 停止服务
./bin/status.sh   # 查看状态

# 开发模式启动
python start.py dev --reload
```

#### 环境配置
```bash
# 自动创建环境配置文件
python scripts/create_env_files.py

# 或者手动创建
cp env.template env.dev
# 编辑 env.dev 设置实际配置

# 主要配置项：
# - MySQL 数据库配置（Agno系统库、业务库、知识库内容库）
# - Milvus 向量数据库配置
# - 模型 API 配置（DeepSeek、DashScope）
# - 讨论团队配置（最大轮次、评估阈值）
# - AgentOS 配置（追踪开关等）
```

### 2. 开发工作流

#### 1. 定义工具
```python
# src/engine/tools/custom_tools.py
@tool
def my_custom_tool(param: str) -> str:
    """我的自定义工具"""
    return f"处理结果: {param}"
```

#### 2. 创建智能体
```python
# src/engine/agents/custom_agent.py
def create_custom_agent() -> Agent:
    return Agent(
        name="Custom Agent",
        model=get_model_config(),
        tools=[my_custom_tool],
        instructions="执行自定义任务"
    )
```

#### 3. 定义工作流
```python
# src/engine/workflows/custom_workflow.py
def create_custom_workflow() -> Workflow:
    return Workflow(
        name="Custom Workflow",
        steps=[Step(name="custom_step", executor=custom_steps)],
        db=get_workflow_database()
    )
```

#### 4. 注册到系统
```python
# src/agentos/__init__.py
# 自动发现和注册新的组件
# 或者手动添加
kwargs['agents'].append(create_custom_agent())
kwargs['workflows'].append(create_custom_workflow())
```

### 3. 测试驱动开发

#### 单元测试
```python
# tests/test_custom_agent.py
def test_custom_agent():
    agent = create_custom_agent()
    result = agent.run("测试输入")
    assert "期望结果" in result.content
```

#### 集成测试
```python
# tests/test_workflow_integration.py
def test_main_workflow():
    workflow = create_main_workflow()
    result = workflow.run("用户查询")
    assert result is not None
```

## 部署架构

### 1. 容器化部署

#### Dockerfile
```dockerfile
FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 启动命令
CMD ["python", "start.py", "prod"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  agno-app:
    build: .
    ports:
      - "8564:8564"
    environment:
      - APP_ENV_TYPE=prod
    depends_on:
      - mysql
      - milvus
      - etcd
    volumes:
      - ./logs:/app/logs

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: agno_backend

  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"
      - "9091:9091"
```

### 2. 生产环境配置

#### 环境变量
```bash
# 生产环境配置
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8564

# 数据库配置
AGNO_MYSQL_HOST=prod-db-host
BUSINESS_MYSQL_HOST=prod-db-host
MILVUS_HOST=prod-milvus-host

# 模型服务
MODEL_API_KEY=prod_model_key
EMBEDDING_API_KEY=prod_embedding_key

# 安全配置
API_SECRET_KEY=prod_secret_key
```

#### 监控和日志
```python
# 结构化日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/agno.log

# 性能监控集成
# 支持 Prometheus metrics
# 支持健康检查端点
```

## 项目优势

### 1. 框架特性
- **多智能体协作**: 支持复杂任务的智能体分工协作
- **工作流编排**: 灵活的工作流定义和执行引擎
- **内存管理**: 自动化的会话和记忆管理
- **追踪系统**: 完整的执行追踪和性能监控

### 2. 架构优势
- **模块化设计**: 高内聚、低耦合的模块架构
- **配置驱动**: 支持多种配置方式和环境管理
- **扩展性强**: 插件化架构支持快速功能扩展
- **生产就绪**: 完整的部署和监控方案

### 3. 开发体验
- **快速启动**: 一键启动开发环境
- **热重载**: 开发模式支持代码热重载
- **测试完善**: 完整的测试套件和 CI/CD 支持
- **文档齐全**: 详细的开发文档和使用指南

## 未来规划

### 1. 功能扩展
- [ ] 支持更多向量数据库 (Pinecone, Weaviate)
- [ ] 集成更多 AI 模型 (Claude, GPT-4)
- [ ] 添加实时通信支持 (WebSocket)
- [ ] 实现智能体市场 (Agent Marketplace)

### 2. 性能优化
- [ ] 实现智能体缓存机制
- [ ] 优化数据库查询性能
- [ ] 添加负载均衡支持
- [ ] 实现水平扩展架构

### 3. 企业级特性
- [ ] 用户权限管理系统
- [ ] 多租户架构支持
- [ ] 审计日志系统
- [ ] 企业级安全加固

## 最新功能更新

### 讨论团队功能
- ✅ 实现了完整的讨论团队（Discussion Team），包含正方、反方和领导角色
- ✅ 支持多轮讨论和自动评估控制
- ✅ 集成 Agent-as-Judge 评估系统
- ✅ 可配置的最大轮次和评估阈值

### 知识库功能
- ✅ 完整的 Milvus + MySQL 知识库集成
- ✅ 支持自定义嵌入模型（OpenAI 兼容 API）
- ✅ 自动创建集合和数据库
- ✅ 向量搜索和内容存储功能

### 工作流增强
- ✅ 工作流支持条件执行（数据库查询和讨论团队可选）
- ✅ 意图识别智能体决定是否启用各个组件
- ✅ 完整的信息传递和整合流程

## 总结

本项目基于 Agno 框架构建了一个功能完整、架构清晰的多智能体开发脚手架。通过精心设计的模块架构和配置系统，实现了 MySQL 与 Milvus 的无缝集成，为开发者提供了高自由度、可扩展的智能体开发平台。

项目充分利用了 Agno 的核心特性，包括 AgentOS 管理系统、工作流引擎、团队协作、内存管理、追踪系统、评估系统等，同时保持了高度的扩展性和生产就绪性，是一个理想的智能体应用开发起点。

主要特性：
- ✅ 完整的多智能体协作架构
- ✅ 灵活的工作流编排系统
- ✅ 讨论团队和评估系统
- ✅ 知识库集成（向量搜索 + 内容存储）
- ✅ 数据库和知识库查询工具
- ✅ 环境配置管理和自动部署



> LMQH - 2026年1月12日
