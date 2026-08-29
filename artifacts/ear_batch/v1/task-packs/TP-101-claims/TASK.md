# TP-101 — Extract chapter claims

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Extract atomic claims from all 20 chapters with chapter, section, source path, claim type, and confidence. Preserve the distinction between proposal and verified fact.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-006
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `knowledge/claims.jsonl`
- `knowledge/claims_summary.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-101.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
