#!/usr/bin/env python3
"""DeepSeek v4 worker transport layer for Moodify AEP worker protocol.

One record per call, env-configured auth, dry-run mode, schema validation.
Part of ECHAIN-MOODIFY-DEEPSEEK-API-015 / MHP-899.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 120


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def validate_output(output: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = []
    required = schema.get("required", [])
    for field in required:
        if field not in output:
            errors.append(f"missing required field: {field}")
    props = schema.get("properties", {})
    for field, spec in props.items():
        if field not in output:
            continue
        value = output[field]
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{field}: {value!r} not in {spec['enum']}")
        if spec.get("type") == "string" and not isinstance(value, str):
            errors.append(f"{field}: expected string, got {type(value).__name__}")
        if spec.get("type") == "boolean" and not isinstance(value, bool):
            errors.append(f"{field}: expected bool, got {type(value).__name__}")
        if "maxLength" in spec and isinstance(value, str) and len(value) > spec["maxLength"]:
            errors.append(f"{field}: length {len(value)} exceeds max {spec['maxLength']}")
    if schema.get("additionalProperties") is False:
        allowed = set(props)
        extra = set(output) - allowed
        if extra:
            errors.append(f"additional properties not allowed: {extra}")
    return errors


def call_deepseek(
    system_prompt: str,
    user_input: dict[str, Any],
    api_key: str,
    base_url: str,
    model: str,
    timeout: int,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_input, ensure_ascii=False)},
        ],
        "temperature": 0.0,
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    body = resp.json()
    content = body["choices"][0]["message"]["content"]
    return json.loads(content)


def process_tasks(
    tasks: list[dict[str, Any]],
    system_prompt: str,
    output_schema: dict[str, Any],
    api_key: str,
    base_url: str,
    model: str,
    timeout: int,
    dry_run: bool,
    out_dir: Path,
) -> dict[str, Any]:
    validated: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for i, task in enumerate(tasks):
        task_id = task.get("task_id", f"task_{i}")
        if dry_run:
            validated.append({
                "task_id": task_id,
                "loop": task.get("loop", ""),
                "severity": "low",
                "reason": "dry-run: no API call",
                "next_action": "dry-run: validate input and proceed",
                "needs_human_review": True,
            })
            continue

        try:
            output = call_deepseek(system_prompt, task, api_key, base_url, model, timeout)
            errors = validate_output(output, output_schema)
            if errors:
                rejected.append({"task_id": task_id, "errors": errors, "output": output})
            else:
                validated.append(output)
        except Exception as exc:
            rejected.append({"task_id": task_id, "error": str(exc)})

    write_jsonl(out_dir / "model_outputs.jsonl", validated)
    write_jsonl(out_dir / "rejected_outputs.jsonl", rejected)

    return {
        "total": len(tasks),
        "validated": len(validated),
        "rejected": len(rejected),
        "dry_run": dry_run,
        "outputs_path": str(out_dir / "model_outputs.jsonl"),
        "rejected_path": str(out_dir / "rejected_outputs.jsonl"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DeepSeek v4 worker transport client")
    parser.add_argument("--task-file", type=Path, required=True, help="JSONL task file")
    parser.add_argument("--prompt-file", type=Path, required=True, help="System prompt markdown file")
    parser.add_argument("--schema-file", type=Path, default=None, help="Expected output JSON schema")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without API call")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="API timeout seconds")
    args = parser.parse_args(argv)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)

    if not args.dry_run and not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set. Use --dry-run or set the env var.", file=sys.stderr)
        return 1

    tasks = load_jsonl(args.task_file)
    if not tasks:
        print("ERROR: no tasks found in task file", file=sys.stderr)
        return 1

    system_prompt = args.prompt_file.read_text(encoding="utf-8")
    schema = load_json(args.schema_file) if args.schema_file else {}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = process_tasks(
        tasks, system_prompt, schema,
        api_key, base_url, model, args.timeout,
        args.dry_run, args.output_dir,
    )

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        **result,
    }
    summary_path = args.output_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
