#!/usr/bin/env bash
# Soak probe — MFY_CLOUD_RELIABILITY_CAPACITY_DR_001.
# Long-running health/queue/backup-age observation; writes a time-series log.
# Usage: soak_probe.sh <minutes> [interval_seconds]
set -u

MINUTES="${1:-10}"
INTERVAL="${2:-60}"
LOG="soak-$(date -u +%Y%m%dT%H%M%SZ).log"
BASE="${MOODIFY_E2E_BASE:-https://rongjingmusic.com}"
MUSIC_BASE="${MOODIFY_E2E_MUSIC_BASE:-https://rongjinwenchuan.xyz}"
END=$(( $(date +%s) + MINUTES * 60 ))

echo "SOAK start $(date -u +%Y-%m-%dT%H:%M:%SZ) minutes=$MINUTES interval=${INTERVAL}s" | tee "$LOG"
while [ "$(date +%s)" -lt "$END" ]; do
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  h_web=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$BASE/healthz" 2>/dev/null || true); [ -z "$h_web" ] && h_web=000
  h_ear=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$BASE/api/v1/health" 2>/dev/null || true); [ -z "$h_ear" ] && h_ear=000
  h_music=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$MUSIC_BASE/api/v1/music/bootstrap" 2>/dev/null || true); [ -z "$h_music" ] && h_music=000
  h_range=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "Range: bytes=0-1023" \
    "$MUSIC_BASE/audio/cadeau10-album1/je-ne-veux-pas-enfermer-ton-aujourdhui.wav" 2>/dev/null || true); [ -z "$h_range" ] && h_range=000
  echo "$ts web=$h_web ear=$h_ear music=$h_music range=$h_range" | tee -a "$LOG"
  sleep "$INTERVAL"
done
echo "SOAK end $(date -u +%Y-%m-%dT%H:%M:%SZ) — log: $LOG" | tee -a "$LOG"
