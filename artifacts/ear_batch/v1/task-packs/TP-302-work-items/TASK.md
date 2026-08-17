# TP-302 — Decompose epics into verifiable work items

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Create small work items with inputs, allowed paths, outputs, acceptance criteria, dependencies, recovery behavior, and evidence requirements.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-301
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `planning/work_items.jsonl`
- `planning/work_items.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-302.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
