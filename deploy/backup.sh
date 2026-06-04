#!/usr/bin/env bash
# Moodify JSONL Backup & Rotation Script
# Usage: ./deploy/backup.sh [--rotate] [--keep N]
# Cron:  0 3 * * * /opt/moodify/deploy/backup.sh --rotate --keep 7

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
DATA_DIR="${MOODIFY_DATA_DIR:-${PROJECT_ROOT}/data}"
BACKUP_DIR="${MOODIFY_BACKUP_DIR:-${PROJECT_ROOT}/backups}"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
KEEP=${KEEP:-7}

JSONL_FILES=(
    "operator_jobs.jsonl"
    "operator_deliveries.jsonl"
    "registry.jsonl"
    "queue.jsonl"
)

backup() {
    mkdir -p "${BACKUP_DIR}"
    local tarball="${BACKUP_DIR}/moodify_backup_${TIMESTAMP}.tar.gz"

    for f in "${JSONL_FILES[@]}"; do
        if [[ -f "${DATA_DIR}/${f}" ]]; then
            cp "${DATA_DIR}/${f}" "${BACKUP_DIR}/${f}.${TIMESTAMP}"
        fi
    done

    # Also backup studio, scheduler, calibration, craft dirs if they exist
    for d in studio scheduler calibration craft_memory; do
        if [[ -d "${DATA_DIR}/${d}" ]]; then
            cp -r "${DATA_DIR}/${d}" "${BACKUP_DIR}/${d}_${TIMESTAMP}"
        fi
    done

    # Create tarball of all backed-up files
    cd "${BACKUP_DIR}"
    tar czf "${tarball}" --mtime="0" ./*_${TIMESTAMP}* 2>/dev/null || true
    echo "Backup: ${tarball}"

    # Clean up loose files
    rm -f ./*_${TIMESTAMP} 2>/dev/null || true
    rm -rf ./*_${TIMESTAMP} 2>/dev/null || true
}

rotate() {
    local files
    files=$(ls -1t "${BACKUP_DIR}"/moodify_backup_*.tar.gz 2>/dev/null || true)
    local count
    count=$(echo "${files}" | grep -c . || echo 0)

    if [[ ${count} -gt ${KEEP} ]]; then
        echo "Rotating: keeping ${KEEP} of ${count} backups"
        echo "${files}" | tail -n +$((KEEP + 1)) | xargs rm -f
    fi
}

main() {
    backup
    for arg in "$@"; do
        case "$arg" in
            --rotate) rotate ;;
            --keep) KEEP="$2"; shift ;;
        esac
    done
    echo "Backup complete. $(date -u)"
}

main "$@"
