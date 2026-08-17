# TP-304 — Build prioritized execution DAG

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

Build a cycle-free dependency graph and prioritize foundational, low-risk, high-evidence tasks.

## Context

- Source corpus: `E:\Moodify ear` (read-only)
- Run directory: `E:\moodify\artifacts\ear_batch\v1`
- Dependencies: TP-302, TP-303
- Risk: `safe`
- Maximum attempts: 3

## Required outputs

- `planning/execution_dag.json`
- `planning/execution_dag.md`

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/TP-304.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
