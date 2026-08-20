#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:?usage: rollback_static_origin.sh DOMAIN RELEASE_ID}"
RELEASE_ID="${2:?usage: rollback_static_origin.sh DOMAIN RELEASE_ID}"
case "$DOMAIN" in
  rongjingmusic.com|rongjingwenchuan.com) ;;
  *) printf 'unsupported domain: %s\n' "$DOMAIN" >&2; exit 2 ;;
esac
TARGET="/var/www/$DOMAIN/releases/$RELEASE_ID"
[[ -d "$TARGET" ]] || { printf 'release not found: %s\n' "$TARGET" >&2; exit 3; }
ln -sfn "$TARGET" "/var/www/$DOMAIN/current"
nginx -t
systemctl reload nginx
printf 'rolled back domain=%s release=%s\n' "$DOMAIN" "$RELEASE_ID"
