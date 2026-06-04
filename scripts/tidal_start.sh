#!/usr/bin/env bash
# 潮汐循环 — 启动脚本
# 用法: bash scripts/tidal_start.sh [--interval 3600] [--max-cycles 0]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_ROOT/outputs/tidal/tidal.pid"

INTERVAL="${INTERVAL:-3600}"
MAX_CYCLES="${MAX_CYCLES:-0}"
TASK_LIMIT="${TASK_LIMIT:-0}"
PRESETS="${PRESETS:-warm_vocal,clean_master,wide_space}"

mkdir -p "$PROJECT_ROOT/outputs/tidal"

# 已运行?
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "❌ 潮汐已在运行 (PID=$PID)"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

echo "🌊 启动 Moodify 潮汐循环"
echo "   间隔: ${INTERVAL}s (${INTERVAL} / 3600 = $(echo "scale=1; $INTERVAL/3600" | bc 2>/dev/null || echo '?')h)"
echo "   最大循环: ${MAX_CYCLES:-∞}"
echo "   每轮任务上限: ${TASK_LIMIT:-∞}"
echo "   预设: ${PRESETS}"
echo "   PID: $PID_FILE"
echo ""

nohup python3 -m moodify_runtime.tidal_cycle \
    --interval "$INTERVAL" \
    --max-cycles "$MAX_CYCLES" \
    --task-limit "$TASK_LIMIT" \
    --presets "$PRESETS" \
    > "$PROJECT_ROOT/outputs/tidal/tidal_stdout.log" 2>&1 &

echo "✅ 潮汐已启动 (PID=$!)"
echo "   bash scripts/tidal_status.sh  查看状态"
echo "   bash scripts/tidal_stop.sh    停止"
