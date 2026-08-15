#!/usr/bin/env bash
# Read-only resource probe — MFY_CLOUD_RESOURCE_AND_VALIDATION_FABRIC_001.
# Verifies reachability of every production resource over the real proxy
# chain. Never writes, never echoes secrets. Run any time; output is a
# timestamped line per resource.
set -u

LA="https://rongjingmusic.com"
MUSIC="https://rongjinwenchuan.xyz"
HANGZHOU_HTTP="http://120.55.191.146:8000"
AUDIO="audio/cadeau10-album1/je-ne-veux-pas-enfermer-ton-aujourdhui.wav"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fail=0

probe() {
  local label="$1" expected="$2" url="$3" extra="${4:-}"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 $extra "$url" 2>/dev/null || true)
  [ -z "$code" ] && code=000
  if [ "$code" = "$expected" ]; then
    echo "$TS OK   $label -> $code"
  else
    echo "$TS FAIL $label -> $code (expected $expected)"
    fail=1
  fi
}

echo "== resource probe $TS =="
probe "LA nginx /healthz"       200 "$LA/healthz"
probe "LA Ear API /health"      200 "$LA/api/v1/health"
probe "LA Music BFF bootstrap"  200 "$MUSIC/api/v1/music/bootstrap"
probe "LA Music BFF readiness"  200 "$MUSIC/ready"
probe "LA Music catalogue"      200 "$MUSIC/api/v1/music/catalogue"
probe "LA audio Range"          206 "$MUSIC/$AUDIO" "-H Range:bytes=0-1023"
probe "Hangzhou Data API health" 200 "$HANGZHOU_HTTP/health"
probe "Hangzhou Data API ready"  200 "$HANGZHOU_HTTP/ready"
probe "官网 index"              200 "$LA/"
probe "官网 evidence"           200 "$LA/evidence.html"

if [ "$fail" = "0" ]; then
  echo "$TS RESULT: ALL RESOURCES REACHABLE"
  exit 0
fi
echo "$TS RESULT: RESOURCE PROBE FAILURES — see lines above (do not modify production boundaries)"
exit 1
