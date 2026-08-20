# TP-204 — Identify orchestration authority conflicts

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Locate duplicate or competing orchestration systems and explain risks without modifying or deleting them.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-201, TP-203
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `alignment/orchestration_risks.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-204.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
