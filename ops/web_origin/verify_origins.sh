#!/usr/bin/env bash
set -euo pipefail

ORIGIN="${ORIGIN:-127.0.0.1}"

check() {
  local host="$1" path="$2" expected="$3"
  local body code
  body=$(mktemp)
  code=$(curl -sS -H "Host: $host" -o "$body" -w '%{http_code}' "http://$ORIGIN$path")
  [[ "$code" == 200 ]]
  grep -Fq "$expected" "$body"
  printf 'PASS host=%s path=%s code=%s bytes=%s\n' "$host" "$path" "$code" "$(wc -c <"$body")"
  rm -f "$body"
}

check rongjingmusic.com /healthz '"site":"rongjingmusic.com"'
check rongjingmusic.com / 'Every voice deserves to be heard.'
check rongjingmusic.com /assets/site-public-form-20260820.css '.site-header'
check rongjingmusic.com /assets/moodify-logo.png 'PNG'
check rongjingwenchuan.com /healthz '"site":"rongjingwenchuan.com"'
check rongjingwenchuan.com / 'We build things worth hearing.'
check rongjingwenchuan.com /styles.css '.company-shell'

nginx -t
systemctl is-enabled nginx
systemctl is-active nginx
