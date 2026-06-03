from __future__ import annotations

import json
from pathlib import Path

from scripts import mt002_validate_mrs_matrix as matrix


def _record(task_id: str, sample_id: str, preset: str, before: float, score: float, d_after: float, flags: list[str] | None = None) -> dict:
    return {
        "run_id": "mt002_baseline",
        "task_id": task_id,
        "sample_id": sample_id,
        "preset": preset,
        "mrs_version": matrix.MRS_VERSION,
        "mrs_before": before,
        "mrs_score": score,
        "mrs_delta": score - before,
        "d_real_after": d_after,
        "penalty_flags": flags or [],
        "status": "completed",
        "created_at": "2026-06-03T00:00:00+00:00",
    }


def test_mt002_validation_matrix_runs_all_tests(tmp_path: Path) -> None:
    records = [
        _record("t1", "s1", "clean_master", 1000.0, 990.0, 0.30, ["over_dark"]),
        _record("t2", "s1", "warm_vocal", 1000.0, 1010.0, 0.25, []),
        _record("t3", "s2", "clean_master", 1120.0, 1110.0, 0.12, []),
        _record("t4", "s2", "wide_space", 1120.0, 1130.0, 0.10, ["loudness_anomaly"]),
        _record("t5", "s3", "clean_master", 980.0, 1005.0, 0.26, []),
        _record("t6", "s3", "warm_vocal", 980.0, 1015.0, 0.24, []),
        _record("t7", "s4", "clean_master", 990.0, 1000.0, 0.27, ["over_dark"]),
        _record("t8", "s4", "wide_space", 990.0, 1020.0, 0.23, []),
        _record("t9", "s5", "clean_master", 1010.0, 1030.0, 0.22, []),
        _record("t10", "s5", "wide_space", 1010.0, 1040.0, 0.21, []),
    ]
    records_path = tmp_path / "records.jsonl"
    records_path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

    result = matrix.run_validation(records_path, None, "mt002_matrix_test")

    assert len(result["tests"]) == len(matrix.TEST_NAMES)
    assert result["decision"] == "EXPERIMENTAL"
    assert result["fail_count"] == 0
    statuses = {item["name"]: item["status"] for item in result["tests"]}
    assert statuses["monotonicity"] == "PASS"
    assert statuses["no_ceiling"] == "PASS"
    assert statuses["stability"] == "PASS"
    assert statuses["v02_v031_correlation"] == "HOLD"


def test_mt002_spearman_detects_rank_correlation() -> None:
    assert matrix._spearman([(1.0, 10.0), (2.0, 20.0), (3.0, 30.0)]) == 1.0
    assert matrix._spearman([(1.0, 30.0), (2.0, 20.0), (3.0, 10.0)]) == -1.0
