# TP-001 — Inventory and hash the v1 corpus

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Build a complete v1 file inventory with relative paths, sizes, SHA-256 hashes, formats, and duplicate candidates. Exclude Moodify Ear v2 from the v1 corpus.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: none
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `corpus/inventory.json`
- `corpus/inventory.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-001.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
