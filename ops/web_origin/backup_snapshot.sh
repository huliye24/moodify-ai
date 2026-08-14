#!/usr/bin/env bash
# Backup snapshot — MFY_PRODUCTION_OPERATIONS_OBSERVABILITY_001.
# Backs up the authoritative data that must survive: Ear case dirs +
# review ledger, Music DB dump, media reference manifest.
# RPO target: 24h. Restore must verify ids/hashes (runbook R3).
set -euo pipefail

BACKUP_ROOT="${MOODIFY_BACKUP_ROOT:-/var/backups/moodify}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="${BACKUP_ROOT}/${STAMP}"
mkdir -p "$DEST"

# Ear: case manifests + review ledger (raw sqlite backup is consistent)
EAR_CASES="${MOODIFY_EAR_CASES:-/var/lib/moodify/data_factory}"
EAR_REVIEW_DB="${MOODIFY_REVIEW_DB:-/var/lib/moodify/review.sqlite3}"
if [ -d "$EAR_CASES" ]; then
  tar -czf "$DEST/ear-cases.tar.gz" -C "$(dirname "$EAR_CASES")" "$(basename "$EAR_CASES")"
fi
if [ -f "$EAR_REVIEW_DB" ]; then
  python - "$EAR_REVIEW_DB" "$DEST/review.sqlite3" <<'PY'
import sqlite3, sys
src, dst = sys.argv[1], sys.argv[2]
con = sqlite3.connect(src)
backup = sqlite3.connect(dst)
con.backup(backup)
backup.close(); con.close()
PY
fi

# Music: media reference manifest (never re-encode media)
MEDIA_ROOT="${MOODIFY_MEDIA_ROOT:-/opt/moodify/music-media}"
if [ -d "$MEDIA_ROOT" ]; then
  find "$MEDIA_ROOT" -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.ogg' -o -name '*.m4a' \) \
    -exec sha256sum {} + > "$DEST/media-manifest.sha256"
fi

# Music DB dump (MySQL/PolarDB); skipped when credentials are absent
if [ -n "${MOODIFY_DB_USER:-}" ] && [ -n "${MOODIFY_DB_NAME:-}" ]; then
  mysqldump --single-transaction --routines \
    -h "${MOODIFY_DB_HOST:-127.0.0.1}" -u "$MOODIFY_DB_USER" \
    "${MOODIFY_DB_PASSWORD:+ -p$MOODIFY_DB_PASSWORD}" \
    "$MOODIFY_DB_NAME" > "$DEST/music-db.sql" 2>/dev/null || echo "db dump skipped (creds)" > "$DEST/db-skip.log"
fi

# release metadata
git -C "$(dirname "${BASH_SOURCE[0]}")/../.." rev-parse HEAD > "$DEST/release-commit.txt" 2>/dev/null || true
sha256sum "$DEST"/* > "$DEST/backup.sha256" 2>/dev/null || true
echo "BACKUP: $DEST"
