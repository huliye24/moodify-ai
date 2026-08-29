#!/usr/bin/env bash
set -euo pipefail

echo "== worker =="
systemctl is-active moodify-data-worker.service

echo "== timers =="
for t in \
  moodify-inbox-ingest.timer \
  moodify-resource-probe.timer \
  moodify-daily-report.timer \
  moodify-metadata-backup.timer
do
  printf "%-40s " "$t"
  systemctl is-active "$t"
done

echo "== resources =="
free -h
swapon --show
df -h /var/lib/moodify

echo "== queue =="
/opt/moodify/.venv/bin/moodify-node status

echo "== recent resource snapshots =="
tail -n 5 /var/lib/moodify/ops/resource_snapshots.jsonl 2>/dev/null || true

echo "== recent reports =="
find /var/lib/moodify/reports -name node_daily_report.md -type f | sort | tail -n 3 || true

echo "== OOM evidence =="
journalctl -k --since "24 hours ago" --no-pager -o cat | grep -Ei 'oom|out of memory|killed process' || true
