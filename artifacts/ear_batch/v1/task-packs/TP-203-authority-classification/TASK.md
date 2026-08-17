# TP-203 — Classify canonical experimental and legacy areas

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Apply repository authority rules and identify classifications that require a human decision.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-201
- Risk: `human-review`
- Maximum attempts: 3

## Required outputs

- `alignment/authority_map.json`
- `alignment/authority_review.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-203.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
