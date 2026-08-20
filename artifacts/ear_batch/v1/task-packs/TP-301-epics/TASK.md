# TP-301 — Generate engineering epics

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Generate outcome-oriented epics tied to traceability identifiers and repository authority.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-202, TP-205
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `planning/epics.json`
- `planning/epics.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-301.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
