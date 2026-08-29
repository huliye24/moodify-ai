# TP-201 — Inventory current repository capabilities

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Inspect verified mainline code and tests. Record CANONICAL, EXPERIMENTAL, LEGACY, HISTORICAL, ABSENT, or UNRESOLVED with concrete paths and test evidence.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-006
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `alignment/repository_capabilities.json`
- `alignment/repository_capabilities.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-201.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
