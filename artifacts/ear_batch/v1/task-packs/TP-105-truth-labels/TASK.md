# TP-105 — Classify theory experiment and verified capability

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Classify every material claim as theory, hypothesis, experimental evidence, current verified capability, historical statement, or unresolved. Never promote a claim from documentation alone.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-101, TP-104
- Risk: `human-review`
- Maximum attempts: 3

## Required outputs

- `knowledge/truth_labels.jsonl`
- `knowledge/truth_label_review.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-105.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
