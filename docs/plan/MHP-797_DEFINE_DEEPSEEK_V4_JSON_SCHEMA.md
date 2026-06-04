# MHP-797: Define DeepSeek v4 JSON Schema

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P1 (Execution)
**Depends on**: MHP-795
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Keep model calls cheap and reliable by forcing every DeepSeek v4 response into one small JSON shape.

## Input Contract

Each request contains exactly one line from `deepseek_tasks.jsonl`.

Allowed `loop` values:

- `runtime_reliability`
- `scoring_calibration`
- `craft_preset_selection`
- `operator_report`

## Output Contract

```json
{
  "task_id": "copy from input",
  "loop": "copy from input",
  "severity": "low|medium|high",
  "reason": "short reason under 180 chars",
  "next_action": "one concrete action under 220 chars",
  "needs_human_review": true
}
```

## Rejection Rules

Reject and rerun the model call if:

- output is not valid JSON;
- output changes `task_id` or `loop`;
- output contains more than one recommendation;
- output includes markdown;
- `reason` or `next_action` exceeds the length limit.

## Acceptance Criteria

- The schema is small enough for cheap per-record calls.
- The schema supports all four E-Chain 014 loops.
- The output can be merged by script without manual cleanup.
