#!/usr/bin/env python3
"""Compare temporal-texture audit reports and fail on newly introduced debt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    if report.get("schema_version") != "1.0" or "findings" not in report:
        raise ValueError(f"Unsupported report format: {path}")
    return report


def finding_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["fingerprint"]: item for item in report["findings"]}


def render_markdown(
    baseline_path: Path,
    current_path: Path,
    new_items: list[dict[str, Any]],
    resolved_items: list[dict[str, Any]],
) -> str:
    lines = [
        "# Temporal Texture Regression Guard",
        "",
        f"- Baseline: `{baseline_path}`",
        f"- Current: `{current_path}`",
        f"- New findings: **{len(new_items)}**",
        f"- Resolved findings: **{len(resolved_items)}**",
        "",
        "## New findings",
        "",
        "| Severity | Rule | Location | Message |",
        "|---|---|---|---|",
    ]
    for item in sorted(new_items, key=lambda x: (x["severity"], x["path"], x["line"], x["rule"])):
        message = item["message"].replace("|", "\\|")
        lines.append(f"| {item['severity'].upper()} | `{item['rule']}` | `{item['path']}:{item['line']}` | {message} |")
    if not new_items:
        lines.append("| - | - | - | No new findings |")
    lines.extend(["", "## Resolved findings", ""])
    if resolved_items:
        for item in sorted(resolved_items, key=lambda x: (x["path"], x["line"], x["rule"])):
            lines.append(f"- `{item['path']}:{item['line']}` `{item['rule']}` — {item['message']}")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fail-on-new-warnings", action="store_true")
    args = parser.parse_args()

    try:
        baseline = load_report(args.baseline)
        current = load_report(args.current)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Guard input error: {exc}")
        return 2

    before = finding_map(baseline)
    after = finding_map(current)
    new_items = [item for key, item in after.items() if key not in before]
    resolved_items = [item for key, item in before.items() if key not in after]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(args.baseline, args.current, new_items, resolved_items), encoding="utf-8")

    new_errors = [item for item in new_items if item["severity"] == "error"]
    new_warnings = [item for item in new_items if item["severity"] == "warning"]
    print(json.dumps({
        "new": len(new_items),
        "new_errors": len(new_errors),
        "new_warnings": len(new_warnings),
        "resolved": len(resolved_items),
    }))
    if new_errors or (args.fail_on_new_warnings and new_warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
