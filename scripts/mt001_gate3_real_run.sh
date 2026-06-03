#!/usr/bin/env bash
# MT-001 Gate 3 runner: unattended real AI music batch, 30 files x 3 presets.
set -euo pipefail

CONFIG="${1:-configs/mt001_gate3_real_ai_30.json}"
RUN_ID="${2:-mt001_gate3_real_ai_$(date +%Y%m%d_%H%M%S)}"
SOURCE_DIR="${MT001_REAL_SOURCE_DIR:-/home/ubuntu/moodify-o3is/data/night_inputs}"
EXPECTED_SAMPLES="${MT001_EXPECTED_SAMPLES:-30}"
EXPECTED_PRESETS="${MT001_EXPECTED_PRESETS:-3}"
FRESH="${MT001_FRESH:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="${ROOT_DIR}:${ROOT_DIR}/moodify-core-package/src:${PYTHONPATH:-}"
mkdir -p logs data
LINK_PATH="data/mt001_real_inputs"
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Missing source dir: $SOURCE_DIR" >&2
  exit 10
fi
rm -rf "$LINK_PATH"
ln -s "$SOURCE_DIR" "$LINK_PATH"

LOG_FILE="logs/${RUN_ID}.log"
SUMMARY_FILE="logs/mt001_gate3_real_ai_final_summary.txt"
EXPECTED_TASKS="$((EXPECTED_SAMPLES * EXPECTED_PRESETS))"

if [ "$FRESH" = "1" ]; then
  rm -rf data/moodify_runtime_mt001_gate3
  rm -rf "outputs/mt001_gate3_real_ai/${RUN_ID}"
  rm -f "reports/mt001_gate3_real_ai/daily_report_${RUN_ID}.md"
  rm -f "reports/mt001_gate3_real_ai/daily_report_${RUN_ID}.json"
fi

{
  echo "============================================================"
  echo " MT-001 Gate 3 Real AI Run ? ${RUN_ID}"
  echo "============================================================"
  echo "started_at       = $(date -Iseconds)"
  echo "root             = ${ROOT_DIR}"
  echo "source_dir       = ${SOURCE_DIR}"
  echo "input_link       = ${LINK_PATH}"
  echo "config           = ${CONFIG}"
  echo "expected_samples = ${EXPECTED_SAMPLES}"
  echo "expected_tasks   = ${EXPECTED_TASKS}"
  echo "log_file         = ${LOG_FILE}"
  echo "fresh            = ${FRESH}"
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

run_step inventory bash -lc "find data/mt001_real_inputs -maxdepth 1 -type f \( -iname '*.mp3' -o -iname '*.flac' \) | sort | head -n ${EXPECTED_SAMPLES}; echo count=\$(find data/mt001_real_inputs -maxdepth 1 -type f \( -iname '*.mp3' -o -iname '*.flac' \) | wc -l)"
run_step system bash -lc "uptime; free -h; df -h .; .venv/bin/python --version; ffmpeg -version | head -n 1"
run_step register .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" register --source mt001_gate3_real_ai --notes "MT-001 Gate 3 real AI music batch"
run_step plan .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" plan --reason mt001_gate3_real_ai
run_step run .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" run --run-id "$RUN_ID"
run_step report .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" report --run-id "$RUN_ID"
run_step craft .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" craft --run-id "$RUN_ID"
run_step failures .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" failures --run-id "$RUN_ID"
run_step next .venv/bin/python -m moodify_runtime.cli --config "$CONFIG" next --run-id "$RUN_ID"

SUMMARY_JSON="outputs/mt001_gate3_real_ai/${RUN_ID}/summary.json"
MANIFEST="outputs/mt001_gate3_real_ai/${RUN_ID}/manifest.csv"
REPORT="reports/mt001_gate3_real_ai/daily_report_${RUN_ID}.md"

.venv/bin/python - <<PY >> "$LOG_FILE"
import csv, json
from pathlib import Path
summary_path = Path("$SUMMARY_JSON")
manifest_path = Path("$MANIFEST")
summary = json.loads(summary_path.read_text(encoding="utf-8"))
rows = list(csv.DictReader(manifest_path.open(encoding="utf-8")))
selected = int(summary.get("total_selected", 0))
success = int(summary.get("success", 0))
failed = int(summary.get("failed", 0))
expected = int("$EXPECTED_TASKS")
print(f"MT001_GATE3_RESULT selected={selected} success={success} failed={failed} manifest_rows={len(rows)} expected={expected}")
if selected != expected or success != expected or failed != 0 or len(rows) != expected:
    raise SystemExit(3)
PY

{
  echo "finished_at = $(date -Iseconds)"
  echo "result      = PASS"
  echo "summary     = ${SUMMARY_JSON}"
  echo "manifest    = ${MANIFEST}"
  echo "report      = ${REPORT}"
  echo "log_file    = ${LOG_FILE}"
} | tee -a "$SUMMARY_FILE" >> "$LOG_FILE"

echo "MT-001 Gate 3 real AI PASS: ${RUN_ID}"
