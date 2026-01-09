#!/bin/bash
# 检查服务状态脚本 - 查看 Agno Backend API Service 运行状态

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# PID 文件路径
PID_FILE="$PROJECT_ROOT/.agno-backend.pid"

echo "=========================================="
echo "Agno Backend API Service 状态检查"
echo "=========================================="
echo ""

# 检查 PID 文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "PID 文件: $PID_FILE"
    echo "记录的 PID: $PID"
    echo ""
    
    # 检查进程是否存在
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ 服务正在运行"
        echo ""
        
        # 显示进程详细信息
        echo "进程信息:"
        ps -p "$PID" -o pid,ppid,user,%cpu,%mem,etime,cmd --no-headers | awk '{
            printf "  PID: %s\n", $1
            printf "  父进程 PID: %s\n", $2
            printf "  用户: %s\n", $3
            printf "  CPU 使用率: %s\n", $4
            printf "  内存使用率: %s\n", $5
            printf "  运行时间: %s\n", $6
        }'
        echo ""
        
        # 检查端口占用（从环境变量或默认值）
        PORT=$(grep -E '^APP_PORT=' "$PROJECT_ROOT/.env" 2>/dev/null | cut -d '=' -f2 || echo '8000')
        HOST=$(grep -E '^APP_HOST=' "$PROJECT_ROOT/.env" 2>/dev/null | cut -d '=' -f2 || echo '0.0.0.0')
        
        echo "网络信息:"
        if command -v netstat &> /dev/null; then
            NETSTAT=$(netstat -tlnp 2>/dev/null | grep ":$PORT " || echo "")
            if [ -n "$NETSTAT" ]; then
                echo "  端口 $PORT 正在监听"
                echo "  $NETSTAT"
            else
                echo "  端口 $PORT 未监听"
            fi
        elif command -v ss &> /dev/null; then
            SS_OUTPUT=$(ss -tlnp 2>/dev/null | grep ":$PORT " || echo "")
            if [ -n "$SS_OUTPUT" ]; then
                echo "  端口 $PORT 正在监听"
                echo "  $SS_OUTPUT"
            else
                echo "  端口 $PORT 未监听"
            fi
        else
            echo "  无法检查端口状态（需要 netstat 或 ss 命令）"
        fi
        echo ""
        
        # 尝试健康检查
        echo "健康检查:"
        if command -v curl &> /dev/null; then
            HEALTH_URL="http://localhost:$PORT/health"
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$HEALTH_URL" 2>/dev/null)
            if [ "$HTTP_CODE" = "200" ]; then
                echo "  ✓ HTTP 健康检查通过 (状态码: $HTTP_CODE)"
                # 获取健康检查响应
                HEALTH_RESPONSE=$(curl -s --connect-timeout 2 "$HEALTH_URL" 2>/dev/null)
                if [ -n "$HEALTH_RESPONSE" ]; then
                    echo "  响应: $HEALTH_RESPONSE"
                fi
            else
                echo "  ✗ HTTP 健康检查失败 (状态码: $HTTP_CODE)"
            fi
        else
            echo "  跳过 HTTP 健康检查（需要 curl 命令）"
        fi
        
    else
        echo "✗ 服务未运行（PID 文件存在但进程不存在）"
        echo ""
        echo "建议: 删除旧的 PID 文件"
        echo "  rm -f $PID_FILE"
    fi
else
    echo "未找到 PID 文件: $PID_FILE"
    echo ""
    
    # 尝试通过进程名查找
    PIDS=$(pgrep -f "uvicorn src.main:app")
    
    if [ -z "$PIDS" ]; then
        echo "✗ 服务未运行"
    else
        echo "发现运行中的进程（但未找到 PID 文件）:"
        for PID in $PIDS; do
            echo "  PID: $PID"
            ps -p "$PID" -o user,%cpu,%mem,etime,cmd --no-headers | awk '{
                printf "    用户: %s, CPU: %s, 内存: %s, 运行时间: %s\n", $1, $2, $3, $4
            }'
        done
        echo ""
        echo "建议: 使用 ./bin/stop.sh 停止服务，然后重新启动"
    fi
fi

echo ""
echo "=========================================="
echo "日志文件位置:"
echo "  应用日志: $PROJECT_ROOT/logs/app.log"
echo "  错误日志: $PROJECT_ROOT/logs/error.log"
echo "=========================================="

