"""MHP-014: Aggregate Moodify Treatment Records into summary JSON and Markdown.

Usage:
  python scripts/v01_aggregate_treatment_records.py
  python scripts/v01_aggregate_treatment_records.py --input-dir treatment_records
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean


SCHEMA_VERSION = "0.1.0"
SUMMARY_TYPE = "moodify_treatment_record_summary"

PRESET_NAMES = ["warm_vocal", "clean_master", "wide_space"]


def load_records(input_dir: str) -> tuple[list[dict], list[dict]]:
    """Scan input_dir for JSON treatment records. Returns (records, errors)."""
    root = Path(input_dir)
    if not root.is_dir():
        print(f"  Input dir not found: {input_dir}. Creating empty summary.")
        return [], [{"error": f"directory not found: {input_dir}"}]

    files = sorted(f for f in root.iterdir() if f.suffix == ".json")
    if not files:
        print(f"  No JSON files found in {input_dir}.")
        return [], []

    records = []
    errors = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("record_type") != "moodify_treatment_record":
                continue
            data["_record_file"] = fp.name
            records.append(data)
        except Exception as e:
            errors.append({"file": fp.name, "error": str(e)})

    return records, errors


def extract_flat_record(rec: dict) -> dict:
    """Extract key fields from a treatment record into a flat dict."""
    delta = rec.get("delta_features", {})
    loudness = rec.get("loudness_match", {})
    fb = rec.get("human_feedback", {})

    return {
        "record_file": rec.get("_record_file", ""),
        "song_id": rec.get("song_id", ""),
        "preset": rec.get("preset", ""),
        "schema_version": rec.get("schema_version", ""),
        "rms_delta_db": delta.get("rms_delta_db"),
        "after_gain_match_db": loudness.get("after_gain_match_db"),
        "warning_level": loudness.get("warning_level"),
        "crest_delta": delta.get("crest_delta"),
        "dynamic_range_delta_db": delta.get("dynamic_range_delta_db"),
        "correlation_delta": delta.get("correlation_delta"),
        "presence_delta_db": delta.get("presence_delta_db"),
        "air_delta_db": delta.get("air_delta_db"),
        "feedback_status": fb.get("status", "unknown"),
        "better_than_before": fb.get("better_than_before"),
    }


def safe_mean(values: list) -> float | None:
    vals = [v for v in values if v is not None]
    return round(mean(vals), 2) if vals else None


def compute_preset_stats(flat_records: list[dict]) -> dict:
    """Group by preset and compute per-preset aggregates."""
    groups: dict[str, list[dict]] = {}
    for r in flat_records:
        p = r.get("preset", "unknown")
        groups.setdefault(p, []).append(r)

    result = {}
    for preset in PRESET_NAMES:
        items = groups.get(preset, [])
        if not items:
            continue

        fb_statuses = [r["feedback_status"] for r in items]
        better_vals = [r["better_than_before"] for r in items]

        avg_delta = {}
        for key in [
            "rms_delta_db", "crest_delta", "dynamic_range_delta_db",
            "correlation_delta", "presence_delta_db", "air_delta_db",
        ]:
            avg_delta[key] = safe_mean([r[key] for r in items])

        result[preset] = {
            "count": len(items),
            "avg_delta": avg_delta,
            "human_feedback": {
                "pending": fb_statuses.count("pending"),
                "completed": fb_statuses.count("completed"),
                "better_yes": better_vals.count(True) + better_vals.count("yes"),
                "better_no": better_vals.count(False) + better_vals.count("no"),
                "better_uncertain": better_vals.count("uncertain"),
            },
        }

    return result


def build_summary(flat_records: list[dict], errors: list[dict]) -> dict:
    preset_stats = compute_preset_stats(flat_records)

    summary_records = []
    for r in flat_records:
        summary_records.append({
            "record_file": r["record_file"],
            "song_id": r["song_id"],
            "preset": r["preset"],
            "rms_delta_db": r["rms_delta_db"],
            "after_gain_match_db": r["after_gain_match_db"],
            "warning_level": r["warning_level"],
            "crest_delta": r["crest_delta"],
            "dynamic_range_delta_db": r["dynamic_range_delta_db"],
            "correlation_delta": r["correlation_delta"],
            "presence_delta_db": r["presence_delta_db"],
            "air_delta_db": r["air_delta_db"],
            "feedback_status": r["feedback_status"],
            "better_than_before": r["better_than_before"],
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "summary_type": SUMMARY_TYPE,
        "record_count": len(flat_records),
        "presets": preset_stats,
        "records": summary_records,
        "errors": errors,
    }


def _fmt(val, prec=2) -> str:
    if val is None:
        return "—"
    return f"{val:+.{prec}f}"


def write_summary_md(summary: dict, out_path: str):
    presets_data = summary.get("presets", {})
    records_list = summary.get("records", [])
    fb_pending = sum(1 for r in records_list if r["feedback_status"] == "pending")
    fb_done = sum(1 for r in records_list if r["feedback_status"] == "completed")

    lines = [
        "# Moodify Treatment Record Summary",
        "",
        "## Overview",
        "",
        f"- **Total records**: {summary['record_count']}",
        f"- **Presets**: {', '.join(presets_data.keys()) or 'none'}",
        f"- **Pending feedback**: {fb_pending}",
        f"- **Completed feedback**: {fb_done}",
        "",
        "## Preset Summary",
        "",
        "| Preset | Count | Avg RMS Δ | Avg Crest Δ | Avg DynRange Δ | "
        "Avg Corr Δ | Avg Presence Δ | Avg Air Δ | FB Pending | FB Done |",
        "|--------|------:|----------:|------------:|---------------:|"
        "----------:|---------------:|---------:|-----------:|--------:|",
    ]

    for preset in PRESET_NAMES:
        if preset not in presets_data:
            continue
        s = presets_data[preset]
        fd = s["human_feedback"]
        ad = s["avg_delta"]
        lines.append(
            f"| {preset} | {s['count']} | {_fmt(ad.get('rms_delta_db'))} | "
            f"{_fmt(ad.get('crest_delta'))} | {_fmt(ad.get('dynamic_range_delta_db'))} | "
            f"{_fmt(ad.get('correlation_delta'))} | {_fmt(ad.get('presence_delta_db'))} | "
            f"{_fmt(ad.get('air_delta_db'))} | {fd['pending']} | {fd['completed']} |"
        )

    lines += [
        "",
        "## Records",
        "",
        "| Record | Song ID | Preset | RMS Δ | Match Gain | Warning | "
        "Crest Δ | DynRange Δ | Corr Δ | Presence Δ | Air Δ | Feedback | Better? |",
        "|--------|---------|--------|------:|-----------:|--------:|"
        "--------:|-----------:|-------:|-----------:|------:|---------:|--------:|",
    ]

    for r in records_list:
        fb = r["feedback_status"]
        btb = r["better_than_before"]
        btb_str = {True: "yes", False: "no", "yes": "yes", "no": "no",
                   "uncertain": "uncertain"}.get(btb, str(btb) if btb else "—")
        lines.append(
            f"| {r['record_file']} | {r['song_id']} | {r['preset']} | "
            f"{_fmt(r['rms_delta_db'])} | {_fmt(r['after_gain_match_db'])} | "
            f"{r['warning_level']} | {_fmt(r['crest_delta'])} | "
            f"{_fmt(r['dynamic_range_delta_db'])} | {_fmt(r['correlation_delta'])} | "
            f"{_fmt(r['presence_delta_db'])} | {_fmt(r['air_delta_db'])} | "
            f"{fb} | {btb_str} |"
        )

    lines += [
        "",
        "## Human Feedback Status",
        "",
        "| Preset | Pending | Completed | Better Yes | Better No | Uncertain |",
        "|--------|--------:|----------:|-----------:|----------:|----------:|",
    ]

    for preset in PRESET_NAMES:
        if preset not in presets_data:
            continue
        fd = presets_data[preset]["human_feedback"]
        lines.append(
            f"| {preset} | {fd['pending']} | {fd['completed']} | "
            f"{fd['better_yes']} | {fd['better_no']} | {fd['better_uncertain']} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "This file is generated from local Treatment Records.",
        "It is not a database, not a cloud data layer, and not a trained model.",
        "It is the first aggregation layer for future adaptive preset logic.",
    ]

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="MHP-014: Aggregate Moodify Treatment Records"
    )
    parser.add_argument("--input-dir", default="treatment_records",
                        help="Directory containing treatment record JSONs")
    parser.add_argument("--output-json", default="treatment_records/summary.json",
                        help="Output path for summary JSON")
    parser.add_argument("--output-md", default="treatment_records/summary.md",
                        help="Output path for summary Markdown")
    args = parser.parse_args()

    print(f"\nMHP-014 Treatment Record Aggregator")
    print(f"  Input:  {args.input_dir}")
    print(f"  Output: {args.output_json}, {args.output_md}\n")

    records, errors = load_records(args.input_dir)
    print(f"  Records loaded: {len(records)}")

    if errors:
        for e in errors:
            print(f"  ERROR: {e}")

    flat = [extract_flat_record(r) for r in records]
    summary = build_summary(flat, errors)

    # Write JSON
    json_path = Path(args.output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  summary.json ({summary['record_count']} records, "
          f"{len(summary['presets'])} presets)")

    # Write MD
    write_summary_md(summary, args.output_md)
    print(f"  summary.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
