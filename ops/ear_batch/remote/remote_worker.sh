#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="${1:-$HOME/moodify-ear-remote}"
REPO_ROOT="$REMOTE_ROOT/repo"
RUN_DIR="$REPO_ROOT/artifacts/ear_batch/v1"
SOURCE_DIR="$REMOTE_ROOT/source/Moodify ear"
LOG_DIR="$REMOTE_ROOT/logs"
LOCK_FILE="$REMOTE_ROOT/worker.lock"
MAX_TASK_SECONDS="${MAX_TASK_SECONDS:-7200}"
IDLE_SECONDS="${IDLE_SECONDS:-30}"

mkdir -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  printf 'another worker owns %s\n' "$LOCK_FILE" >&2
  exit 2
fi

export PYTHONUNBUFFERED=1
cd "$REPO_ROOT"
bash ops/ear_batch/remote/remote_preflight.sh "$REMOTE_ROOT"

ledger_counts() {
  python3 - "$RUN_DIR/TASK_LEDGER.json" <<'PY'
import json, sys
from collections import Counter
data=json.load(open(sys.argv[1], encoding="utf-8"))
c=Counter(item["state"] for item in data["tasks"])
print(c.get("READY",0), c.get("RUNNING",0), c.get("VERIFYING",0),
      c.get("FAILED_RETRYABLE",0), c.get("PENDING",0), c.get("PASSED",0),
      c.get("BLOCKED_HUMAN",0), c.get("SKIPPED",0))
PY
}

while true; do
  claim_file=$(mktemp "$REMOTE_ROOT/claim.XXXXXX")
  python3 ops/ear_batch/ear_batch.py claim --run-dir "$RUN_DIR" >"$claim_file"
  if grep -qx 'NO_READY_TASK' "$claim_file"; then
    read -r ready running verifying retryable pending passed blocked skipped < <(ledger_counts)
    rm -f "$claim_file"
    if (( ready + running + verifying + retryable == 0 )); then
      if (( pending == 0 )); then
        python3 ops/ear_batch/ear_batch.py report --run-dir "$RUN_DIR"
        printf 'QUEUE_TERMINAL passed=%s blocked=%s skipped=%s\n' "$passed" "$blocked" "$skipped"
        exit 0
      fi
      printf 'QUEUE_STALLED pending=%s blocked=%s; no ready work remains\n' "$pending" "$blocked" >&2
      python3 ops/ear_batch/ear_batch.py report --run-dir "$RUN_DIR"
      exit 3
    fi
    sleep "$IDLE_SECONDS"
    continue
  fi

  task_id=$(python3 - "$claim_file" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["id"])
PY
)
  task_file=$(python3 - "$claim_file" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["task_file"])
PY
)
  rm -f "$claim_file"
  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  event_log="$LOG_DIR/${task_id}-${stamp}.jsonl"
  final_log="$LOG_DIR/${task_id}-${stamp}.final.md"
  prompt_file=$(mktemp "$REMOTE_ROOT/prompt.XXXXXX")
  {
    printf '%s\n\n' 'You are the unattended worker for one Moodify Ear v1 task pack.'
    printf '%s\n' "Repository: $REPO_ROOT"
    printf '%s\n' "Read-only source corpus: $SOURCE_DIR"
    printf '%s\n' "Run directory: $RUN_DIR"
    printf '%s\n\n' 'Follow AGENTS.md. Work only on this task. Never change source corpus files, product authority, credentials, remote services, Git remotes, or publish anything. Produce every required output below the run directory. Run relevant verification. Do not update TASK_LEDGER.json; the wrapper owns state transitions. If a human decision is required, do not guess: explain it in the final response and avoid fabricating the output.'
    cat "$task_file"
  } >"$prompt_file"

  set +e
  timeout --signal=TERM --kill-after=30s "$MAX_TASK_SECONDS" \
    codex exec --sandbox workspace-write --json -C "$REPO_ROOT" \
      --output-last-message "$final_log" - <"$prompt_file" >"$event_log" 2>"$event_log.stderr"
  rc=$?
  set -e
  rm -f "$prompt_file"

  if [[ "$rc" -eq 0 ]]; then
    python3 ops/ear_batch/ear_batch.py complete --run-dir "$RUN_DIR" --task "$task_id"
  else
    reason="codex exec failed rc=$rc; logs=$event_log"
    python3 ops/ear_batch/ear_batch.py fail --run-dir "$RUN_DIR" --task "$task_id" --reason "$reason"
  fi
done
