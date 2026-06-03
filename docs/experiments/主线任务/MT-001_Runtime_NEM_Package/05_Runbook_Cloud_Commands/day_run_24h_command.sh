#!/usr/bin/env bash
set -e

PROJECT_DIR="/path/to/moodify-o3is"
cd "$PROJECT_DIR"

mkdir -p logs runs reports

LOG_FILE="logs/day_run_001_$(date +%Y%m%d_%H%M%S).log"

nohup python3 scripts/day_run_24h.py > "$LOG_FILE" 2>&1 &

echo "Moodify Day Run started."
echo "PID: $!"
echo "LOG: $LOG_FILE"
echo ""
echo "Check progress:"
echo "tail -20 $LOG_FILE"
echo ""
echo "Check process:"
echo "ps aux | grep day_run_24h | grep -v grep"
