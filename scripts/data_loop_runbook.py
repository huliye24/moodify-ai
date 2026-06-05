#!/usr/bin/env python3
"""Extract a usable optimization dataset from last night's run and convert it into
DeepSeek v4 micro-tasks.

Part of ECHAIN-MOODIFY-DATA-LOOP-014 / MHP-795.
Follows docs/protocol/AEP_WORKER_PROTOCOL.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Allowed loops for DeepSeek v4 worker — one per micro-task.
ALLOWED_LOOPS = [
    "runtime_reliability",
    "scoring_calibration",
    "craft_preset_selection",
    "operator_report",
]

OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["task_id", "loop", "severity", "reason", "next_action", "needs_human_review"],
    "properties": {
        "task_id": {"type": "string"},
        "loop": {"enum": ALLOWED_LOOPS},
        "severity": {"enum": ["low", "medium", "high"]},
        "reason": {"type": "string", "maxLength": 180},
        "next_action": {"type": "string", "maxLength": 220},
        "needs_human_review": {"type": "boolean"},
    },
}

DEEPSEEK_PROMPT = """You are processing one Moodify optimization micro-task.

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
"""


def load_summary(source: Path) -> dict[str, Any]:
    """Load the night-run summary.json."""
    with source.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert each task entry into a metric row with disagreement detection."""
    rows: list[dict[str, Any]] = []
    tasks = summary.get("tasks", [])
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
    return rows


def build_snapshot(summary: dict[str, Any], rows: list[dict[str, Any]], source_path: str) -> dict[str, Any]:
    """Build the last-night metric snapshot."""
    return {
        "source_run": summary.get("run_id"),
        "source_file": source_path,
        "success": summary.get("success"),
        "failed": summary.get("failed"),
        "fatal_error": summary.get("fatal_error"),
        "tasks": rows,
    }


def build_deepseek_tasks(summary: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert rows into DeepSeek v4 worker micro-tasks (one record per request)."""
    task_lines: list[dict[str, Any]] = []
    run_id = summary.get("run_id")
    fatal = summary.get("fatal_error")
    failed = summary.get("failed") or 0

    # Runtime reliability task — always emitted if there's a fatal error or failures.
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
        # Scoring calibration — when pseudo MRS and MRS Open disagree on direction.
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
        # Craft/preset selection — when penalty flags are present.
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

    # Operator report — always emitted as the final synthesis task.
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

    return task_lines


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in records:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run(source: Path, out_dir: Path) -> int:
    """Execute the data loop runbook: produce snapshot, tasks, prompt, schema."""
    summary = load_summary(source)
    rows = build_rows(summary)
    snapshot = build_snapshot(summary, rows, str(source))
    deepseek_tasks = build_deepseek_tasks(summary, rows)

    snapshot_path = out_dir / "last_night_metric_snapshot.json"
    tasks_path = out_dir / "deepseek_tasks.jsonl"
    prompt_path = out_dir / "deepseek_prompt.md"
    schema_path = out_dir / "expected_output_schema.json"

    write_json(snapshot_path, snapshot)
    write_jsonl(tasks_path, deepseek_tasks)
    write_text(prompt_path, DEEPSEEK_PROMPT)
    write_json(schema_path, OUTPUT_SCHEMA)

    print(f"Snapshot : {snapshot_path}")
    print(f"Tasks    : {tasks_path}  ({len(deepseek_tasks)} lines)")
    print(f"Prompt   : {prompt_path}")
    print(f"Schema   : {schema_path}")
    print(json.dumps({
        "tasks": len(deepseek_tasks),
        "disagreement_count": sum(1 for row in rows if row["score_direction_disagreement"]),
        "flagged_count": sum(1 for row in rows if row["mrs_open_flags"]),
        "fatal_error": bool(summary.get("fatal_error")),
    }, sort_keys=True))

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Data Loop Runbook — extract night metrics and build DeepSeek micro-tasks"
    )
    parser.add_argument(
        "--source", type=Path,
        default=Path("outputs/20260605_000141/summary.json"),
        help="Path to last night's summary.json",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=None,
        help="Output directory (default: reports/echain_moodify_data_loop_014/{RUN_ID})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source = args.source.resolve()

    if args.out_dir is None:
        import datetime
        run_id = f"data_loop_014_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        out_dir = Path("reports/echain_moodify_data_loop_014") / run_id
    else:
        out_dir = args.out_dir

    if not source.exists():
        print(f"Error: source file not found: {source}", file=sys.stderr)
        return 1

    return run(source, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
