# TP-003 — Define v1 and v2 isolation rules

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Document deterministic inclusion and exclusion rules so v2 material can never enter the v1 batch accidentally.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-001
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `corpus/version_boundaries.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-003.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
