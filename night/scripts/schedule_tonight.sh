#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   bash scripts/schedule_tonight.sh 23:30
# 不依赖 at/cron；使用 nohup + sleep 后台等待。
# 注意：请先用 date 确认服务器当前时间。

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TARGET_TIME="${1:-23:30}"
CONFIG="${2:-configs/night_config.json}"
mkdir -p logs outputs/night_runs

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

echo "[Moodify] server_now=$(date '+%F %T')"
echo "[Moodify] schedule_time=$TARGET_TIME"
echo "[Moodify] seconds_to_wait=$SECONDS_TO_WAIT"

nohup bash -lc "sleep $SECONDS_TO_WAIT; cd '$ROOT_DIR'; bash scripts/run_night_once.sh '$CONFIG'" \
  > "logs/night_schedule_$(date '+%Y%m%d_%H%M%S').log" 2>&1 &

echo "[Moodify] scheduled_pid=$!"
echo "[Moodify] 查看调度日志: tail -f logs/night_schedule_*.log"
echo "[Moodify] 查看运行日志: tail -f outputs/night_runs/latest/night_worker.log"
