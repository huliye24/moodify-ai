# Moodify Ear Batch Control Layer

This directory contains a thin, file-backed control layer for converting the
Moodify Ear v1 monograph corpus into reviewable engineering work. It is an
operations aid, not a Moodify product state machine.

The source corpus is treated as read-only. Every run records source hashes,
task dependencies, attempts, verification evidence, and blocked human
decisions. Moodify Ear v2 is explicitly excluded from the v1 batch.

## Quick start

```powershell
python ops/ear_batch/ear_batch.py init --source "E:\Moodify ear" --run-dir artifacts/ear_batch/v1
python ops/ear_batch/ear_batch.py validate --run-dir artifacts/ear_batch/v1
python ops/ear_batch/ear_batch.py status --run-dir artifacts/ear_batch/v1
python ops/ear_batch/ear_batch.py claim --run-dir artifacts/ear_batch/v1
```

After Codex's durable goal has started consuming the queue, keep Windows awake
and write a heartbeat once per minute with:

```powershell
powershell -ExecutionPolicy Bypass -File ops/ear_batch/Start-EarBatchWatch.ps1
```

The watcher never claims or edits tasks. It validates the source snapshot,
prevents system sleep while it is running, records liveness, and writes the
final summary once the queue reaches terminal states.

`claim` prints the next ready task and atomically changes its state to
`RUNNING`. The long-running Codex goal reads `TASK.md`, produces the declared
outputs, and then calls either `complete` or `fail`.

```powershell
python ops/ear_batch/ear_batch.py complete --run-dir artifacts/ear_batch/v1 --task TP-001
python ops/ear_batch/ear_batch.py fail --run-dir artifacts/ear_batch/v1 --task TP-001 --reason "reason"
python ops/ear_batch/ear_batch.py report --run-dir artifacts/ear_batch/v1
```

## Safety model

- No source file is modified.
- A task cannot be claimed before all dependencies pass.
- Failed tasks retry at most the declared number of times.
- Human-authority tasks become `BLOCKED_HUMAN` instead of guessing.
- Independent ready tasks remain runnable when another task is blocked.
- Ledger writes use replace-on-success and a process lock.
- Outputs live below the run directory and are reusable by later batches.

The controller does not invoke the Windows Store Codex executable. In this
environment that executable is owned by the desktop app and is not a reliable
CLI entry point. Codex's durable goal is the worker; this layer is the durable
queue and evidence record.
