#!/bin/bash
# 停止服务脚本 - 停止 Agno Backend API Service

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# PID 文件路径
PID_FILE="$PROJECT_ROOT/.agno-backend.pid"

# 检查 PID 文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "未找到 PID 文件，尝试通过进程名查找..."
    
    # 通过进程名查找
    PIDS=$(pgrep -f "uvicorn src.main:app")
    
    if [ -z "$PIDS" ]; then
        echo "服务未运行"
        exit 0
    else
        echo "找到运行中的进程: $PIDS"
        for PID in $PIDS; do
            echo "正在停止进程 $PID..."
            kill "$PID" 2>/dev/null
        done
        
        # 等待进程结束
        sleep 2
        
        # 如果进程仍在运行，强制杀死
        for PID in $PIDS; do
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "强制停止进程 $PID..."
                kill -9 "$PID" 2>/dev/null
            fi
        done
        
        echo "✓ 服务已停止"
        exit 0
    fi
fi

# 读取 PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "进程 $PID 不存在，服务可能已经停止"
    rm -f "$PID_FILE"
    exit 0
fi

# 停止进程
echo "正在停止服务 (PID: $PID)..."
kill "$PID" 2>/dev/null

# 等待进程结束
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ 服务已停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 如果进程仍在运行，强制杀死
if ps -p "$PID" > /dev/null 2>&1; then
    echo "进程未响应，强制停止..."
    kill -9 "$PID" 2>/dev/null
    sleep 1
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ 服务已强制停止"
        rm -f "$PID_FILE"
        exit 0
    else
        echo "✗ 无法停止服务，请手动检查进程 $PID"
        exit 1
    fi
fi

rm -f "$PID_FILE"
echo "✓ 服务已停止"

