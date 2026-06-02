#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   bash scripts/schedule_daily.sh 23:30
# 说明：
#   不依赖 cron/at。用 nohup + sleep 挂后台。
#   服务器重启后不会保留。长期应改成 cron 或 systemd timer。

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TARGET_TIME="${1:-23:30}"
CONFIG="${2:-configs/runtime_config.json}"
mkdir -p logs

SECONDS_TO_WAIT="$(python3 - "$TARGET_TIME" <<'PY'
import sys, datetime as dt
target = sys.argv[1]
hh, mm = map(int, target.split(":"))
now = dt.datetime.now()
run_at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
if run_at <= now:
    run_at += dt.timedelta(days=1)
print(int((run_at - now).total_seconds()))
PY
)"

echo "[Moodify Runtime] server_now=$(date '+%F %T')"
echo "[Moodify Runtime] target=$TARGET_TIME"
echo "[Moodify Runtime] seconds_to_wait=$SECONDS_TO_WAIT"

nohup bash -lc "sleep $SECONDS_TO_WAIT; cd '$ROOT_DIR'; bash scripts/run_daily.sh '$CONFIG'" \
  > "logs/moodify_daily_schedule_$(date '+%Y%m%d_%H%M%S').log" 2>&1 &

echo "[Moodify Runtime] scheduled_pid=$!"
echo "[Moodify Runtime] log: tail -f logs/moodify_daily_schedule_*.log"
