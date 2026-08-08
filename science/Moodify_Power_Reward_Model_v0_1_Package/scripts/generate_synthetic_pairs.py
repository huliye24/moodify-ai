"""Generate synthetic pair records for D04 pipeline validation.

Creates sufficient records to exercise all quality gates:
- min 20 records, 40 decisive labels (pilot threshold)
- min 8 train + 4 test decisive pairs (baseline threshold)

All records are marked with provenance='synthetic=true'. NOT scientific evidence.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "runs" / "PWRM_EXP_001" / "02_stimuli" / "stimulus_manifest.json"
SCHEMA_PATH = ROOT / "schemas" / "power_pair_record_v0.2.json"
OUTPUT_DIR = ROOT / "runs" / "PWRM_EXP_001" / "04_synthetic_validation"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _stimulus_by_id(stimuli: list[dict], stimulus_id: str) -> dict:
    for s in stimuli:
        if s["stimulus_id"] == stimulus_id:
            return s
    raise KeyError(stimulus_id)


def _features(stimulus: dict) -> dict[str, float]:
    m = stimulus["metrics"]
    return {
        "lufs_i": m["lufs_i"],
        "true_peak_dbTP": m["true_peak_dbTP"],
        "rms_dbFS": m["rms_dbFS"],
        "crest_db": m["crest_db"],
        "low_ratio": m["low_ratio"],
        "mid_ratio": m["mid_ratio"],
        "high_ratio": m["high_ratio"],
        "transient_strength": m["transient_strength"],
        "clarity_proxy": m["clarity_proxy"],
    }


def _make_labels(rng: random.Random, winner: str, count: int = 3) -> list[dict]:
    labels = []
    for i in range(count):
        preference = winner if rng.random() < 0.85 else ("A" if winner == "B" else "B")
        labels.append({
            "annotator_id": f"syn-rater-{i + 1}",
            "preference": preference,
            "confidence": rng.randint(3, 5),
            "reason_code": rng.choice(
                ["impact", "forward_motion", "density", "transient_control", "clarity"]
            ),
        })
    return labels


def _make_record(
    *,
    pair_id: str,
    track_id: str,
    side_a: dict,
    side_b: dict,
    labels: list[dict],
    dataset_split: str,
) -> dict:
    fa = _features(side_a)
    fb = _features(side_b)
    return {
        "pair_id": pair_id,
        "source": {
            "track_id": track_id,
            "audio_sha256": side_a["source_sha256"],
            "genre": "synth-validation",
            "provenance": "synthetic=true; D04 pipeline test",
        },
        "candidate_a": {
            "candidate_id": side_a["stimulus_id"],
            "audio_sha256": side_a["source_sha256"],
            "processing_chain": (
                [] if side_a.get("is_original") else
                [{"op": "loudness_match", "gain_db": side_a.get("loudness_match_gain_db", 0)}]
            ),
            "features": fa,
        },
        "candidate_b": {
            "candidate_id": side_b["stimulus_id"],
            "audio_sha256": side_b["source_sha256"],
            "processing_chain": (
                [] if side_b.get("is_original") else
                [{"op": "loudness_match", "gain_db": side_b.get("loudness_match_gain_db", 0)}]
            ),
            "features": fb,
        },
        "constraints": {
            "lufs_delta": round(abs(fa["lufs_i"] - fb["lufs_i"]), 10),
            "clarity_delta": round(fb["clarity_proxy"] - fa["clarity_proxy"], 10),
        },
        "context": {
            "playback_system": "synthetic-pipeline-validation",
            "randomized_order": True,
            "notes": "SYNTHETIC DATA — not human listening evidence",
        },
        "labels": labels,
        "governance": {
            "dataset_split": dataset_split,
            "rubric_version": "power-v0.1",
            "created_at": "2026-07-24T00:00:00Z",
        },
    }


def build_records(manifest: dict, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    stimuli = manifest["stimuli"]
    original = next(s for s in stimuli if s["is_original"])
    candidates = [s for s in stimuli if not s["is_original"]]
    track_id = "CAD-MFY-001"
    records: list[dict] = []

    # --- Stage A: 5 candidates vs original, 2 excerpts each = 10 pairs ---
    for idx, candidate in enumerate(candidates):
        for excerpt in ("mid", "contrast"):
            pair_id = f"syn-A-{candidate['stimulus_id']}-{excerpt}"
            split = "train" if idx < 3 else "test"
            labels = _make_labels(rng, "B", count=3)
            records.append(_make_record(
                pair_id=pair_id,
                track_id=track_id,
                side_a=original,
                side_b=candidate,
                labels=labels,
                dataset_split=split,
            ))

    # --- Stage B: candidate vs candidate round-robin (subset to reach 24 pairs) ---
    cc_pairs = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (0, 2), (1, 3), (2, 4), (3, 0), (4, 1),
        (0, 3), (1, 4),
    ]
    for idx, (i, j) in enumerate(cc_pairs):
        ca = candidates[i]
        cb = candidates[j]
        for excerpt in ("mid", "contrast"):
            pair_id = f"syn-B-{ca['stimulus_id']}-vs-{cb['stimulus_id']}-{excerpt}"
            split = "train" if idx < 8 else "test"
            winner = "A" if rng.random() < 0.6 else "B"
            labels = _make_labels(rng, winner, count=3)
            records.append(_make_record(
                pair_id=pair_id,
                track_id=track_id,
                side_a=ca,
                side_b=cb,
                labels=labels,
                dataset_split=split,
            ))

    return records


def main() -> int:
    manifest = load_manifest()
    records = build_records(manifest)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(schema)
    errors = []
    for record in records:
        for err in validator.iter_errors(record):
            errors.append(f"{record['pair_id']}: {err.message}")

    if errors:
        print(f"Schema validation FAILED ({len(errors)} errors):")
        for err in errors:
            print(f"  - {err}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "synthetic_pairs.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    total_labels = sum(len(r["labels"]) for r in records)
    decisive = sum(
        sum(1 for l in r["labels"] if l["preference"] in ("A", "B"))
        for r in records
    )
    splits: dict[str, int] = {}
    for r in records:
        s = r["governance"]["dataset_split"]
        splits[s] = splits.get(s, 0) + 1

    train_decisive = sum(
        len([l for l in r["labels"] if l["preference"] in ("A", "B")])
        for r in records if r["governance"]["dataset_split"] == "train"
    )

    print(f"Generated {len(records)} synthetic pair records")
    print(f"  Total labels: {total_labels}")
    print(f"  Decisive labels (all): {decisive}")
    print(f"  Decisive labels (train): {train_decisive}")
    print(f"  Splits: {splits}")
    print(f"  Schema valid: OK")
    print(f"  Output: {output_path}")

    # Quick check against baseline minimums
    usable = [r for r in records if len(set(
        l["preference"] for l in r["labels"]
    ) & {"A", "B"}) > 0]
    train_pairs = [r for r in usable if r["governance"]["dataset_split"] == "train"]
    test_pairs = [r for r in usable if r["governance"]["dataset_split"] == "test"]
    print(f"  Usable pairs (>=1 decisive label): {len(usable)}")
    print(f"  Train usable pairs: {len(train_pairs)}, Test usable pairs: {len(test_pairs)}")
    if len(train_pairs) >= 8 and len(test_pairs) >= 4:
        print("  Baseline threshold: SATISFIED")
    else:
        print("  Baseline threshold: WARNING - need 8 train + 4 test")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
