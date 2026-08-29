# TP-305 — Select unattended-safe implementation batch

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Select only reversible, bounded, testable work that requires no listening judgment, external authorization, secrets, publishing, deletion, or authority change.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-304
- Risk: `human-review`
- Maximum attempts: 3

## Required outputs

- `planning/unattended_batch.json`
- `planning/unattended_batch.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-305.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
