# MHP-802: Pick Next Three Optimization Tasks

**Status**: planned
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P6 (Next Entry)
**Depends on**: MHP-801
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Turn validated DeepSeek decisions into a small next-action list.

Use `scripts/aep_worker_protocol.py select` for the first implementation.

## Input

`deepseek_decisions_validated.jsonl`

## Selection Rule

1. Keep all `high` severity decisions first.
2. Then keep `medium`.
3. Then keep `low`.
4. Keep at most three total tasks.
5. Prefer one task from each loop if severities are tied.

## Output

`next_three_optimization_tasks.json`

## Acceptance Criteria

- Output has no more than three tasks.
- Each task has one owner action.
- The next night run can verify whether the action helped.
