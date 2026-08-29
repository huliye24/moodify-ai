# TP-104 — Extract measurement and evidence requirements

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Extract what is measured, what evidence is produced, how results are verified, and what happens on failure.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-101
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `knowledge/evidence_requirements.json`
- `knowledge/evidence_requirements.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-104.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
