"""MFY-DATA-FACTORY-001 dataset builder tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.auditory.manifests import sha256_file
from moodify.data_factory.dataset_builder import aggregate_dataset, build_case_dataset

CASE_ID = "case_" + "f" * 32


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_minimal_complete_case(case_dir: Path, case_id: str) -> None:
    """Minimal files that satisfy build_case_dataset without real scans.

    No source_sha256 is declared: hash verification only applies to manifests
    that claim artifact hashes (real runner cases).
    """
    _write_json(case_dir / "case_manifest.json", {
        "data_protocol_version": "MFY-DATA-PROTOCOL-001",
        "case_id": case_id,
        "versions": {"scan_profile_hash": "c" * 64},
    })
    _write_json(case_dir / "06_human_review" / "review.json", {
        "case_id": case_id,
        "ranking": ["B", "A", "SOURCE", "C"],
        "rejected": [],
        "reviewer_id": "human-test-001",
        "notes": "",
        "completed_at": "2026-08-10T00:00:00+00:00",
    })
    _write_json(case_dir / "01_source_scan" / "metrics.json", {
        "presence_2000_5000_hz": {"value": 0.05},
    })
    for label in ("A", "B", "C"):
        _write_json(case_dir / "04_after_scan" / label / "metrics.json", {
            "presence_2000_5000_hz": {"value": 0.10},
        })
        _write_json(case_dir / "05_comparison" / f"source_vs_{label}" / "metrics_delta.json", {
            "metric_deltas": {},
        })
        _write_json(case_dir / "02_plans" / f"plan_{label}.json", {
            "plan_id": f"{case_id}__PLAN_{label}",
        })
        _write_json(case_dir / "03_candidates" / f"candidate_{label}.json", {
            "candidate_id": f"{case_id}__CAND_{label}",
        })


def test_dataset_builder_refuses_incomplete_review(tmp_path: Path):
    case = tmp_path / "case"
    _write_json(case / "case_manifest.json", {
        "data_protocol_version": "MFY-DATA-PROTOCOL-001",
        "case_id": "case_" + "a" * 32,
        "source_sha256": "b" * 64,
        "versions": {},
    })
    _write_json(case / "06_human_review" / "review.json", {
        "case_id": "case_" + "a" * 32,
        "ranking": [],
        "rejected": [],
        "reviewer_id": "",
        "notes": "",
        "completed_at": None,
    })
    with pytest.raises(ValueError):
        build_case_dataset(case)


def test_aggregate_includes_only_completed_valid_cases(tmp_path: Path):
    cases_root = tmp_path / "cases"
    _make_minimal_complete_case(cases_root / CASE_ID, CASE_ID)
    _add_real_source_wav(cases_root / CASE_ID)

    broken = cases_root / ("case_" + "e" * 32)
    _write_json(broken / "case_manifest.json", {
        "data_protocol_version": "MFY-DATA-PROTOCOL-001",
        "case_id": "case_" + "e" * 32,
        "source_sha256": "d" * 64,
        "versions": {},
    })
    _write_json(broken / "06_human_review" / "review.json", {
        "case_id": "case_" + "e" * 32,
        "ranking": [],
        "rejected": [],
        "reviewer_id": "",
        "notes": "",
        "completed_at": None,
    })

    summary = aggregate_dataset(cases_root, tmp_path / "dataset")
    assert summary["completed_cases"] == 1
    assert summary["pairwise_preferences"] == 6
    assert summary["skipped_cases"] == 1

    dataset_dir = tmp_path / "dataset"
    assert (dataset_dir / "cases.jsonl").is_file()
    assert (dataset_dir / "pairwise_preferences.jsonl").is_file()
    assert (dataset_dir / "rejected_cases.jsonl").is_file()
    cases_rows = (dataset_dir / "cases.jsonl").read_text().strip().splitlines()
    assert len(cases_rows) == 1
    assert json.loads(cases_rows[0])["case_id"] == CASE_ID
    rejected_rows = (dataset_dir / "rejected_cases.jsonl").read_text().strip().splitlines()
    assert len(rejected_rows) == 1
    assert json.loads(rejected_rows[0])["case_id"] == broken.name


def _add_real_source_wav(case_dir: Path) -> Path:
    """Attach real wavs + matching manifest hashes (MFY-FI-FINDING-001 path)."""
    src_dir = case_dir / "00_source"
    src_dir.mkdir(parents=True, exist_ok=True)
    sr = 8000
    t = np.arange(sr) / sr
    x = (0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    wav = src_dir / "source.wav"
    sf.write(wav, x, sr)

    cand_dir = case_dir / "03_candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    candidate_hashes: dict[str, str] = {}
    for label in ("A", "B", "C"):
        cand_wav = cand_dir / f"candidate_{label}.wav"
        sf.write(cand_wav, x * (0.9 + 0.05 * ord(label) / 100), sr)
        candidate_hashes[label] = sha256_file(cand_wav)

    manifest_path = case_dir / "case_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_path"] = "00_source/source.wav"
    manifest["source_sha256"] = sha256_file(wav)
    manifest["candidate_sha256"] = candidate_hashes
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return wav


def test_build_case_dataset_accepts_correct_hashes(tmp_path: Path):
    case = tmp_path / "case"
    _make_minimal_complete_case(case, CASE_ID)
    _add_real_source_wav(case)
    record = build_case_dataset(case)
    assert record["case_id"] == CASE_ID


def test_aggregate_rejects_tampered_source_hash(tmp_path: Path):
    cases_root = tmp_path / "cases"
    good = cases_root / ("case_" + "9" * 32)
    _make_minimal_complete_case(good, "case_" + "9" * 32)
    _add_real_source_wav(good)

    tampered = cases_root / ("case_" + "8" * 32)
    _make_minimal_complete_case(tampered, "case_" + "8" * 32)
    _add_real_source_wav(tampered)
    manifest_path = tampered / "case_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = aggregate_dataset(cases_root, tmp_path / "dataset")
    assert summary["completed_cases"] == 1
    assert summary["skipped_cases"] == 1
    rejected_rows = (tmp_path / "dataset" / "rejected_cases.jsonl").read_text().splitlines()
    assert len(rejected_rows) == 1
    rejected = json.loads(rejected_rows[0])
    assert rejected["case_id"] == tampered.name
    assert rejected["error_type"] == "ValueError"
    assert "hash mismatch" in rejected["message"]


def test_aggregate_rejects_tampered_candidate_hash(tmp_path: Path):
    cases_root = tmp_path / "cases"
    tampered = cases_root / ("case_" + "7" * 32)
    _make_minimal_complete_case(tampered, "case_" + "7" * 32)
    _add_real_source_wav(tampered)
    manifest_path = tampered / "case_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["candidate_sha256"]["A"] = "f" * 64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="candidate A hash mismatch"):
        build_case_dataset(tampered)
