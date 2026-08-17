# TP-205 — Define Ear 1.0 engineering scope

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Draft an evidence-backed implementation scope, non-goals, human-authority points, and unresolved architecture decisions.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-202, TP-203, TP-204
- Risk: `human-review`
- Maximum attempts: 3

## Required outputs

- `planning/ear_v1_engineering_scope.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-205.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
