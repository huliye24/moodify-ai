#!/usr/bin/env bash
# ===========================================================================
# Moodify Day Run 24h — 无人值守 24 小时自运行系统
#
# 用法:
#   nohup bash scripts/day_run_24h.sh [config] [run_name] [hours] [sleep_s] &
#
# 默认:
#   config=configs/runtime_config.json
#   run_name=day_run_001
#   hours=24
#   sleep_s=600  (每轮之间休息 10 分钟)
#
# 每轮执行:
#   register → plan → run → report → craft → next
#
# 结束后:
#   自动生成 logs/<run_name>_final_summary.txt
# ===========================================================================
set -euo pipefail

CONFIG="${1:-configs/runtime_config.json}"
RUN_NAME="${2:-day_run_001}"
DURATION_HOURS="${3:-24}"
SLEEP_SECONDS="${4:-600}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="${ROOT_DIR}:${ROOT_DIR}/moodify-core-package/src:${PYTHONPATH:-}"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

mkdir -p logs

START_TS="$(date +%s)"
END_TS="$((START_TS + DURATION_HOURS * 3600))"
LOG_FILE="logs/${RUN_NAME}_$(date +%Y%m%d_%H%M%S).log"
SUMMARY_FILE="logs/${RUN_NAME}_final_summary.txt"

ROUND=0
TOTAL_BEFORE="$(find outputs/daily_runs -maxdepth 1 -type d 2>/dev/null | wc -l || true)"

{
  echo "============================================================"
  echo " Moodify Day Run 24h — ${RUN_NAME}"
  echo "============================================================"
  echo "start_time  = $(date '+%F %T')"
  echo "duration    = ${DURATION_HOURS}h"
  echo "sleep       = ${SLEEP_SECONDS}s between rounds"
  echo "config      = ${CONFIG}"
  echo "root        = ${ROOT_DIR}"
  echo "pid         = $$"
  echo "log_file    = ${LOG_FILE}"
  echo "summary     = ${SUMMARY_FILE}"
  echo ""
} | tee "$SUMMARY_FILE" > "$LOG_FILE"

while [ "$(date +%s)" -lt "$END_TS" ]; do
  ROUND=$((ROUND + 1))

  {
    echo ""
    echo "===== ROUND ${ROUND} $(date '+%F %T') ====="
    echo ""
    echo "--- system ---"
    echo "uptime: $(uptime)"
    echo "memory: $(free -h | head -2 | tail -1)"
    echo "disk:   $(df -h . | tail -1)"
    echo "outputs: $(du -sh outputs data logs 2>/dev/null | paste -s - || true)"
    echo ""
    echo "--- register ---"
  } >> "$LOG_FILE" 2>&1

  python3 -m moodify_runtime.cli --config "$CONFIG" register --source "$RUN_NAME" >> "$LOG_FILE" 2>&1 || true

  echo "--- plan ---" >> "$LOG_FILE"
  python3 -m moodify_runtime.cli --config "$CONFIG" plan >> "$LOG_FILE" 2>&1 || true

  echo "--- queue size ---" >> "$LOG_FILE"
  wc -l data/moodify_runtime/run_queue.jsonl >> "$LOG_FILE" 2>&1 || true

  echo "--- run ---" >> "$LOG_FILE"
  python3 -m moodify_runtime.cli --config "$CONFIG" run >> "$LOG_FILE" 2>&1 || true

  echo "--- report ---" >> "$LOG_FILE"
  python3 -m moodify_runtime.cli --config "$CONFIG" report >> "$LOG_FILE" 2>&1 || true

  echo "--- craft ---" >> "$LOG_FILE"
  python3 -m moodify_runtime.cli --config "$CONFIG" craft >> "$LOG_FILE" 2>&1 || true

  echo "--- next ---" >> "$LOG_FILE"
  python3 -m moodify_runtime.cli --config "$CONFIG" next >> "$LOG_FILE" 2>&1 || true

  {
    echo "ROUND ${ROUND} DONE $(date '+%F %T')"
    echo "sleep ${SLEEP_SECONDS}s..."
  } >> "$LOG_FILE"

  sleep "$SLEEP_SECONDS"
done

# ===========================================================================
# Final summary
# ===========================================================================
TOTAL_AFTER="$(find outputs/daily_runs -maxdepth 1 -type d 2>/dev/null | wc -l || true)"
REPORT_COUNT="$(find reports/daily_runs -type f -name '*.md' 2>/dev/null | wc -l || true)"
CRAFT_COUNT="$(find data/moodify_runtime/craft_memory -type f -name '*.md' 2>/dev/null | wc -l || true)"
LATEST_OUTPUTS="$(ls -lt outputs/daily_runs 2>/dev/null | head -5 || true)"
LATEST_REPORTS="$(ls -lt reports/daily_runs 2>/dev/null | head -5 || true)"

{
  echo ""
  echo "============================================================"
  echo " ${RUN_NAME} — FINAL SUMMARY"
  echo "============================================================"
  echo "finish_time       = $(date '+%F %T')"
  echo "total_rounds      = ${ROUND}"
  echo "daily_run_dirs    = ${TOTAL_BEFORE} → ${TOTAL_AFTER}"
  echo "reports           = ${REPORT_COUNT}"
  echo "craft_memories    = ${CRAFT_COUNT}"
  echo ""
  echo "--- disk ---"
  df -h .
  echo ""
  echo "--- size ---"
  du -sh outputs data logs reports 2>/dev/null || true
  echo ""
  echo "--- latest outputs ---"
  echo "${LATEST_OUTPUTS}"
  echo ""
  echo "--- latest reports ---"
  echo "${LATEST_REPORTS}"
  echo ""
  echo "log_file = ${LOG_FILE}"
  echo "============================================================"
} | tee "$SUMMARY_FILE" >> "$LOG_FILE"

echo "DONE $(date '+%F %T')" >> "$LOG_FILE"
