#!/usr/bin/env bash
# 潮汐循环 — 停止脚本
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/outputs/tidal/tidal.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚫ 潮汐未在运行"
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    echo "🌊 发送停止信号 (SIGTERM) → PID=$PID"
    kill -TERM "$PID"
    # 等待优雅退出
    for i in $(seq 1 30); do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "✅ 潮汐已停止"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done
    # 强制停止
    echo "⚠️  强制停止 (SIGKILL)"
    kill -KILL "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"
else
    echo "⚫ 进程已不存在, 清理PID文件"
    rm -f "$PID_FILE"
fi
