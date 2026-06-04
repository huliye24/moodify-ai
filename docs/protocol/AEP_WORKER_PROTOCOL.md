# AEP Worker Protocol

## Purpose

AEP Worker Protocol lets Moodify use cheap models such as DeepSeek v4 as bounded execution workers.

The worker does not own project direction. It only processes atomic records prepared by the architect layer.

```text
architect layer -> JSONL worker tasks -> cheap model outputs -> validator -> merged decisions -> next tasks
```

## Roles

### Architect Layer

Usually Codex.

Responsibilities:

- define the E-Chain, NEM, and MHP boundary;
- choose input artifacts;
- create JSONL worker tasks;
- write the fixed prompt and output schema;
- validate and merge model outputs;
- select tasks worth implementing.

### Worker Layer

Usually DeepSeek v4.

Responsibilities:

- read one JSONL task;
- use only the fields in that task;
- return one JSON object;
- avoid repository-wide reasoning;
- avoid code edits;
- avoid project-direction decisions.

### Judge Layer

Usually scripts plus Codex.

Responsibilities:

- reject malformed output;
- reject outputs that change `task_id` or `loop`;
- merge valid decisions;
- rank decisions by severity;
- cap the next-action list.

## Worker Contract

Every model call follows this shape:

```text
system prompt: prompt.md
user input: one line from tasks.jsonl
model output: one JSON object
```

Do not send multiple JSONL lines in one worker call unless the task explicitly says batch mode is allowed.

## Worker Pack Layout

Each AEP worker pack should use this layout:

```text
reports/aep_worker/{chain_id}/{run_id}/
  tasks.jsonl
  prompt.md
  expected_output_schema.json
  model_outputs.jsonl
  decisions_validated.jsonl
  rejected_outputs.jsonl
  next_three_tasks.json
```

E-Chain-specific packs may add extra source snapshots, but the files above keep the protocol stable.

## Task JSONL Shape

Each line in `tasks.jsonl` should be small:

```json
{
  "task_id": "unique-id",
  "loop": "runtime_reliability",
  "input_type": "run_record",
  "data": {
    "run_id": "20260605_000141",
    "failed": 0,
    "fatal_error": "error text"
  },
  "instruction": "Classify runtime severity and give one next action."
}
```

Limits:

- one objective per task;
- no more than 12 source fields;
- no more than 3 allowed decisions;
- no repository paths unless the path itself is the evidence;
- no request to write or edit code.

## Output JSON Shape

Default worker output:

```json
{
  "task_id": "copy from input",
  "loop": "copy from input",
  "severity": "low",
  "reason": "short reason",
  "next_action": "one concrete action",
  "needs_human_review": true
}
```

Default required fields:

- `task_id`
- `loop`
- `severity`
- `reason`
- `next_action`
- `needs_human_review`

Allowed severities:

- `high`
- `medium`
- `low`

## Rejection Rules

Reject and rerun one worker call if:

- output is not valid JSON;
- output includes markdown;
- output changes `task_id`;
- output changes `loop`;
- output has an unsupported severity;
- output contains multiple recommendations;
- `reason` or `next_action` is too long;
- the worker claims to inspect files that were not in the input.

## Selection Rule

After validation:

1. Keep valid decisions only.
2. Sort by severity: `high`, then `medium`, then `low`.
3. Prefer loop diversity on ties.
4. Keep at most three tasks.
5. Send selected tasks back to the architect layer for implementation or a new MHP.

## Moodify E-Chain 014 Mapping

E-Chain 014 uses this protocol with:

- source snapshot: `last_night_metric_snapshot.json`;
- task file: `deepseek_tasks.jsonl`;
- prompt file: `deepseek_prompt.md`;
- schema file: `expected_output_schema.json`;
- validated decisions: `deepseek_decisions_validated.jsonl`;
- final selection: `next_three_optimization_tasks.json`.
