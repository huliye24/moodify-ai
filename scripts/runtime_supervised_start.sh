#!/usr/bin/env bash
# MHP-116: Supervised Launch Script — starts the runtime under supervisor.
set -euo pipefail

HEARTBEAT_FILE="${MOODIFY_RUNTIME_HEARTBEAT:-/tmp/moodify_runtime_heartbeat.json}"
HEARTBEAT_INTERVAL="${HEARTBEAT_INTERVAL:-15}"
RUN_LIMIT="${RUN_LIMIT:-0}"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Runtime supervisor starting..."
echo "  Heartbeat: ${HEARTBEAT_FILE} (interval: ${HEARTBEAT_INTERVAL}s)"
echo "  Limit: ${RUN_LIMIT:-unlimited}"

# Write initial heartbeat
python3 -c "
import json, os, time
open('${HEARTBEAT_FILE}','w').write(json.dumps({
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'pid': os.getpid(),
    'uptime_s': 0
}))
"

trap "echo 'Supervisor shutting down...'" EXIT

# Start runtime with supervisor module
exec python3 -m moodify_runtime.cli run --limit "${RUN_LIMIT}"
