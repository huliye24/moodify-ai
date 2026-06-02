#!/usr/bin/env bash
# ===========================================================================
# Moodify Night Worker — 后台启动脚本
#
# 用法:
#   bash scripts/run_night.sh
#   bash scripts/run_night.sh --config configs/night_jobs.yaml
# ===========================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKER_SCRIPT="$PROJECT_ROOT/workers/night_worker.py"
PID_FILE="$PROJECT_ROOT/runs/night_auto/night_worker.pid"
LOG_DIR="$PROJECT_ROOT/runs/night_auto/logs"

# 创建目录
mkdir -p "$LOG_DIR"

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "错误: Night Worker 已在运行 (PID=$PID)"
        echo "      使用 scripts/stop_night.sh 停止, 或 scripts/monitor_night.sh 查看"
        exit 1
    else
        echo "清理过期的 PID 文件..."
        rm -f "$PID_FILE"
    fi
fi

# 激活虚拟环境 (如果存在)
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "已激活虚拟环境: $PROJECT_ROOT/.venv"
fi

# 启动
CONFIG="${1:-configs/night_jobs.yaml}"
echo "Moodify Night Worker 启动中..."
echo "  配置: $CONFIG"
echo "  日志: $LOG_DIR/night_worker.log"
echo "  PID:  $PID_FILE"

nohup python "$WORKER_SCRIPT" \
    --config "$CONFIG" \
    > "$LOG_DIR/night_worker.log" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
echo ""
echo "============================================"
echo "  Moodify Night Worker 已启动"
echo "============================================"
echo "  PID:  $PID"
echo "  PID文件: $PID_FILE"
echo "  日志: $LOG_DIR/night_worker.log"
echo ""
echo "监控: bash scripts/monitor_night.sh"
echo "停止: bash scripts/stop_night.sh"
echo "============================================"
