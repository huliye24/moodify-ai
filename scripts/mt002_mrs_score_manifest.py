#!/usr/bin/env python3
"""Score a Runtime manifest with MRS Open v0.3.1.

This is MT-002's first production-facing scoring bridge: it keeps MRS
optional and post-run, reads an existing Runtime manifest, scores before/after
audio, and writes JSONL/CSV/Markdown evidence without mutating Runtime outputs.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from moodify_runtime.metrics import compute_mrs_open_v031  # noqa: E402
from moodify_runtime.utils import utc_now_iso  # noqa: E402

AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}
MRS_VERSION = "mrs_open_v031"


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _find_output_audio(output_dir: str) -> str | None:
    if not output_dir:
        return None
    root = Path(output_dir)
    if not root.exists():
        return None
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES)
    return str(files[0]) if files else None


def _score_cached(path: str, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if path not in cache:
        cache[path] = compute_mrs_open_v031(path)
    return cache[path]


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _record_from_row(row: dict[str, str], run_id: str, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    input_path = row.get("input_path", "")
    output_path = _find_output_audio(row.get("output_dir", ""))
    created_at = utc_now_iso()
    base = {
        "run_id": run_id,
        "source_runtime_run_id": row.get("run_id", ""),
        "task_id": row.get("task_id", ""),
        "sample_id": row.get("sample_id", ""),
        "input_path": input_path,
        "output_path": output_path or "",
        "preset": row.get("preset", ""),
        "mrs_version": MRS_VERSION,
        "mrs_score": None,
        "mrs_before": None,
        "mrs_delta": None,
        "d_real_before": None,
        "d_real_after": None,
        "subscores": {},
        "penalties": {},
        "penalty_flags": [],
        "status": "failed",
        "error": None,
        "created_at": created_at,
    }
    if not input_path or not Path(input_path).exists():
        base["error"] = f"missing_input: {input_path}"
        return base
    if not output_path or not Path(output_path).exists():
        base["error"] = f"missing_output: {row.get('output_dir', '')}"
        return base

    before = _score_cached(input_path, cache)
    after = _score_cached(output_path, cache)
    before_score = _float_or_none(before.get("mrs_open"))
    after_score = _float_or_none(after.get("mrs_open"))
    if before.get("error") or after.get("error") or before_score is None or after_score is None:
        base["error"] = after.get("error") or before.get("error") or "score_unavailable"
        base["subscores"] = after.get("subscores") or {}
        base["penalties"] = after.get("extra_penalties") or {}
        return base

    base.update({
        "mrs_score": after_score,
        "mrs_before": before_score,
        "mrs_delta": after_score - before_score,
        "d_real_before": before.get("d_real"),
        "d_real_after": after.get("d_real"),
        "subscores": after.get("subscores") or {},
        "penalties": after.get("extra_penalties") or {},
        "penalty_flags": after.get("penalty_flags") or [],
        "status": "completed",
        "error": None,
    })
    return base


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=False) + "\n")


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = ["run_id", "source_runtime_run_id", "task_id", "sample_id", "preset", "mrs_version", "mrs_before", "mrs_score", "mrs_delta", "d_real_before", "d_real_after", "penalty_flags", "status", "error", "input_path", "output_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["penalty_flags"] = ",".join(row.get("penalty_flags") or [])
            writer.writerow({k: row.get(k, "") for k in fields})


def _summary(records: list[dict[str, Any]], run_id: str, manifest: Path) -> dict[str, Any]:
    completed = [r for r in records if r.get("status") == "completed"]
    failed = [r for r in records if r.get("status") != "completed"]
    scores = [float(r["mrs_score"]) for r in completed if r.get("mrs_score") is not None]
    deltas = [float(r["mrs_delta"]) for r in completed if r.get("mrs_delta") is not None]
    per_preset: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in completed:
        grouped[str(r.get("preset", ""))].append(r)
    for preset, rows in grouped.items():
        preset_scores = [float(r["mrs_score"]) for r in rows if r.get("mrs_score") is not None]
        preset_deltas = [float(r["mrs_delta"]) for r in rows if r.get("mrs_delta") is not None]
        per_preset[preset] = {
            "count": len(rows),
            "mean_mrs": statistics.fmean(preset_scores) if preset_scores else None,
            "median_mrs": statistics.median(preset_scores) if preset_scores else None,
            "mean_delta": statistics.fmean(preset_deltas) if preset_deltas else None,
            "median_delta": statistics.median(preset_deltas) if preset_deltas else None,
        }
    flags = Counter(flag for r in completed for flag in (r.get("penalty_flags") or []))
    return {
        "run_id": run_id,
        "generated_at": utc_now_iso(),
        "source_manifest": str(manifest),
        "mrs_version": MRS_VERSION,
        "total_records": len(records),
        "completed": len(completed),
        "failed": len(failed),
        "unique_samples": len({r.get("sample_id") for r in records}),
        "score_min": min(scores) if scores else None,
        "score_median": statistics.median(scores) if scores else None,
        "score_mean": statistics.fmean(scores) if scores else None,
        "score_max": max(scores) if scores else None,
        "delta_median": statistics.median(deltas) if deltas else None,
        "delta_mean": statistics.fmean(deltas) if deltas else None,
        "per_preset": per_preset,
        "penalty_flags": dict(flags),
        "top_records": sorted(completed, key=lambda r: float(r["mrs_score"]), reverse=True)[:10],
        "bottom_records": sorted(completed, key=lambda r: float(r["mrs_score"]))[:10],
        "failed_examples": failed[:20],
        "decision": "PASS" if not failed and len(completed) == len(records) else "HOLD",
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        f"# MT-002 MRS Baseline Report - {summary['run_id']}",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Result",
        "",
        f"- Decision: `{summary['decision']}`",
        f"- MRS version: `{summary['mrs_version']}`",
        f"- Records: `{summary['completed']}/{summary['total_records']}` completed",
        f"- Unique samples: `{summary['unique_samples']}`",
        "",
        "## Distribution",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Min MRS | {_fmt(summary['score_min'])} |",
        f"| Median MRS | {_fmt(summary['score_median'])} |",
        f"| Mean MRS | {_fmt(summary['score_mean'])} |",
        f"| Max MRS | {_fmt(summary['score_max'])} |",
        f"| Median delta | {_fmt(summary['delta_median'])} |",
        f"| Mean delta | {_fmt(summary['delta_mean'])} |",
        "",
        "## Per Preset",
        "",
        "| Preset | Count | Median MRS | Mean MRS | Median Delta | Mean Delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for preset, item in sorted(summary["per_preset"].items()):
        lines.append(f"| {preset} | {item['count']} | {_fmt(item['median_mrs'])} | {_fmt(item['mean_mrs'])} | {_fmt(item['median_delta'])} | {_fmt(item['mean_delta'])} |")
    lines += ["", "## Top 10", "", "| Rank | Sample | Preset | MRS | Delta | Flags |", "|---:|---|---|---:|---:|---|"]
    for idx, record in enumerate(summary["top_records"], 1):
        flags = ",".join(record.get("penalty_flags") or []) or "-"
        lines.append(f"| {idx} | {record['sample_id']} | {record['preset']} | {_fmt(record['mrs_score'])} | {_fmt(record['mrs_delta'])} | {flags} |")
    lines += ["", "## Bottom 10", "", "| Rank | Sample | Preset | MRS | Delta | Flags |", "|---:|---|---|---:|---:|---|"]
    for idx, record in enumerate(summary["bottom_records"], 1):
        flags = ",".join(record.get("penalty_flags") or []) or "-"
        lines.append(f"| {idx} | {record['sample_id']} | {record['preset']} | {_fmt(record['mrs_score'])} | {_fmt(record['mrs_delta'])} | {flags} |")
    lines += ["", "## Penalty Flags", ""]
    if summary["penalty_flags"]:
        lines += ["| Flag | Count |", "|---|---:|"]
        for flag, count in sorted(summary["penalty_flags"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {flag} | {count} |")
    else:
        lines.append("No penalty flags.")
    if summary["failed_examples"]:
        lines += ["", "## Failed Examples", ""]
        for record in summary["failed_examples"]:
            lines.append(f"- `{record.get('task_id')}`: {record.get('error')}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a Runtime manifest with MRS Open v0.3.1")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default="reports/mt002_mrs_baseline")
    parser.add_argument("--expected-records", type=int, default=0)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    manifest = Path(args.manifest)
    output_dir = Path(args.output_dir) / args.run_id
    rows = _read_manifest(manifest)
    cache: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, 1):
        records.append(_record_from_row(row, args.run_id, cache))
        if idx == len(rows) or idx % 10 == 0:
            print(f"scored {idx}/{len(rows)} records", flush=True)
    summary = _summary(records, args.run_id, manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "mrs_score_records.jsonl", records)
    _write_csv(output_dir / "mrs_score_records.csv", records)
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(output_dir / "summary.md", summary)
    print(json.dumps({k: summary[k] for k in ["run_id", "mrs_version", "total_records", "completed", "failed", "unique_samples", "score_median", "delta_median", "decision"]}, ensure_ascii=False, indent=2))
    if args.expected_records and summary["total_records"] != args.expected_records:
        return 2
    if args.require_complete and summary["decision"] != "PASS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
