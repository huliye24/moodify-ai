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
        "correlation_delta": _first_present(delta, [
            "correlation_delta", "correlation_lr_delta", "lr_correlation_delta"]),
        "presence_delta_db": delta.get("presence_delta_db"),
        "air_delta_db": delta.get("air_delta_db"),
        "feedback_status": fb.get("status", "unknown"),
        "better_than_before": fb.get("better_than_before"),
        # Feedback scores
        "clarity": fb.get("clarity"),
        "warmth": fb.get("warmth"),
        "space": fb.get("space"),
        "harshness_control": fb.get("harshness_control"),
        "plastic_feel_control": fb.get("plastic_feel_control"),
        "artifact_control": fb.get("artifact_control"),
        "target_fit": fb.get("target_fit"),
        "volume_matched": fb.get("volume_matched"),
        "feedback_notes": fb.get("notes", ""),
    }


def _first_present(data: dict, keys: list[str], default=None):
    """Return the first key in `keys` that exists and is non-None in `data`."""
    for k in keys:
        v = data.get(k)
        if v is not None:
            return v
    return default


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

        # Feedback scores (completed only)
        completed = [r for r in items if r["feedback_status"] == "completed"]
        score_keys = [
            "clarity", "warmth", "space", "harshness_control",
            "plastic_feel_control", "artifact_control", "target_fit",
        ]
        feedback_scores = {}
        for sk in score_keys:
            values = [r[sk] for r in completed if r.get(sk) is not None]
            feedback_scores[f"avg_{sk}"] = round(mean(values), 1) if values else None

        completed_count = len(completed)
        total_count = len(items)
        better_yes_count = sum(
            1 for r in completed
            if r.get("better_than_before") in (True, "yes")
        )

        result[preset] = {
            "count": total_count,
            "avg_delta": avg_delta,
            "human_feedback": {
                "pending": fb_statuses.count("pending"),
                "completed": fb_statuses.count("completed"),
                "better_yes": better_vals.count(True) + better_vals.count("yes"),
                "better_no": better_vals.count(False) + better_vals.count("no"),
                "better_uncertain": better_vals.count("uncertain"),
            },
            "feedback_scores": feedback_scores,
            "feedback_quality": {
                "feedback_coverage": round(completed_count / total_count, 2) if total_count else 0.0,
                "better_rate": round(better_yes_count / completed_count, 2) if completed_count else None,
                "completed_count": completed_count,
                "pending_count": total_count - completed_count,
                "better_yes_count": better_yes_count,
                "better_no_count": sum(
                    1 for r in completed
                    if r.get("better_than_before") in (False, "no")
                ),
                "better_uncertain_count": sum(
                    1 for r in completed
                    if r.get("better_than_before") == "uncertain"
                ),
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
            "clarity": r["clarity"],
            "warmth": r["warmth"],
            "space": r["space"],
            "harshness_control": r["harshness_control"],
            "plastic_feel_control": r["plastic_feel_control"],
            "artifact_control": r["artifact_control"],
            "target_fit": r["target_fit"],
            "volume_matched": r["volume_matched"],
        })

    # Feedback overview
    total = len(flat_records)
    completed = [r for r in flat_records if r["feedback_status"] == "completed"]
    cc = len(completed)
    better_yes = sum(
        1 for r in completed
        if r.get("better_than_before") in (True, "yes")
    )
    better_no = sum(
        1 for r in completed
        if r.get("better_than_before") in (False, "no")
    )
    better_uncertain = sum(
        1 for r in completed
        if r.get("better_than_before") == "uncertain"
    )

    feedback_overview = {
        "total_records": total,
        "completed_records": cc,
        "pending_records": total - cc,
        "feedback_coverage": round(cc / total, 2) if total else 0.0,
        "better_yes": better_yes,
        "better_no": better_no,
        "better_uncertain": better_uncertain,
        "global_better_rate": round(better_yes / cc, 2) if cc else None,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "summary_type": SUMMARY_TYPE,
        "record_count": total,
        "feedback_overview": feedback_overview,
        "presets": preset_stats,
        "records": summary_records,
        "errors": errors,
    }


def _fmt(val, prec=2) -> str:
    if val is None:
        return "—"
    return f"{val:+.{prec}f}"


def _fb_score(val, prec=1) -> str:
    if val is None:
        return "—"
    return f"{val:.{prec}f}"


def _pct(val) -> str:
    if val is None:
        return "—"
    return f"{val * 100:.0f}%"


def write_summary_md(summary: dict, out_path: str):
    presets_data = summary.get("presets", {})
    records_list = summary.get("records", [])
    fb_overview = summary.get("feedback_overview", {})
    fb_pending = fb_overview.get("pending_records",
        sum(1 for r in records_list if r["feedback_status"] == "pending"))
    fb_done = fb_overview.get("completed_records",
        sum(1 for r in records_list if r["feedback_status"] == "completed"))
    fb_coverage = fb_overview.get("feedback_coverage")
    fb_better = fb_overview.get("better_yes", 0)
    fb_global_rate = fb_overview.get("global_better_rate")

    lines = [
        "# Moodify Treatment Record Summary",
        "",
        "## Overview",
        "",
        f"- **Total records**: {summary['record_count']}",
        f"- **Presets**: {', '.join(presets_data.keys()) or 'none'}",
        f"- **Pending feedback**: {fb_pending}",
        f"- **Completed feedback**: {fb_done}",
        f"- **Feedback coverage**: {fb_done}/{summary['record_count']} ({_pct(fb_coverage)})",
        f"- **Global better rate**: {fb_better}/{fb_done} yes ({_pct(fb_global_rate)})",
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

    # Feedback Score Summary
    lines += [
        "",
        "## Feedback Score Summary",
        "",
        "| Preset | Completed | Coverage | Better Rate | Clarity | Warmth | Space | "
        "Harsh Ctrl | Plastic Ctrl | Artifact Ctrl | Target Fit |",
        "|--------|----------:|---------:|------------:|--------:|-------:|------:|"
        "----------:|------------:|-------------:|----------:|",
    ]

    for preset in PRESET_NAMES:
        if preset not in presets_data:
            continue
        s = presets_data[preset]
        fq = s.get("feedback_quality", {})
        fs_ = s.get("feedback_scores", {})
        lines.append(
            f"| {preset} | {fq.get('completed_count', 0)} | "
            f"{_pct(fq.get('feedback_coverage'))} | "
            f"{_pct(fq.get('better_rate'))} | "
            f"{_fb_score(fs_.get('avg_clarity'))} | "
            f"{_fb_score(fs_.get('avg_warmth'))} | "
            f"{_fb_score(fs_.get('avg_space'))} | "
            f"{_fb_score(fs_.get('avg_harshness_control'))} | "
            f"{_fb_score(fs_.get('avg_plastic_feel_control'))} | "
            f"{_fb_score(fs_.get('avg_artifact_control'))} | "
            f"{_fb_score(fs_.get('avg_target_fit'))} |"
        )

    # Records table
    lines += [
        "",
        "## Records",
        "",
        "| Record | Song ID | Preset | RMS Δ | Match Gain | Warning | "
        "Crest Δ | DynRange Δ | Corr Δ | Feedback | Better? | Target Fit |",
        "|--------|---------|--------|------:|-----------:|--------:|"
        "--------:|-----------:|-------:|---------:|--------:|----------:|",
    ]

    for r in records_list:
        fb = r["feedback_status"]
        btb = r["better_than_before"]
        btb_str = {True: "yes", False: "no", "yes": "yes", "no": "no",
                   "uncertain": "uncertain"}.get(btb, str(btb) if btb else "—")
        tf = _fb_score(r.get("target_fit"), 0) if r.get("target_fit") is not None else "—"
        lines.append(
            f"| {r['record_file']} | {r['song_id']} | {r['preset']} | "
            f"{_fmt(r['rms_delta_db'])} | {_fmt(r['after_gain_match_db'])} | "
            f"{r['warning_level']} | {_fmt(r['crest_delta'])} | "
            f"{_fmt(r['dynamic_range_delta_db'])} | {_fmt(r['correlation_delta'])} | "
            f"{fb} | {btb_str} | {tf} |"
        )

    # Positive Feedback
    positive = [r for r in records_list
                if r["feedback_status"] == "completed"
                and r.get("better_than_before") in (True, "yes")]
    lines += [
        "",
        "## Positive Feedback",
        "",
    ]
    if positive:
        lines += [
            "| Record | Song ID | Preset | Target Fit | Notes |",
            "|--------|---------|--------|----------:|-------|",
        ]
        for r in positive:
            notes = (r.get("feedback_notes", "") or "")[:60]
            tf = _fb_score(r.get("target_fit"), 0) if r.get("target_fit") is not None else "—"
            lines.append(
                f"| {r['record_file']} | {r['song_id']} | {r['preset']} | "
                f"{tf} | {notes} |"
            )
    else:
        lines.append("No positive feedback yet.")

    # Pending Feedback
    pending = [r for r in records_list if r["feedback_status"] == "pending"]
    lines += [
        "",
        "## Pending Feedback",
        "",
    ]
    if pending:
        lines += [
            "| Record | Song ID | Preset |",
            "|--------|---------|--------|",
        ]
        for r in pending:
            lines.append(f"| {r['record_file']} | {r['song_id']} | {r['preset']} |")
    else:
        lines.append("No pending feedback.")

    # Human Feedback Status
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
        "Generated from local Treatment Records via Feedback-aware Aggregator.",
        "Not a database, not a cloud data layer, not a trained model.",
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
