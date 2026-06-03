from __future__ import annotations

from pathlib import Path

from scripts import mt002_mrs_score_manifest as scorer


def test_mt002_record_shape_completed(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "input.wav"
    input_path.write_bytes(b"input")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    output_path = output_dir / "output.wav"
    output_path.write_bytes(b"output")

    def fake_compute(path: str) -> dict:
        if path == str(input_path):
            return {"mrs_open": 1000.0, "d_real": 0.25, "subscores": {"dynamic_reality": 80.0}, "extra_penalties": {}, "penalty_flags": [], "error": None}
        return {"mrs_open": 1012.5, "d_real": 0.22, "subscores": {"dynamic_reality": 82.0}, "extra_penalties": {"over_dark": 0.1}, "penalty_flags": ["over_dark"], "error": None}

    monkeypatch.setattr(scorer, "compute_mrs_open_v031", fake_compute)

    row = {
        "run_id": "runtime_run",
        "task_id": "task_1",
        "sample_id": "sample_1",
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "preset": "clean_master",
    }
    record = scorer._record_from_row(row, "mt002_test", {})

    assert record["run_id"] == "mt002_test"
    assert record["sample_id"] == "sample_1"
    assert record["mrs_version"] == scorer.MRS_VERSION
    assert record["mrs_score"] == 1012.5
    assert record["mrs_before"] == 1000.0
    assert record["mrs_delta"] == 12.5
    assert record["status"] == "completed"
    assert record["penalty_flags"] == ["over_dark"]


def test_mt002_summary_pass_when_all_records_complete() -> None:
    records = [
        {"sample_id": "a", "preset": "clean_master", "mrs_score": 1001.0, "mrs_delta": 1.0, "penalty_flags": [], "status": "completed"},
        {"sample_id": "b", "preset": "warm_vocal", "mrs_score": 1003.0, "mrs_delta": 3.0, "penalty_flags": ["over_dark"], "status": "completed"},
    ]

    summary = scorer._summary(records, "mt002_test", Path("manifest.csv"))

    assert summary["decision"] == "PASS"
    assert summary["total_records"] == 2
    assert summary["completed"] == 2
    assert summary["failed"] == 0
    assert summary["unique_samples"] == 2
    assert summary["score_median"] == 1002.0
    assert summary["delta_median"] == 2.0
    assert summary["penalty_flags"] == {"over_dark": 1}
