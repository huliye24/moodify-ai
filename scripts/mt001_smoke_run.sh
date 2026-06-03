#!/usr/bin/env bash
# MT-001 Gate 1/2 smoke runner: register -> plan -> run -> report -> craft -> next.
set -euo pipefail

CONFIG="${1:-configs/mt001_runtime_smoke.json}"
RUN_ID="${2:-mt001_smoke_$(date +%Y%m%d_%H%M%S)}"
FRESH="${MT001_FRESH:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="${ROOT_DIR}:${ROOT_DIR}/moodify-core-package/src:${PYTHONPATH:-}"
mkdir -p logs
LOG_FILE="logs/${RUN_ID}.log"
SUMMARY_FILE="logs/mt001_smoke_final_summary.txt"

if [ "$FRESH" = "1" ]; then
  rm -rf data/moodify_runtime_mt001
  rm -rf "outputs/mt001_smoke/${RUN_ID}"
  rm -f "reports/mt001_smoke/daily_report_${RUN_ID}.md"
  rm -f "reports/mt001_smoke/daily_report_${RUN_ID}.json"
fi

{
  echo "============================================================"
  echo " MT-001 Runtime Smoke ? ${RUN_ID}"
  echo "============================================================"
  echo "started_at = $(date -Iseconds)"
  echo "root       = ${ROOT_DIR}"
  echo "config     = ${CONFIG}"
  echo "log_file   = ${LOG_FILE}"
  echo "fresh      = ${FRESH}"
  echo ""
} | tee "$SUMMARY_FILE" > "$LOG_FILE"

run_step() {
  local name="$1"
  shift
  {
    echo ""
    echo "--- ${name} $(date -Iseconds) ---"
    "$@"
  } >> "$LOG_FILE" 2>&1
}

run_step system bash -lc "uptime; free -h; df -h .; .venv/bin/python --version; ffmpeg -version | head -n 1"
run_step register .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" register --source mt001_smoke --notes "MT-001 Gate 1 baseline fixture"
run_step plan .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" plan --reason mt001_gate1
run_step run .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" run --run-id "$RUN_ID"
run_step report .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" report --run-id "$RUN_ID"
run_step craft .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" craft --run-id "$RUN_ID"
run_step failures .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" failures --run-id "$RUN_ID"
run_step next .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" next --run-id "$RUN_ID"

SUMMARY_JSON="outputs/mt001_smoke/${RUN_ID}/summary.json"
MANIFEST="outputs/mt001_smoke/${RUN_ID}/manifest.csv"
REPORT="reports/mt001_smoke/daily_report_${RUN_ID}.md"

.venv/bin/python - <<PY >> "$LOG_FILE"
import json
from pathlib import Path
summary_path = Path("$SUMMARY_JSON")
summary = json.loads(summary_path.read_text(encoding="utf-8"))
success = int(summary.get("success", 0))
failed = int(summary.get("failed", 0))
selected = int(summary.get("total_selected", 0))
print(f"MT001_RESULT selected={selected} success={success} failed={failed}")
if selected != 9 or success != 9 or failed != 0:
    raise SystemExit(2)
PY

{
  echo "finished_at = $(date -Iseconds)"
  echo "result      = PASS"
  echo "summary     = ${SUMMARY_JSON}"
  echo "manifest    = ${MANIFEST}"
  echo "report      = ${REPORT}"
  echo "log_file    = ${LOG_FILE}"
} | tee -a "$SUMMARY_FILE" >> "$LOG_FILE"

echo "MT-001 smoke PASS: ${RUN_ID}"
