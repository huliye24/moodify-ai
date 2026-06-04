#!/usr/bin/env python3
"""Validate and select AEP worker outputs.

This script keeps cheap-model workers bounded: each output must match an input
task, keep the same task_id and loop, and use the small decision schema.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
DEFAULT_REQUIRED = ["task_id", "loop", "severity", "reason", "next_action", "needs_human_review"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                records.append({"__invalid_json__": stripped, "__line__": lineno, "__error__": str(exc)})
                continue
            if isinstance(value, dict):
                value.setdefault("__line__", lineno)
                records.append(value)
            else:
                records.append({"__invalid_json__": stripped, "__line__": lineno, "__error__": "line is not a JSON object"})
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            clean = {k: v for k, v in record.items() if k != "__line__"}
            f.write(json.dumps(clean, ensure_ascii=False, sort_keys=True) + "\n")


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "__line__"}


def load_schema(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"required": DEFAULT_REQUIRED, "properties": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_output(
    output: dict[str, Any],
    task_by_id: dict[str, dict[str, Any]],
    schema: dict[str, Any],
) -> tuple[bool, str]:
    if "__invalid_json__" in output:
        return False, output.get("__error__", "invalid JSON")

    required = schema.get("required") or DEFAULT_REQUIRED
    missing = [field for field in required if field not in output]
    if missing:
        return False, f"missing required fields: {', '.join(missing)}"

    task_id = str(output.get("task_id", ""))
    task = task_by_id.get(task_id)
    if task is None:
        return False, "task_id does not match any input task"

    if output.get("loop") != task.get("loop"):
        return False, "loop does not match input task"

    severity = output.get("severity")
    allowed_severity = (
        schema.get("properties", {})
        .get("severity", {})
        .get("enum", ["low", "medium", "high"])
    )
    if severity not in allowed_severity:
        return False, "unsupported severity"

    for field in ("reason", "next_action"):
        value = output.get(field)
        if not isinstance(value, str) or not value.strip():
            return False, f"{field} must be a non-empty string"
        max_length = schema.get("properties", {}).get(field, {}).get("maxLength")
        if max_length and len(value) > int(max_length):
            return False, f"{field} exceeds maxLength {max_length}"

    if not isinstance(output.get("needs_human_review"), bool):
        return False, "needs_human_review must be boolean"

    return True, "valid"


def cmd_validate(args: argparse.Namespace) -> int:
    tasks = load_jsonl(args.tasks)
    outputs = load_jsonl(args.outputs)
    schema = load_schema(args.schema)
    task_by_id = {str(task.get("task_id")): task for task in tasks if task.get("task_id")}

    valid: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_valid: set[str] = set()

    for output in outputs:
        ok, reason = validate_output(output, task_by_id, schema)
        if ok:
            task_id = str(output["task_id"])
            if task_id in seen_valid:
                rejected.append({"output": output, "reject_reason": "duplicate valid output for task_id"})
                continue
            seen_valid.add(task_id)
            valid.append(output)
        else:
            rejected.append({"output": output, "reject_reason": reason})

    write_jsonl(args.valid, valid)
    write_jsonl(args.rejected, rejected)
    print(json.dumps({"valid": len(valid), "rejected": len(rejected)}, sort_keys=True))
    return 0 if not rejected else 2


def _selection_key(record: dict[str, Any], loop_order: dict[str, int]) -> tuple[int, int, str]:
    severity = SEVERITY_RANK.get(str(record.get("severity")), 99)
    loop = str(record.get("loop", ""))
    return (severity, loop_order.get(loop, 99), str(record.get("task_id", "")))


def cmd_select(args: argparse.Namespace) -> int:
    records = load_jsonl(args.valid)
    loop_order: dict[str, int] = {}
    for record in records:
        loop = str(record.get("loop", ""))
        if loop and loop not in loop_order:
            loop_order[loop] = len(loop_order)

    sorted_records = sorted(records, key=lambda record: _selection_key(record, loop_order))
    selected: list[dict[str, Any]] = []
    used_loops: set[str] = set()

    for record in sorted_records:
        loop = str(record.get("loop", ""))
        if loop not in used_loops:
            selected.append(record)
            used_loops.add(loop)
        if len(selected) >= args.limit:
            break

    if len(selected) < args.limit:
        selected_ids = {str(record.get("task_id")) for record in selected}
        for record in sorted_records:
            if str(record.get("task_id")) in selected_ids:
                continue
            selected.append(record)
            if len(selected) >= args.limit:
                break

    result = {"limit": args.limit, "selected": [clean_record(record) for record in selected]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": len(selected)}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AEP worker protocol utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate worker model outputs")
    validate.add_argument("--tasks", type=Path, required=True)
    validate.add_argument("--outputs", type=Path, required=True)
    validate.add_argument("--schema", type=Path)
    validate.add_argument("--valid", type=Path, required=True)
    validate.add_argument("--rejected", type=Path, required=True)
    validate.set_defaults(func=cmd_validate)

    select = subparsers.add_parser("select", help="select the next bounded optimization tasks")
    select.add_argument("--valid", type=Path, required=True)
    select.add_argument("--out", type=Path, required=True)
    select.add_argument("--limit", type=int, default=3)
    select.set_defaults(func=cmd_select)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
