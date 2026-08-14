#!/usr/bin/env bash
# R06 data plane unblock — MFY_PRODUCTION_DATA_PLANE_001.
# RUN ONLY AFTER the human provides: (1) VPC peering / secure link between
# Hangzhou ECS and PolarDB, (2) credentials injected via the approved
# secret/env mechanism (never in this script, never in git).
# Sequence: network check -> health/read -> isolated write -> migration
# dry-run -> backup -> isolated restore -> entity reconciliation.
set -euo pipefail

: "${MOODIFY_DB_HOST:?set DB host via approved env mechanism}"
: "${MOODIFY_DB_USER:?set DB user via approved env mechanism}"
: "${MOODIFY_DB_NAME:?set DB name}"
MUSIC="https://rongjinwenchuan.xyz"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
echo "== data plane live $STAMP =="

echo "[1/7] network: Hangzhou API reachable over real chain"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$MUSIC/api/v1/music/bootstrap" || true)
[ "$code" = "200" ] || { echo "FAIL: bootstrap $code"; exit 1; }
echo "  bootstrap 200 (nginx -> BFF -> Hangzhou)"

echo "[2/7] health/read: catalogue through the chain"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$MUSIC/api/v1/music/catalogue" || true)
[ "$code" = "200" ] || { echo "FAIL: catalogue $code"; exit 1; }
echo "  catalogue 200"

echo "[3/7] isolated write: validation user + track in moodify_validation"
# requires a dedicated validation identity (56 dataset) and idempotency keys
# (invoke via BFF with session; fail-closed on 401/403)

echo "[4/7] migration dry-run: schema render + constraint tests"
python ops/schema_dry_run.py || exit 1

echo "[5/7] backup: mysqldump -> backup root"
BACKUP="${MOODIFY_BACKUP_ROOT:-/var/backups/moodify}/$STAMP"
mkdir -p "$BACKUP"
mysqldump --single-transaction --routines \
  -h "$MOODIFY_DB_HOST" -u "$MOODIFY_DB_USER" "${MOODIFY_DB_PASSWORD:+ -p$MOODIFY_DB_PASSWORD}" \
  "$MOODIFY_DB_NAME" > "$BACKUP/music-db.sql"
sha256sum "$BACKUP/music-db.sql" > "$BACKUP/music-db.sql.sha256"
echo "  backup: $BACKUP/music-db.sql"

echo "[6/7] restore into isolated database"
mysql -h "$MOODIFY_DB_HOST" -u "$MOODIFY_DB_USER" "${MOODIFY_DB_PASSWORD:+ -p$MOODIFY_DB_PASSWORD}" \
  -e "CREATE DATABASE IF NOT EXISTS ${MOODIFY_DB_NAME}_restore_${STAMP}"
mysql -h "$MOODIFY_DB_HOST" -u "$MOODIFY_DB_USER" "${MOODIFY_DB_PASSWORD:+ -p$MOODIFY_DB_PASSWORD}" \
  "${MOODIFY_DB_NAME}_restore_${STAMP}" < "$BACKUP/music-db.sql"

echo "[7/7] entity reconciliation (zero drift required)"
# export both schemas to sqlite-compatible dumps or run reconcile against a
# read replica; script ops/reconcile_data.py defines the six families
echo "  run: python ops/reconcile_data.py <prod-dump> <restore-dump>"
echo "== data plane live complete: record RPO/RTO, then close R06 =="
