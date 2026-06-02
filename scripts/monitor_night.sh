#!/usr/bin/env bash
# ===========================================================================
# Moodify Night Worker — 监控脚本
#
# 用法:
#   bash scripts/monitor_night.sh          # 查看一次状态
#   bash scripts/monitor_night.sh --watch  # 每 5 秒刷新
#   bash scripts/monitor_night.sh --tail   # 跟踪日志
# ===========================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_ROOT/runs/night_auto/night_worker.pid"
LOG_FILE="$PROJECT_ROOT/runs/night_auto/logs/night_worker.log"
CHECKPOINT_DIR="$PROJECT_ROOT/runs/night_auto/checkpoints"
RUN_DIR="$PROJECT_ROOT/runs/night_auto"
RUN_NAME="$(grep -o '"run_name": "[^"]*"' "$CHECKPOINT_DIR/stage_status.json" 2>/dev/null | head -1 | cut -d'"' -f4 || echo "?")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── 状态 ────────────────────────────────────────

print_status() {
    clear 2>/dev/null || true
    echo "╔══════════════════════════════════════════════╗"
    echo "║   Moodify Night Worker — 运行状态            ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""

    # 进程状态
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "  进程: ${GREEN}运行中${NC} (PID=$PID)"
            # 运行时长
            ELAPSED=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')
            echo "  运行时间: $ELAPSED"
        else
            echo -e "  进程: ${RED}已退出${NC} (PID 文件存在但进程不存在)"
        fi
    else
        echo -e "  进程: ${YELLOW}未启动${NC}"
    fi

    echo "  运行名: $RUN_NAME"
    echo ""

    # 阶段状态
    echo "── 阶段 ──────────────────────────────────────"
    STAGES="scan analyze sweep score bench report"
    for stage in $STAGES; do
        STATUS="未开始"
        COLOR="$YELLOW"
        if [ -f "$CHECKPOINT_DIR/stage_status.json" ]; then
            ST=$(python3 -c "
import json
try:
    d = json.load(open('$CHECKPOINT_DIR/stage_status.json'))
    print(d.get('$stage', {}).get('status', 'not_started'))
except: print('not_started')
" 2>/dev/null)
            case "$ST" in
                completed) STATUS="已完成"; COLOR="$GREEN" ;;
                in_progress) STATUS="进行中"; COLOR="$GREEN" ;;
                *) STATUS="$ST"; COLOR="$YELLOW" ;;
            esac
        fi
        printf "    %-10s ${COLOR}%s${NC}\n" "$stage:" "$STATUS"
    done

    echo ""

    # 统计
    echo "── 统计 ──────────────────────────────────────"
    if [ -f "$CHECKPOINT_DIR/analyzed_files.json" ]; then
        ANALYZED=$(python3 -c "import json; d=json.load(open('$CHECKPOINT_DIR/analyzed_files.json')); print(len(d))" 2>/dev/null || echo "?")
    else
        ANALYZED="0"
    fi
    if [ -f "$CHECKPOINT_DIR/processed_versions.json" ]; then
        PROCESSED=$(python3 -c "
import json
d = json.load(open('$CHECKPOINT_DIR/processed_versions.json'))
total = sum(len(v) for v in d.values())
print(total)
" 2>/dev/null || echo "?")
    else
        PROCESSED="0"
    fi
    if [ -f "$CHECKPOINT_DIR/failed_jobs.json" ]; then
        FAILED=$(python3 -c "import json; d=json.load(open('$CHECKPOINT_DIR/failed_jobs.json')); print(len(d))" 2>/dev/null || echo "?")
    else
        FAILED="0"
    fi
    echo "  已分析音频: $ANALYZED"
    echo "  已处理版本: $PROCESSED"
    echo "  失败: $FAILED"

    echo ""

    # 磁盘
    echo "── 磁盘 ──────────────────────────────────────"
    if [ -d "$RUN_DIR" ]; then
        du -sh "$RUN_DIR" 2>/dev/null | awk '{print "  运行目录: " $0}'
    fi
    df -h / | tail -1 | awk '{print "  系统剩余: " $4}'

    echo ""

    # 日志尾部
    echo "── 最近日志 ──────────────────────────────────"
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE" 2>/dev/null
    else
        echo "  (日志文件尚未生成)"
    fi

    echo ""
    echo "──────────────────────────────────────────────"
    echo "  bash scripts/monitor_night.sh --watch  刷新"
    echo "  bash scripts/monitor_night.sh --tail   日志"
    echo "  bash scripts/stop_night.sh             停止"
    echo "──────────────────────────────────────────────"
}

# ── 主逻辑 ──────────────────────────────────────

case "${1:-}" in
    --watch|-w)
        while true; do
            print_status
            sleep 5
        done
        ;;
    --tail|-t)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "日志文件不存在: $LOG_FILE"
            exit 1
        fi
        ;;
    *)
        print_status
        ;;
esac
