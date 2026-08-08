"""DSK-MFY-DATA-ASSET-001 — unified job data pipeline tests."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify_runtime.data_asset import (
    SOURCE_REGISTRY,
    DataAssetStore,
    collect_evidence_package,
    collect_listening_scorecard,
    collect_metrics_comparison,
    collect_treatment_record,
    ingest_sources,
    record_id,
    validate_record,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_EVIDENCE = REPO_ROOT / "artifacts" / "verification" / "runtime_integration" / "golden_case" / "evidence"


def make_wav(path: Path) -> None:
    sr = 44_100
    t = np.arange(sr // 2) / sr
    sf.write(str(path), 0.3 * np.sin(2 * np.pi * 440 * t), sr)


def sample_record() -> dict:
    return {
        "record_id": record_id("treatment", "test"),
        "record_type": "treatment",
        "schema_version": "1.0.0",
        "collected_at": "2026-08-01T00:00:00Z",
        "source_artifacts": {"treatment_record": "treatment_records/test.json"},
        "job": {"job_id": "song_001", "status": "COMPLETED"},
        "scan": {"before_features": {"peak_db": -5.0, "rms_db": -20.0}},
        "scores": {"mrs": None, "mrs_not_available": "case predates MRS scoring"},
        "gates": {"status": "NONE", "checks": {}},
        "review": None,
        "craft": {"preset": "warm_vocal"},
        "evidence": {},
    }


class TestSchema:
    def test_well_formed_record_accepted(self):
        assert validate_record(sample_record()) == []

    def test_missing_required_field_rejected(self):
        record = sample_record()
        del record["source_artifacts"]
        errors = validate_record(record)
        assert any("source_artifacts" in e for e in errors)

    def test_unknown_record_type_rejected(self):
        record = sample_record()
        record["record_type"] = "not_a_type"
        assert validate_record(record)

    def test_implicit_null_section_rejected(self):
        record = sample_record()
        del record["scores"]  # scores must be explicit, never omitted
        assert validate_record(record)


class TestCollectors:
    def test_treatment_collector_produces_valid_record(self, tmp_path):
        wav = tmp_path / "before.wav"
        make_wav(wav)
        treatment = tmp_path / "record.json"
        treatment.write_text(json.dumps({
            "schema_version": "0.1.0", "record_type": "moodify_treatment_record",
            "song_id": "song_001", "preset": "warm_vocal", "created_at": "2026-01-01T00:00:00Z",
            "paths": {"before_audio": str(wav)},
            "before_features": {"peak_db": -5.0}, "after_features": {"peak_db": -1.0},
            "preset_params": {"steps": [{"type": "gain"}]},
        }), encoding="utf-8")
        record = collect_treatment_record(treatment)
        assert record["record_type"] == "treatment"
        assert record["job"]["job_id"] == "song_001"
        assert record["source_audio"]["sha256"]
        assert validate_record(record) == []

    def test_treatment_collector_skips_non_records(self, tmp_path):
        not_a_record = tmp_path / "summary.json"
        not_a_record.write_text('{"something": "else"}', encoding="utf-8")
        from moodify_runtime.data_asset import _SkipSource
        with pytest.raises(_SkipSource):
            collect_treatment_record(not_a_record)

    def test_scorecard_collector_parses_presets_and_dimensions(self, tmp_path):
        scorecard = tmp_path / "song_scorecard.md"
        scorecard.write_text(
            "# Moodify A/B 听感评分卡\n\n"
            "## 歌曲信息\n\n"
            "| 字段 | 值 |\n| ---- | -- |\n"
            "| song_id | song_001 |\n"
            "| 源文件 | `src.wav` |\n"
            "| 试听者 | tester |\n"
            "| volume_matched | true |\n\n"
            "### warm_vocal（温暖人声）\n\n"
            "| 字段 | 值 |\n| ---- | -- |\n"
            "| preset | warm_vocal |\n"
            "| better_than_before | true |\n\n"
            "| 维度 | 分数 (1-5) | 备注 |\n"
            "| ---- | :---: | ---- |\n"
            "| clarity（清晰度） | 4 | |\n"
            "| warmth（温暖度） | 5 | |\n"
            "| space（空间感） | 3 | |\n"
            "| harshness_control（刺耳控制） | 4 | |\n"
            "| plastic_feel_control（塑料感控制） | 4 | |\n"
            "| artifact_control（伪影控制） | 5 | |\n"
            "| target_fit（预设目标适配） | 4 | |\n\n"
            "**听感备注：**\n\n```\ngood warmth\n```\n",
            encoding="utf-8")
        records = collect_listening_scorecard(scorecard)
        assert len(records) == 1
        review = records[0]["review"]
        assert review["preset"] == "warm_vocal"
        assert review["better_than_before"] is True
        assert review["listener"] == "tester"
        assert review["volume_matched"] is True
        assert review["dimensions"]["clarity"] == 4
        assert review["dimensions"]["warmth"] == 5
        assert "good warmth" in review["notes"]
        assert validate_record(records[0]) == []

    def test_scorecard_empty_template_produces_no_records(self, tmp_path):
        template = tmp_path / "SCORECARD_TEMPLATE_ZH.md"
        template.write_text("# Template\n\nno preset sections here\n", encoding="utf-8")
        assert collect_listening_scorecard(template) == []

    def test_metrics_comparison_collector(self, tmp_path):
        wav = tmp_path / "before.wav"
        make_wav(wav)
        comparison = tmp_path / "metrics_comparison.json"
        comparison.write_text(json.dumps({
            "title": "t", "preset": "warm_vocal", "before_path": str(wav),
            "before": {"peak_db": -5.0}, "after": {"peak_db": -1.0},
            "delta": {"peak_db": 4.0}, "warnings": [], "loudness": {},
        }), encoding="utf-8")
        record = collect_metrics_comparison(comparison)
        assert record["record_type"] == "metrics_comparison"
        assert record["scan"]["before_features"]["peak_db"] == -5.0
        assert validate_record(record) == []

    def test_evidence_collector_binds_hashes(self, tmp_path):
        evidence = _build_evidence_package(tmp_path)
        record = collect_evidence_package(evidence)
        manifest = json.loads((evidence / "evidence_manifest.json").read_text(encoding="utf-8"))
        assert record["job"]["case_id"] == manifest["case_id"]
        assert record["evidence"]["output_sha256"] == manifest["output_sha256"]
        assert record["evidence"]["verification_status"] == "PASS"
        assert record["gates"]["status"] == "PASS"
        assert validate_record(record) == []

    def test_golden_evidence_package_validates(self):
        if not (GOLDEN_EVIDENCE / "evidence_manifest.json").exists():
            pytest.skip("golden evidence package not present")
        record = collect_evidence_package(GOLDEN_EVIDENCE)
        assert record["evidence"]["verification_status"] == "PASS"
        assert validate_record(record) == []


def _build_evidence_package(tmp_path: Path) -> Path:
    """Build a real evidence package through the production-control service."""
    from moodify.app.engines import NativeExecutionEngine
    from moodify.app.production_control import (
        ProductionCase,
        ProductionCaseStore,
        ProductionControlService,
        default_plan,
    )
    wav = tmp_path / "source.wav"
    make_wav(wav)
    store = ProductionCaseStore(tmp_path / "cases")
    case = ProductionCase(case_id="MFY-CASE-DATA-ASSET-TEST")
    case.register_source(str(wav))
    case.specify("warm vocal", ["vocal intimacy"], ["harsh highs"],
                 "gentle normalization", "tester")
    case.analyze({"peak_db": -12.0, "crest_factor": 8.0})
    case.set_plan(default_plan(case.analysis))
    case.run_technical_gate()
    case.approve("tester")
    store.save(case)
    service = ProductionControlService(store, NativeExecutionEngine())
    service.execute("MFY-CASE-DATA-ASSET-TEST")
    service.verify("MFY-CASE-DATA-ASSET-TEST")
    service.package("MFY-CASE-DATA-ASSET-TEST")
    return service.evidence_dir(store.load("MFY-CASE-DATA-ASSET-TEST"))


class TestStore:
    def test_append_dedup_and_roundtrip(self, tmp_path):
        store = DataAssetStore(tmp_path / "data_asset")
        record = sample_record()
        assert store.append(record) is True
        assert store.append(record) is False  # dedup
        loaded = store.load_record(record["record_id"])
        assert loaded == record
        assert store.stats()["total"] == 1

    def test_invalid_record_rejected(self, tmp_path):
        store = DataAssetStore(tmp_path / "data_asset")
        bad = sample_record()
        bad["record_type"] = "nope"
        with pytest.raises(ValueError, match="invalid"):
            store.append(bad)
        assert store.stats()["total"] == 0

    def test_append_accumulates_multiple_records(self, tmp_path):
        store = DataAssetStore(tmp_path / "data_asset")
        first = sample_record()
        second = sample_record()
        second["record_id"] = record_id("treatment", "second")
        assert store.append(first) and store.append(second)
        assert store.stats()["total"] == 2
        assert store.load_record(first["record_id"]) == first
        assert store.load_record(second["record_id"]) == second


class TestBackfill:
    def test_backfill_is_idempotent(self, tmp_path):
        fake_root = tmp_path / "repo"
        treatment_dir = fake_root / "treatment_records"
        treatment_dir.mkdir(parents=True)
        wav = fake_root / "before.wav"
        make_wav(wav)
        (treatment_dir / "a.json").write_text(json.dumps({
            "schema_version": "0.1.0", "record_type": "moodify_treatment_record",
            "song_id": "song_001", "preset": "warm_vocal", "created_at": "2026-01-01T00:00:00Z",
            "paths": {"before_audio": str(wav)},
            "before_features": {"peak_db": -5.0},
        }), encoding="utf-8")
        (treatment_dir / "summary.json").write_text('{"nope": 1}', encoding="utf-8")
        store = DataAssetStore(tmp_path / "store")
        first = ingest_sources(store, fake_root,
                               registry=[SOURCE_REGISTRY[0]])
        second = ingest_sources(store, fake_root,
                                registry=[SOURCE_REGISTRY[0]])
        assert first["treatment"]["records"] == 1
        assert second["treatment"]["records"] == 0  # no duplicates
        assert store.stats()["by_type"]["treatment"] == 1
        assert store.stats()["total"] == 1
