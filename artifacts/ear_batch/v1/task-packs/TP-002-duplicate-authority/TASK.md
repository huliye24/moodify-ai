# TP-002 — Resolve duplicate chapter sources

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Compare duplicate Chapter 02-04 directories and packages byte-for-byte and semantically. Recommend the authoritative copy without deleting anything. Mark unresolved differences for human review.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-001
- Risk: `human-review`
- Maximum attempts: 3

## Required outputs

- `corpus/source_authority.json`
- `corpus/duplicate_analysis.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-002.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
