# AEP Worker Pack Template

Use this template when adding cheap-model worker tasks to any E-Chain.

## Directory

```text
reports/aep_worker/{chain_id}/{run_id}/
```

## Required Files

### `tasks.jsonl`

One worker task per line.

```json
{"task_id":"CHAIN:item-001","loop":"loop_name","input_type":"record","data":{},"instruction":"Do one bounded action."}
```

### `prompt.md`

```text
You are processing one Moodify AEP worker task.

Return JSON only.
Use only the input record.
Do not inspect the repository.
Do not write markdown.
Do not propose more than one next action.
```

### `expected_output_schema.json`

```json
{
  "type": "object",
  "required": ["task_id", "loop", "severity", "reason", "next_action", "needs_human_review"],
  "properties": {
    "task_id": {"type": "string"},
    "loop": {"type": "string"},
    "severity": {"enum": ["low", "medium", "high"]},
    "reason": {"type": "string", "maxLength": 180},
    "next_action": {"type": "string", "maxLength": 220},
    "needs_human_review": {"type": "boolean"}
  }
}
```

### `model_outputs.jsonl`

One raw model response JSON object per line.

### `decisions_validated.jsonl`

Written by the validator.

### `rejected_outputs.jsonl`

Written by the validator when output needs a one-line rerun.

### `next_three_tasks.json`

Written by the selector.

## Standard Commands

```bash
python3 scripts/aep_worker_protocol.py validate \
  --tasks reports/aep_worker/{chain_id}/{run_id}/tasks.jsonl \
  --outputs reports/aep_worker/{chain_id}/{run_id}/model_outputs.jsonl \
  --schema reports/aep_worker/{chain_id}/{run_id}/expected_output_schema.json \
  --valid reports/aep_worker/{chain_id}/{run_id}/decisions_validated.jsonl \
  --rejected reports/aep_worker/{chain_id}/{run_id}/rejected_outputs.jsonl

python3 scripts/aep_worker_protocol.py select \
  --valid reports/aep_worker/{chain_id}/{run_id}/decisions_validated.jsonl \
  --out reports/aep_worker/{chain_id}/{run_id}/next_three_tasks.json
```
