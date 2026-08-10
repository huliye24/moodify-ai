"""MFY-DATA-FACTORY-001 dataset builder tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify.data_factory.dataset_builder import aggregate_dataset, build_case_dataset

CASE_ID = "case_" + "f" * 32


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_minimal_complete_case(case_dir: Path, case_id: str) -> None:
    """Minimal files that satisfy build_case_dataset without real scans."""
    _write_json(case_dir / "case_manifest.json", {
        "data_protocol_version": "MFY-DATA-PROTOCOL-001",
        "case_id": case_id,
        "source_sha256": "b" * 64,
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
    cases_rows = (dataset_dir / "cases.jsonl").read_text().strip().splitlines()
    assert len(cases_rows) == 1
    assert json.loads(cases_rows[0])["case_id"] == CASE_ID
