# MHP-857: Worker Task JSONL Shape — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C

## Key Deliverable

MAP-specific Worker Task JSONL shape extending the generic AEP Worker Protocol.

## Task Shape (18 fields)

Full JSONL task record with: `task_id`, `echain`, `nem`, `mhp`, `mhp_title`, `phase`, `type`, `layer`, `role`, `input_files`, `allowed_files`, `forbidden_files`, `expected_outputs`, `proof_commands`, `architect_notes`, `priority`, `depends_on`.

## Worker Output Shape (6 fields)

Worker returns: `task_id`, `status`, `artifacts`, `proof_results`, `diff_summary`, `notes`.

## AWJ Control

- Architect writes JSONL, defines allowed/forbidden files, sets proof commands.
- Worker processes ONE task, cannot change task_id/mhp/allowed_files/proof_commands/priority.
- Judge validates scope (allowed_files check), runtime (proof commands exit 0), evidence (artifacts exist).

## Compatibility

Shape is compatible with existing `scripts/aep_worker_protocol.py validate` and `select` subcommands. The `task_id` and `loop`-equivalent field (`layer`) are preserved.

## Build NEM Application

~36 Worker tasks across 18 Build MHPs, dispatched as JSONL files per Build block (6A/6B/6C).
