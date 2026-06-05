# MHP-796: Data Loop Probe Backlog

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P6 (Next Entry)
**Depends on**: MHP-795
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define the next cheap-model probes after the first data-loop extraction.

DeepSeek v4 constraint: each backlog item must create or consume one small JSONL shape. No item may require repository-wide reading or multi-step reasoning inside the model.

## Backlog Status — 2026-06-05 Execution

| MHP | Title | Status | Notes |
|-----|-------|--------|-------|
| MHP-797 | Define DeepSeek v4 JSON Schema | ✅ done | Schema at `schemas/deepseek_worker_output.schema.json` |
| MHP-798 | Generate Runtime Reliability Task JSONL | ⏳ planned | Per-loop standalone extraction from snapshot |
| MHP-799 | Generate Scoring Calibration Task JSONL | ⏳ planned | Per-loop standalone extraction from snapshot |
| MHP-800 | Generate Craft/Preset Task JSONL | ⏳ planned | Per-loop standalone extraction from snapshot |
| MHP-801 | Merge DeepSeek JSON Outputs | ✅ done | `scripts/aep_worker_protocol.py validate` works — 7 valid / 2 rejected |
| MHP-802 | Pick Next Three Optimization Tasks | ✅ done | `scripts/aep_worker_protocol.py select` works — 3 picked by severity + loop diversity |

## Runbook Path (One-Pass)

The runbook script `scripts/data_loop_runbook.py` generates all four loop types in one pass into `deepseek_tasks.jsonl`. Per-loop standalone extraction (MHP-798/799/800) provides finer-grained control for individual loop reruns.

## Probe Plan-6A Completion

Probe Plan-6A (Loop Boundary) is functionally complete. The runbook extracted last-night metrics, detected 3 score-direction disagreements and 2 penalty flags, and produced 7 DeepSeek micro-tasks across all four loops.

## Next: Probe Plan-6B Completion → Probe Plan-6C

1. MHP-798/799/800: Per-loop standalone extraction scripts.
2. MHP-803: Define Data Loop SLO (Probe Plan-6C entry).
3. MHP-804: Run Two-Cycle Learning Probe (real DeepSeek API calls).
4. MHP-805: Validate Recommendation Replayability.
5. MHP-806: Validate Optimization Backlog Quality.
6. MHP-807: Data Loop Probe Decision (ADOPT/HOLD/DROP).
7. MHP-808: Data Loop Build Entry.

## Acceptance Criteria

- Backlog names the next executable MHP. ✅ → MHP-798
- Each backlog item can be run with one-record JSONL model calls. ✅
- The model never needs more than one input record at a time. ✅
- The final output is capped at three optimization tasks. ✅ — validated by `select`
