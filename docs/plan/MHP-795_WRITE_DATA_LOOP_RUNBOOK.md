# MHP-795: Write Data Loop Runbook

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P5 (Systemization)
**Depends on**: MHP-794
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Provide a runbook that extracts a usable optimization dataset from last night's run and converts it into DeepSeek v4 micro-tasks.

This runbook follows `docs/protocol/AEP_WORKER_PROTOCOL.md`.

## DeepSeek v4 Constraint

DeepSeek should not inspect the repository. It receives one JSONL line, makes one decision, and returns one JSON object.

Rules:

- one record per request;
- no cross-record reasoning;
- no code patches;
- JSON output only;
- reason length under 180 characters;
- next action length under 220 characters.

## Runbook

```bash
cd /home/ubuntu/moodify-mainline
SOURCE=${SOURCE:-outputs/20260605_000141/summary.json}
RUN_ID=data_loop_014_$(date -u +%Y%m%d_%H%M%S)
OUT=reports/echain_moodify_data_loop_014/$RUN_ID
mkdir -p "$OUT"
export SOURCE OUT

python3 - <<'PY'
import json
import os
from pathlib import Path

source = os.environ["SOURCE"]
out = Path(os.environ["OUT"])
summary = json.load(open(source))
tasks = summary.get("tasks", [])
rows = []
for t in tasks:
    pseudo = t.get("pseudo_delta_mrs")
    open_delta = t.get("delta_mrs_open_v031")
    disagreement = None
    if pseudo is not None and open_delta is not None:
        disagreement = (pseudo >= 0) != (open_delta >= 0)
    rows.append({
        "task_id": t.get("task_id"),
        "sample_id": t.get("sample_id"),
        "preset": t.get("preset"),
        "status": t.get("status"),
        "pseudo_delta_mrs": pseudo,
        "delta_mrs_open_v031": open_delta,
        "score_direction_disagreement": disagreement,
        "mrs_open_flags": t.get("mrs_open_flags"),
        "recommended_loop": (
            "runtime_reliability" if summary.get("fatal_error") else
            "scoring_calibration" if disagreement else
            "craft_preset_selection" if t.get("mrs_open_flags") else
            "operator_report"
        ),
    })

snapshot = {
    "source_run": summary.get("run_id"),
    "source_file": source,
    "success": summary.get("success"),
    "failed": summary.get("failed"),
    "fatal_error": summary.get("fatal_error"),
    "tasks": rows,
}
(out / "last_night_metric_snapshot.json").write_text(
    json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
)

task_lines = []
run_id = summary.get("run_id")
fatal = summary.get("fatal_error")
failed = summary.get("failed") or 0

if fatal or failed:
    task_lines.append({
        "task_id": f"{run_id}:runtime",
        "loop": "runtime_reliability",
        "input_type": "run_record",
        "data": {
            "run_id": run_id,
            "success": summary.get("success"),
            "failed": failed,
            "fatal_error": fatal,
        },
        "instruction": "Classify runtime severity and give one next action.",
    })

for row in rows:
    if row["score_direction_disagreement"]:
        task_lines.append({
            "task_id": f"{row['task_id']}:score",
            "loop": "scoring_calibration",
            "input_type": "task_record",
            "data": {
                "task_id": row["task_id"],
                "sample_id": row["sample_id"],
                "preset": row["preset"],
                "pseudo_delta_mrs": row["pseudo_delta_mrs"],
                "delta_mrs_open_v031": row["delta_mrs_open_v031"],
                "score_direction_disagreement": row["score_direction_disagreement"],
            },
            "instruction": "Classify scoring disagreement severity and give one calibration action.",
        })
    if row["mrs_open_flags"]:
        task_lines.append({
            "task_id": f"{row['task_id']}:craft",
            "loop": "craft_preset_selection",
            "input_type": "task_record",
            "data": {
                "task_id": row["task_id"],
                "sample_id": row["sample_id"],
                "preset": row["preset"],
                "delta_mrs_open_v031": row["delta_mrs_open_v031"],
                "mrs_open_flags": row["mrs_open_flags"],
            },
            "instruction": "Classify preset risk and give one craft/preset action.",
        })

task_lines.append({
    "task_id": f"{run_id}:operator",
    "loop": "operator_report",
    "input_type": "run_summary",
    "data": {
        "run_id": run_id,
        "task_count": len(rows),
        "fatal_error": fatal,
        "disagreement_count": sum(1 for row in rows if row["score_direction_disagreement"]),
        "flagged_count": sum(1 for row in rows if row["mrs_open_flags"]),
    },
    "instruction": "Choose PASS, HOLD, or REWORK and give one next MHP direction.",
})

with (out / "deepseek_tasks.jsonl").open("w") as f:
    for item in task_lines:
        f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")

(out / "deepseek_prompt.md").write_text("""You are processing one Moodify optimization micro-task.

Return JSON only.
Do not write markdown.
Do not inspect code.
Do not invent missing fields.
Use only the input record.

Allowed loop values:
- runtime_reliability
- scoring_calibration
- craft_preset_selection
- operator_report

Allowed severity values:
- low
- medium
- high

Output schema:
{
  "task_id": "copy from input",
  "loop": "copy from input",
  "severity": "low|medium|high",
  "reason": "short reason under 180 chars",
  "next_action": "one concrete action under 220 chars",
  "needs_human_review": true
}
""")

(out / "expected_output_schema.json").write_text(json.dumps({
    "type": "object",
    "required": ["task_id", "loop", "severity", "reason", "next_action", "needs_human_review"],
    "properties": {
        "task_id": {"type": "string"},
        "loop": {"enum": ["runtime_reliability", "scoring_calibration", "craft_preset_selection", "operator_report"]},
        "severity": {"enum": ["low", "medium", "high"]},
        "reason": {"type": "string", "maxLength": 180},
        "next_action": {"type": "string", "maxLength": 220},
        "needs_human_review": {"type": "boolean"},
    },
}, ensure_ascii=False, indent=2) + "\n")

print(out)
PY
```

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/last_night_metric_snapshot.json`

`reports/echain_moodify_data_loop_014/{RUN_ID}/deepseek_tasks.jsonl`

`reports/echain_moodify_data_loop_014/{RUN_ID}/deepseek_prompt.md`

`reports/echain_moodify_data_loop_014/{RUN_ID}/expected_output_schema.json`

## DeepSeek Call Pattern

Send this pair for each JSONL line:

```text
System prompt: contents of deepseek_prompt.md
User input: one line from deepseek_tasks.jsonl
```

Expected output example:

```json
{
  "task_id": "20260605_000141:operator",
  "loop": "operator_report",
  "severity": "medium",
  "reason": "Run completed but has scoring disagreements and flagged presets.",
  "next_action": "Run scoring calibration and craft/preset review before accepting this batch.",
  "needs_human_review": true
}
```

## Validate and Select

After writing DeepSeek outputs to `model_outputs.jsonl`, run:

```bash
python3 scripts/aep_worker_protocol.py validate \
  --tasks "$OUT/deepseek_tasks.jsonl" \
  --outputs "$OUT/model_outputs.jsonl" \
  --schema "$OUT/expected_output_schema.json" \
  --valid "$OUT/deepseek_decisions_validated.jsonl" \
  --rejected "$OUT/rejected_outputs.jsonl"

python3 scripts/aep_worker_protocol.py select \
  --valid "$OUT/deepseek_decisions_validated.jsonl" \
  --out "$OUT/next_three_optimization_tasks.json"
```

## Acceptance Criteria

- The snapshot exists.
- `deepseek_tasks.jsonl` exists.
- Each DeepSeek task has one loop only.
- Score-direction disagreement is explicit.
- Model output can be validated against `expected_output_schema.json`.
- `next_three_optimization_tasks.json` contains no more than three items.
