#!/bin/bash
# 启动服务脚本 - 后台运行 Agno Backend API Service

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录
cd "$PROJECT_ROOT" || exit 1

# PID 文件路径
PID_FILE="$PROJECT_ROOT/.agno-backend.pid"
LOG_FILE="$PROJECT_ROOT/logs/app.log"
ERROR_LOG_FILE="$PROJECT_ROOT/logs/error.log"

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

# 检查服务是否已经在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "服务已经在运行中 (PID: $OLD_PID)"
        echo "如果服务未正常响应，请先运行 ./bin/stop.sh 停止服务"
        exit 1
    else
        # PID 文件存在但进程不存在，删除旧的 PID 文件
        rm -f "$PID_FILE"
    fi
fi

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3 命令"
    exit 1
fi

# 检查虚拟环境（如果存在）
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# 启动服务（后台运行）
echo "正在启动 Agno Backend API Service..."
nohup python3 -m uvicorn src.main:app \
    --host "$(grep -E '^APP_HOST=' .env 2>/dev/null | cut -d '=' -f2 || echo '0.0.0.0')" \
    --port "$(grep -E '^APP_PORT=' .env 2>/dev/null | cut -d '=' -f2 || echo '8000')" \
    --log-level info \
    > "$LOG_FILE" 2> "$ERROR_LOG_FILE" &

# 保存 PID
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# 等待一下，检查进程是否成功启动
sleep 2

if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✓ 服务启动成功"
    echo "  PID: $NEW_PID"
    echo "  日志文件: $LOG_FILE"
    echo "  错误日志: $ERROR_LOG_FILE"
    echo "  PID 文件: $PID_FILE"
    echo ""
    echo "使用以下命令查看服务状态:"
    echo "  ./bin/status.sh"
    echo ""
    echo "使用以下命令停止服务:"
    echo "  ./bin/stop.sh"
else
    echo "✗ 服务启动失败，请检查错误日志: $ERROR_LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

