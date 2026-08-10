"""Materialize case-level and aggregate training records after human review."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moodify.auditory.manifests import sha256_file

from .human_review import load_review, pairwise_preferences, validate_completed_review


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_artifact_hashes(case_dir: Path, manifest: dict[str, Any]) -> None:
    """Reject tampered artifacts: manifest hashes must match the actual files.

    Missing files raise FileNotFoundError from the caller naturally; present
    files with mismatched hashes are an integrity violation, never silent.
    """
    if manifest.get("source_sha256"):
        source_rel = manifest.get("source_path")
        if not source_rel:
            raise ValueError("manifest declares source_sha256 but no source_path")
        source_file = case_dir / source_rel
        if not source_file.is_file():
            raise FileNotFoundError(f"source artifact missing: {source_file}")
        actual = sha256_file(source_file)
        if actual != manifest["source_sha256"]:
            raise ValueError(
                f"source hash mismatch: manifest={manifest['source_sha256'][:12]} actual={actual[:12]}"
            )
    for label, expected in (manifest.get("candidate_sha256") or {}).items():
        candidate_file = case_dir / "03_candidates" / f"candidate_{label}.wav"
        if not candidate_file.is_file():
            raise FileNotFoundError(f"candidate {label} artifact missing: {candidate_file}")
        actual = sha256_file(candidate_file)
        if actual != expected:
            raise ValueError(
                f"candidate {label} hash mismatch: manifest={expected[:12]} actual={actual[:12]}"
            )


def _metric_values(payload: dict) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, dict) and "value" in value:
            out[key] = value.get("value")
        else:
            out[key] = value
    return out


def build_case_dataset(case_dir: Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    manifest = _read_json(case_dir / "case_manifest.json")
    _verify_artifact_hashes(case_dir, manifest)
    review = load_review(case_dir / "06_human_review" / "review.json")
    validate_completed_review(review)

    source_metrics = _metric_values(_read_json(case_dir / "01_source_scan" / "metrics.json"))
    candidates: dict[str, dict[str, Any]] = {}
    for label in ("A", "B", "C"):
        after_metrics = _metric_values(
            _read_json(case_dir / "04_after_scan" / label / "metrics.json")
        )
        delta = _read_json(
            case_dir / "05_comparison" / f"source_vs_{label}" / "metrics_delta.json"
        )
        plan = _read_json(case_dir / "02_plans" / f"plan_{label}.json")
        candidate_meta = _read_json(case_dir / "03_candidates" / f"candidate_{label}.json")
        candidates[label] = {
            "plan": plan,
            "candidate": candidate_meta,
            "after_metrics": after_metrics,
            "delta": delta,
        }

    pairwise = pairwise_preferences(review)
    record = {
        "schema_version": "1.0",
        "data_protocol_version": manifest["data_protocol_version"],
        "case_id": manifest["case_id"],
        "source_sha256": manifest["source_sha256"],
        "versions": manifest["versions"],
        "source_metrics": source_metrics,
        "candidates": candidates,
        "human_review": review.to_dict(),
        "pairwise_preferences": pairwise,
    }

    learning_dir = case_dir / "07_learning"
    learning_dir.mkdir(parents=True, exist_ok=True)
    (learning_dir / "training_record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (learning_dir / "pairwise_preferences.jsonl").open("w", encoding="utf-8") as handle:
        for row in pairwise:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return record


def aggregate_dataset(cases_root: Path, output_dir: Path) -> dict[str, int]:
    cases_root = Path(cases_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    case_rows: list[dict] = []
    pairwise_rows: list[dict] = []
    skipped = 0
    rejections: list[dict[str, str]] = []
    for case_dir in sorted(path for path in cases_root.iterdir() if path.is_dir()):
        try:
            record = build_case_dataset(case_dir)
        except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
            skipped += 1
            rejections.append(
                {
                    "case_id": case_dir.name,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            continue
        case_rows.append(record)
        pairwise_rows.extend(record["pairwise_preferences"])

    with (output_dir / "cases.jsonl").open("w", encoding="utf-8") as handle:
        for row in case_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "pairwise_preferences.jsonl").open("w", encoding="utf-8") as handle:
        for row in pairwise_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "rejected_cases.jsonl").open("w", encoding="utf-8") as handle:
        for row in rejections:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "completed_cases": len(case_rows),
        "pairwise_preferences": len(pairwise_rows),
        "skipped_cases": skipped,
    }
    (output_dir / "dataset_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary
