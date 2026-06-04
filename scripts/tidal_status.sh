#!/usr/bin/env bash
# 潮汐循环 — 状态查看
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/outputs/tidal/tidal.pid"
HB_FILE="$PROJECT_ROOT/outputs/tidal/tidal_heartbeat.json"
EVENTS_FILE="$PROJECT_ROOT/outputs/tidal/tidal_events.jsonl"

echo "🌊 Moodify 潮汐循环 — 状态"
echo ""

# 进程
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        ELAPSED=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')
        echo "  状态: 🟢 运行中 (PID=$PID, 运行=$ELAPSED)"
    else
        echo "  状态: 🔴 已停止 (PID文件残留)"
    fi
else
    echo "  状态: ⚫ 未启动"
fi

# 心跳
if [ -f "$HB_FILE" ]; then
    echo ""
    echo "── 最后心跳 ──"
    python3 -c "
import json
d=json.load(open('$HB_FILE'))
print(f\"  时间: {d['timestamp']}\")
print(f\"  周期: {d['cycle']}\")
print(f\"  任务: {d['total_succeeded']}成功 / {d['total_failed']}失败\")
print(f\"  磁盘: {d['free_disk_gb']}GB / 内存: {d['free_mem_gb']}GB\")
" 2>/dev/null || echo "  (心跳读取失败)"
fi

# 最近事件
if [ -f "$EVENTS_FILE" ]; then
    echo ""
    echo "── 最近事件 ──"
    tail -5 "$EVENTS_FILE" 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d=json.loads(line.strip())
        print(f\"  [{d.get('event_type','?')}] {d.get('message','')[:80]}\")
    except: pass
" 2>/dev/null || echo "  (事件解析失败)"
fi

# 磁盘
echo ""
echo "── 磁盘 ──"
df -h "$PROJECT_ROOT/outputs" 2>/dev/null | tail -1 | awk '{print "  " $4 " 可用 / " $2 " 总量"}'
