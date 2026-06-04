# MHP-801: Merge DeepSeek JSON Outputs

**Status**: planned
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P5 (Systemization)
**Depends on**: MHP-797
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Merge DeepSeek outputs without trusting free-form text.

Use `scripts/aep_worker_protocol.py validate` for the first implementation.

## Input

- `deepseek_tasks.jsonl`
- one model output JSON object per line
- `expected_output_schema.json`

## Validation

Reject a model output if:

- it is not valid JSON;
- `task_id` does not match an input task;
- `loop` does not match the input task;
- `severity` is not `low`, `medium`, or `high`;
- it includes more than one action.

## Output

`deepseek_decisions_validated.jsonl`

## Acceptance Criteria

- Valid outputs are mergeable by script.
- Invalid outputs are rerunnable one line at a time.
