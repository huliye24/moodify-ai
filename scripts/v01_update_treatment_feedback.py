"""MHP-017: Update human_feedback in a Moodify Treatment Record.

Usage:
  python scripts/v01_update_treatment_feedback.py \
    --record treatment_records/vocal_folk_warm_vocal.json \
    --clarity 4 --warmth 5 --better-than-before yes \
    --notes "warmer vocals"

  python scripts/v01_update_treatment_feedback.py \
    --record treatment_records/vocal_folk_warm_vocal.json \
    --notes "补充备注"

  python scripts/v01_update_treatment_feedback.py \
    --record treatment_records/vocal_folk_warm_vocal.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SCORE_FIELDS = [
    "clarity", "warmth", "space",
    "harshness_control", "plastic_feel_control", "artifact_control",
    "target_fit",
]

TRISTATE_FIELDS = {
    "yes": True,
    "no": False,
    "uncertain": None,
}


def _parse_tristate(value: str) -> bool | None:
    v = value.strip().lower()
    if v not in TRISTATE_FIELDS:
        raise ValueError(f"Expected yes/no/uncertain, got: {value}")
    return TRISTATE_FIELDS[v]


def _parse_score(value: int) -> int:
    v = int(value)
    if v < 1 or v > 5:
        raise ValueError(f"Score must be 1-5, got: {v}")
    return v


def load_record(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_record(record: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def build_feedback_patch(args) -> dict:
    """Build a dict of human_feedback fields from CLI args."""
    patch = {}

    if args.volume_matched is not None:
        patch["volume_matched"] = _parse_tristate(args.volume_matched)

    for field in SCORE_FIELDS:
        val = getattr(args, field, None)
        if val is not None:
            patch[field] = _parse_score(val)

    if args.better_than_before is not None:
        patch["better_than_before"] = _parse_tristate(args.better_than_before)

    if args.notes is not None:
        patch["notes"] = args.notes

    return patch


def main():
    parser = argparse.ArgumentParser(
        description="MHP-017: Update human feedback in Treatment Record"
    )
    parser.add_argument("--record", required=True,
                        help="Path to treatment record JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written, do not modify file")

    # Feedback params
    parser.add_argument("--volume-matched",
                        help="yes / no / uncertain")
    parser.add_argument("--clarity", type=int,
                        help="1-5: 1=muddy, 5=clear")
    parser.add_argument("--warmth", type=int,
                        help="1-5: 1=cold/thin, 5=warm/full")
    parser.add_argument("--space", type=int,
                        help="1-5: 1=flat/crowded, 5=open/deep")
    parser.add_argument("--harshness-control", type=int,
                        help="1-5: 1=harsh, 5=smooth")
    parser.add_argument("--plastic-feel-control", type=int,
                        help="1-5: 1=obvious AI/plastic, 5=natural")
    parser.add_argument("--artifact-control", type=int,
                        help="1-5: 1=obvious artifacts, 5=clean")
    parser.add_argument("--target-fit", type=int,
                        help="1-5: 1=misses goal, 5=perfectly achieves goal")
    parser.add_argument("--better-than-before",
                        help="yes / no / uncertain")
    parser.add_argument("--notes", help="Free-form listening notes")
    args = parser.parse_args()

    record_path = args.record
    if not Path(record_path).exists():
        print(f"ERROR: record not found: {record_path}")
        sys.exit(1)

    # Build patch
    try:
        patch = build_feedback_patch(args)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not patch:
        print("No feedback fields provided. Nothing to update.")
        return 0

    # Load existing record
    record = load_record(record_path)
    existing_fb = record.setdefault("human_feedback", {})

    # Merge: only overwrite fields the user specified
    merged = dict(existing_fb)
    merged.update(patch)
    merged["status"] = "completed"
    merged["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.dry_run:
        print("\n[Dry-run] Would write human_feedback:")
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        print("\nFile NOT modified.")
        return 0

    # Backup
    bak_path = record_path + ".bak"
    shutil.copy2(record_path, bak_path)
    print(f"  Backup: {bak_path}")

    # Write
    record["human_feedback"] = merged
    save_record(record, record_path)

    print(f"\nUpdated feedback:")
    print(f"  record: {record_path}")
    print(f"  status: {merged['status']}")
    print(f"  better_than_before: {merged.get('better_than_before')}")
    print(f"  volume_matched: {merged.get('volume_matched')}")

    scores_written = [f for f in SCORE_FIELDS if f in patch]
    if scores_written:
        print(f"  scores: {', '.join(f'{f}={patch[f]}' for f in scores_written)}")
    if patch.get("notes"):
        print(f"  notes: {patch['notes'][:80]}{'...' if len(patch['notes']) > 80 else ''}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
