"""Hardening tests for the Treatment Record aggregator."""

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "v01_aggregate_treatment_records.py"
SPEC = importlib.util.spec_from_file_location("treatment_aggregator", SCRIPT)
assert SPEC and SPEC.loader
aggregator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aggregator)


def _record(song_id: str = "song-1", preset: str = "warm_vocal") -> dict:
    return {
        "record_type": "moodify_treatment_record",
        "schema_version": "0.1.0",
        "song_id": song_id,
        "preset": preset,
        "delta_features": {},
        "loudness_match": {},
        "human_feedback": {"status": "pending"},
    }


def test_valid_records_are_loaded_in_filename_order(tmp_path):
    (tmp_path / "b.json").write_text(json.dumps(_record("b")), encoding="utf-8")
    (tmp_path / "a.json").write_text(json.dumps(_record("a")), encoding="utf-8")
    records, errors = aggregator.load_records(str(tmp_path))
    assert errors == []
    assert [record["song_id"] for record in records] == ["a", "b"]


def test_invalid_treatment_record_is_rejected_not_aggregated(tmp_path):
    invalid = _record()
    del invalid["delta_features"]
    (tmp_path / "invalid.json").write_text(json.dumps(invalid), encoding="utf-8")
    records, errors = aggregator.load_records(str(tmp_path))
    assert records == []
    assert any("missing required field 'delta_features'" in item["error"] for item in errors)


def test_malformed_json_is_preserved_as_error(tmp_path):
    (tmp_path / "bad.json").write_text("{bad", encoding="utf-8")
    records, errors = aggregator.load_records(str(tmp_path))
    assert records == []
    assert errors[0]["file"] == "bad.json"


def test_non_treatment_json_is_ignored(tmp_path):
    (tmp_path / "summary.json").write_text(json.dumps({"summary_type": "derived"}), encoding="utf-8")
    records, errors = aggregator.load_records(str(tmp_path))
    assert records == []
    assert errors == []


def test_bak_artifacts_are_factual_exclusions_not_records(tmp_path):
    (tmp_path / "song.json.bak").write_text(json.dumps(_record()), encoding="utf-8")
    (tmp_path / "summary.json.bak").write_text("{}", encoding="utf-8")
    assert aggregator.scan_absent_records(str(tmp_path)) == ["song.json.bak"]
    records, errors = aggregator.load_records(str(tmp_path))
    assert records == []
    assert errors == []


def test_summary_exposes_errors_and_excluded_artifacts():
    summary = aggregator.build_summary(
        [], [{"file": "bad.json", "error": "bad"}], ["old.json.bak"]
    )
    assert summary["record_count"] == 0
    assert summary["errors"] == [{"file": "bad.json", "error": "bad"}]
    assert summary["known_absent"] == ["old.json.bak"]
