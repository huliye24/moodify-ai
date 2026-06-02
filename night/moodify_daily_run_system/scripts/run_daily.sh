#!/usr/bin/env bash
# Moodify Daily Run — full pipeline
# Usage: bash scripts/run_daily.sh [config_path]
# Critical steps (register, plan, run) use strict error handling.
# Report/craft/next steps warn on failure but do not block.

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

CONFIG="${1:-configs/runtime_config.json}"
CLI="python3 -m moodify_runtime.cli --config $CONFIG"

echo "[Moodify] root=$ROOT_DIR"
echo "[Moodify] config=$CONFIG"
echo "[Moodify] start=$(date '+%F %T')"

# Step 1-3: critical — fail hard
echo "=== [1/6] register ==="
$CLI register --source "daily_input" || { echo "FATAL: register failed"; exit 1; }

echo "=== [2/6] plan ==="
$CLI plan || { echo "FATAL: plan failed"; exit 1; }

echo "=== [3/6] run ==="
$CLI run || { echo "FATAL: run failed"; exit 1; }

# Step 4-6: best-effort — warn only
echo "=== [4/6] report ==="
$CLI report || echo "WARNING: report generation failed (run data is still saved)"

echo "=== [5/6] craft ==="
$CLI craft || echo "WARNING: craft memory generation failed"

echo "=== [6/6] next ==="
$CLI next || echo "WARNING: planner failed"

echo "[Moodify] finish=$(date '+%F %T')"
echo "[Moodify] Done. Check outputs/daily_runs/latest/ and reports/daily_runs/"
