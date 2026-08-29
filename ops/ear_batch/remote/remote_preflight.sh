#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="${1:-$HOME/moodify-ear-remote}"
REPO_ROOT="$REMOTE_ROOT/repo"
RUN_DIR="$REPO_ROOT/artifacts/ear_batch/v1"
SOURCE_DIR="$REMOTE_ROOT/source/Moodify ear"

fail=0
check_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'MISSING command=%s\n' "$1"
    fail=1
  fi
}

for command_name in bash python3 git tar flock timeout codex; do
  check_command "$command_name"
done

if [[ ! -d "$REPO_ROOT/.git" ]]; then
  printf 'MISSING git_repository=%s\n' "$REPO_ROOT"
  fail=1
fi
if [[ ! -f "$RUN_DIR/TASK_LEDGER.json" ]]; then
  printf 'MISSING ledger=%s\n' "$RUN_DIR/TASK_LEDGER.json"
  fail=1
fi
if [[ ! -d "$SOURCE_DIR" ]]; then
  printf 'MISSING source=%s\n' "$SOURCE_DIR"
  fail=1
fi
if command -v codex >/dev/null 2>&1; then
  codex --version || fail=1
  codex login status || {
    printf 'MISSING codex_auth=run codex login --device-auth as this service user\n'
    fail=1
  }
fi

available_kb=$(df -Pk "$REMOTE_ROOT" | awk 'NR==2 {print $4}')
if [[ "${available_kb:-0}" -lt 2097152 ]]; then
  printf 'INSUFFICIENT disk_available_kb=%s required_kb=2097152\n' "${available_kb:-0}"
  fail=1
fi

printf 'REMOTE_ROOT=%s\nREPO_ROOT=%s\nRUN_DIR=%s\nSOURCE_DIR=%s\n' \
  "$REMOTE_ROOT" "$REPO_ROOT" "$RUN_DIR" "$SOURCE_DIR"
printf 'cpu=%s\n' "$(nproc)"
awk '/MemTotal/{printf "memory_mb=%d\n", $2/1024}' /proc/meminfo
printf 'disk_available_kb=%s\n' "$available_kb"

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

python3 "$REPO_ROOT/ops/ear_batch/ear_batch.py" validate --run-dir "$RUN_DIR"
printf 'PREFLIGHT_OK\n'
