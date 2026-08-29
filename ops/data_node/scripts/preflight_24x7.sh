#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-artifacts/mfy_24x7_data_pipeline_001}"
mkdir -p "$OUT"

{
  echo "date=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -a)"
  echo "python=$(/opt/moodify/.venv/bin/python --version 2>&1 || true)"
  echo "ffmpeg=$(ffmpeg -version 2>/dev/null | head -n1 || true)"
  echo "moodify_node=$(/opt/moodify/.venv/bin/moodify-node --help >/dev/null 2>&1 && echo OK || echo MISSING)"
} >"$OUT/preflight.txt"

free -h >"$OUT/free.txt"
df -h >"$OUT/df.txt"
swapon --show >"$OUT/swapon.txt" || true
systemctl --no-pager --full status moodify-data-worker.service >"$OUT/worker_status.txt" 2>&1 || true
systemctl --no-pager --full status moodify-api.service >"$OUT/api_status.txt" 2>&1 || true
/opt/moodify/.venv/bin/moodify-node health >"$OUT/node_health.json" 2>&1 || true
/opt/moodify/.venv/bin/moodify-node status >"$OUT/node_status.json" 2>&1 || true

echo "preflight written to $OUT"
