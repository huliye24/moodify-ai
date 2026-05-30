"""MHP-012: Create a Moodify Treatment Record from Inspector metrics + preset params.

Usage:
  python scripts/v01_create_treatment_record.py \
    --before <original.wav> --after <processed.wav> \
    --inspector-report <metrics_comparison.json> \
    --preset warm_vocal \
    --output treatment_records/my_record.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


TREATMENT_RECORD_SCHEMA_VERSION = "0.1.0"

HUMAN_FEEDBACK_TEMPLATE = {
    "status": "pending",
    "volume_matched": None,
    "clarity": None,
    "warmth": None,
    "space": None,
    "harshness_control": None,
    "plastic_feel_control": None,
    "artifact_control": None,
    "target_fit": None,
    "better_than_before": None,
    "notes": "",
}

ALGORITHM_LEARNING_TEMPLATE = {
    "usable_for_future_adaptive_preset": True,
    "issue_tags": [],
    "positive_tags": [],
    "parameter_adjustment_suggestion": None,
}


def load_inspector_metrics(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_preset_params(preset: str) -> dict:
    from moodify.v01_presets import get_preset
    info = get_preset(preset)
    if info is None:
        print(f"ERROR: unknown preset '{preset}'")
        sys.exit(1)
    return {k: v for k, v in info["params"].items()}


def find_inspector_file(base_dir: str, filename: str) -> str | None:
    """Check if a file exists relative to base_dir, return path or None."""
    p = Path(base_dir) / filename
    return str(p) if p.exists() else None


def build_treatment_record(
    before_path: str,
    after_path: str,
    inspector_report_path: str,
    preset: str,
    song_id: str,
    notes: str,
) -> dict:
    # Load metrics
    metrics = load_inspector_metrics(inspector_report_path)
    before = metrics.get("before", {})
    after = metrics.get("after", {})
    delta = metrics.get("delta", {})
    loudness = metrics.get("loudness", {})

    # Load preset params
    params = load_preset_params(preset)

    # Inspector dir for finding related files
    insp_dir = str(Path(inspector_report_path).parent)

    # Build paths
    paths = {
        "before_audio": before_path,
        "after_audio": after_path,
        "inspector_metrics": inspector_report_path,
        "matched_after_audio": find_inspector_file(insp_dir, "after_matched.wav"),
        "inspector_report_md": find_inspector_file(insp_dir, "report.md"),
        "inspector_report_html": find_inspector_file(insp_dir, "report.html"),
    }

    # Map bands from metrics.bands format
    bands_before = {}
    bands_after = {}
    if "bands" in before:
        for bk, bv in before["bands"].items():
            bands_before[bk.replace("_db", "")] = bv
    if "bands" in after:
        for bk, bv in after["bands"].items():
            bands_after[bk.replace("_db", "")] = bv

    before_features = {
        "peak_db": before.get("peak_db"),
        "rms_db": before.get("rms_db"),
        "crest_factor": before.get("crest_factor"),
        "dynamic_range_db": before.get("dynamic_range_db"),
        "correlation_lr": before.get("correlation_lr"),
        "mid_side_ratio_db": before.get("mid_side_ratio_db"),
        "bands": bands_before,
        "spectral_centroid": before.get("spectral_centroid"),
        "spectral_rolloff_95": before.get("spectral_rolloff_95"),
        "spectral_flatness": before.get("spectral_flatness"),
    }

    after_features = {
        "peak_db": after.get("peak_db"),
        "rms_db": after.get("rms_db"),
        "crest_factor": after.get("crest_factor"),
        "dynamic_range_db": after.get("dynamic_range_db"),
        "correlation_lr": after.get("correlation_lr"),
        "mid_side_ratio_db": after.get("mid_side_ratio_db"),
        "bands": bands_after,
        "spectral_centroid": after.get("spectral_centroid"),
        "spectral_rolloff_95": after.get("spectral_rolloff_95"),
        "spectral_flatness": after.get("spectral_flatness"),
    }

    record = {
        "schema_version": TREATMENT_RECORD_SCHEMA_VERSION,
        "record_type": "moodify_treatment_record",
        "song_id": song_id,
        "preset": preset,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "paths": paths,
        "before_features": before_features,
        "after_features": after_features,
        "delta_features": delta,
        "preset_params": params,
        "loudness_match": {
            "rms_delta_db": loudness.get("rms_delta_db"),
            "after_gain_match_db": loudness.get("after_gain_match_db"),
            "warning_level": loudness.get("warning_level"),
            "matched_after_path": loudness.get("matched_after_path"),
        },
        "human_feedback": dict(HUMAN_FEEDBACK_TEMPLATE),
        "algorithm_learning": dict(ALGORITHM_LEARNING_TEMPLATE),
    }

    if notes:
        record["human_feedback"]["notes"] = notes

    return record


def main():
    parser = argparse.ArgumentParser(
        description="MHP-012: Create Moodify Treatment Record"
    )
    parser.add_argument("--before", required=True, help="Path to original audio")
    parser.add_argument("--after", required=True, help="Path to processed audio")
    parser.add_argument("--inspector-report", required=True,
                        help="Path to Inspector metrics_comparison.json")
    parser.add_argument("--preset", required=True,
                        help="Preset name (warm_vocal|clean_master|wide_space)")
    parser.add_argument("--song-id", default="",
                        help="Identifier for this song (optional)")
    parser.add_argument("--notes", default="", help="Free-form notes (optional)")
    parser.add_argument("--output", required=True,
                        help="Output path for treatment record JSON")
    args = parser.parse_args()

    # Validate
    if not Path(args.before).exists():
        print(f"ERROR: before file not found: {args.before}")
        sys.exit(1)
    if not Path(args.after).exists():
        print(f"ERROR: after file not found: {args.after}")
        sys.exit(1)
    if not Path(args.inspector_report).exists():
        print(f"ERROR: inspector report not found: {args.inspector_report}")
        sys.exit(1)

    song_id = args.song_id or Path(args.before).stem

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nMHP-012 Treatment Record")
    print(f"  Before:   {args.before}")
    print(f"  After:    {args.after}")
    print(f"  Preset:   {args.preset}")
    print(f"  Song ID:  {song_id}")
    print(f"  Output:   {out_path}\n")

    record = build_treatment_record(
        before_path=args.before,
        after_path=args.after,
        inspector_report_path=args.inspector_report,
        preset=args.preset,
        song_id=song_id,
        notes=args.notes,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"  OK {out_path}")
    print(f"     schema: {record['schema_version']}")
    print(f"     preset_params: {len(record['preset_params'])} params")
    print(f"     delta_features: {len(record['delta_features'])} deltas")
    print(f"     human_feedback: {record['human_feedback']['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
