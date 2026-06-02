#!/usr/bin/env bash
# ===========================================================================
# Moodify Night Worker — 安全停止脚本
#
# 用法:
#   bash scripts/stop_night.sh          # 优雅停止 (SIGTERM)
#   bash scripts/stop_night.sh --force  # 强制停止 (SIGKILL)
# ===========================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_ROOT/runs/night_auto/night_worker.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo "未找到 PID 文件 ($PID_FILE), Night Worker 可能未在运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "进程 $PID 已不存在, 清理 PID 文件"
    rm -f "$PID_FILE"
    exit 0
fi

FORCE="${1:-}"

if [ "$FORCE" = "--force" ] || [ "$FORCE" = "-f" ]; then
    echo -e "${RED}强制停止 Night Worker (PID=$PID)...${NC}"
    kill -9 "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "已强制停止"
else
    echo "优雅停止 Night Worker (PID=$PID)..."
    echo "  发送 SIGTERM, 等待当前 job 完成..."

    kill "$PID" 2>/dev/null || true

    # 等待最多 30 秒
    for i in $(seq 1 30); do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}Night Worker 已安全停止${NC}"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
        echo -n "."
    done
    echo ""

    # 超时 -> 强制
    echo -e "${YELLOW}超时, 发送 SIGKILL...${NC}"
    kill -9 "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "已强制停止"
fi

echo ""
echo "下次运行时将自动从 checkpoint 续跑"
echo "查看报告: ls $PROJECT_ROOT/runs/night_auto/reports/"
