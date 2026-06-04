# MHP-796: Data Loop Probe Backlog

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P6 (Next Entry)
**Depends on**: MHP-795
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define the next cheap-model probes after the first data-loop extraction.

DeepSeek v4 constraint: each backlog item must create or consume one small JSONL shape. No item may require repository-wide reading or multi-step reasoning inside the model.

## Backlog

1. MHP-797 Define DeepSeek v4 JSON Schema
   - Fix the model output shape before running any calls.
2. MHP-798 Generate Runtime Reliability Task JSONL
   - Create one run-level task when fatal errors, failed tasks, or missing artifacts appear.
3. MHP-799 Generate Scoring Calibration Task JSONL
   - Create one task-level record per pseudo/MRS Open sign disagreement.
4. MHP-800 Generate Craft/Preset Task JSONL
   - Create one task-level record per penalty flag or weak preset result.
5. MHP-801 Merge DeepSeek JSON Outputs
   - Validate JSON, reject malformed output, and merge model decisions into one table.
6. MHP-802 Pick Next Three Optimization Tasks
   - Sort validated decisions by severity and choose at most three tasks for the next run.

## Acceptance Criteria

- Backlog names the next executable MHP.
- Each backlog item can be run with one-record JSONL model calls.
- The model never needs more than one input record at a time.
- The final output is capped at three optimization tasks.
