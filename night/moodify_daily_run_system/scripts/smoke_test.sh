#!/usr/bin/env bash
# Smoke test: validates the full pipeline.
# Default: dry-run only (safe).
# With --real: processes 1 audio file for real.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

CONFIG="${2:-configs/runtime_config.json}"
CLI="python3 -m moodify_runtime.cli --config $CONFIG"

if [ "${1:-}" = "--real" ]; then
  echo "=== Smoke Test (REAL) ==="
  $CLI register --source "smoke_test"
  $CLI plan --max-new-tasks 1
  $CLI run --limit 1
  echo "Smoke test (real) complete. Check outputs/daily_runs/latest/"
else
  echo "=== Smoke Test (DRY-RUN) ==="
  $CLI register --source "smoke_test"
  $CLI plan --max-new-tasks 1
  $CLI run --limit 1 --dry-run
  echo "Smoke test (dry-run) complete. To run for real: bash scripts/smoke_test.sh --real"
fi
