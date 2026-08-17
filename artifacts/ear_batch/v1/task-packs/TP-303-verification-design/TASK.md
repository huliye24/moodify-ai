# TP-303 — Design tests and evidence for work items

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

For every work item specify automated tests, evidence artifacts, failure handling, and any required human listening judgment.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-302
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `planning/verification_matrix.csv`
- `planning/verification_matrix.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-303.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
