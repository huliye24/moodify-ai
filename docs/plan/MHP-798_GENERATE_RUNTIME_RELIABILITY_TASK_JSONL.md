# MHP-798: Generate Runtime Reliability Task JSONL

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P2 (Execution)
**Depends on**: MHP-797
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Create at most one DeepSeek task for runtime reliability.

## Input

`last_night_metric_snapshot.json`

Fields:

- `source_run`
- `success`
- `failed`
- `fatal_error`

## Output

Append one JSONL line only when `fatal_error` exists or `failed > 0`.

```json
{
  "task_id": "RUN_ID:runtime",
  "loop": "runtime_reliability",
  "input_type": "run_record",
  "data": {
    "run_id": "RUN_ID",
    "success": 4,
    "failed": 0,
    "fatal_error": "error text"
  },
  "instruction": "Classify runtime severity and give one next action."
}
```

## Acceptance Criteria

- Zero or one runtime task is generated.
- The model receives no file paths except error text already present in the summary.
