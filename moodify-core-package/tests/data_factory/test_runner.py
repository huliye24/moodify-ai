"""MFY-DATA-FACTORY-001 full machine-loop integration tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.auditory.errors import AudioDecodeFailed, AudioEmpty
from moodify.data_factory.dataset_builder import build_case_dataset
from moodify.data_factory.models import DATA_PROTOCOL_VERSION
from moodify.data_factory.runner import validate_source_audio

CASE_ID = "case_" + "f" * 32


def _scan_profile_hash(case_dir: Path, *parts: str) -> str:
    manifest = json.loads(
        (case_dir / Path(*parts) / "scan_manifest.json").read_text(encoding="utf-8")
    )
    return manifest["scan_profile_hash"]


def test_case_directory_layout(completed_case_dir: Path):
    expected = [
        "00_source",
        "01_source_scan",
        "02_plans",
        "03_candidates",
        "04_after_scan",
        "05_comparison",
        "06_human_review",
        "case_manifest.json",
        "production_case.json",
    ]
    for name in expected:
        assert (completed_case_dir / name).exists(), f"missing {name}"


def test_exactly_three_plans_persisted(completed_case_dir: Path):
    for label in ("A", "B", "C"):
        plan = json.loads(
            (completed_case_dir / "02_plans" / f"plan_{label}.json").read_text(encoding="utf-8")
        )
        assert plan["candidate_label"] == label
        assert plan["case_id"] == CASE_ID
        assert plan["plan_id"] == f"{CASE_ID}__PLAN_{label}"
        assert plan["candidate_id"] == f"{CASE_ID}__CAND_{label}"
        assert plan["source_sha256"]
        assert plan["scan_profile_hash"]


def test_three_candidate_wavs_with_lineage(completed_case_dir: Path):
    for label in ("A", "B", "C"):
        wav = completed_case_dir / "03_candidates" / f"candidate_{label}.wav"
        assert wav.is_file()
        data, sr = sf.read(wav)
        assert sr == 48000
        assert len(data) > 0
        meta = json.loads(
            (completed_case_dir / "03_candidates" / f"candidate_{label}.json").read_text(
                encoding="utf-8"
            )
        )
        assert meta["candidate_sha256"]
        assert meta["parent_source_sha256"] == json.loads(
            (completed_case_dir / "case_manifest.json").read_text(encoding="utf-8")
        )["source_sha256"]


def test_before_and_after_share_scan_profile_hash(completed_case_dir: Path):
    before = _scan_profile_hash(completed_case_dir, "01_source_scan")
    for label in ("A", "B", "C"):
        after = _scan_profile_hash(completed_case_dir, "04_after_scan", label)
        assert after == before, f"after {label} scan profile hash differs"


def test_source_and_candidate_hashes_persisted_in_manifest(completed_case_dir: Path):
    manifest = json.loads(
        (completed_case_dir / "case_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["data_protocol_version"] == DATA_PROTOCOL_VERSION
    assert len(manifest["source_sha256"]) == 64
    assert set(manifest["candidate_sha256"]) == {"A", "B", "C"}
    assert all(len(h) == 64 for h in manifest["candidate_sha256"].values())
    versions = manifest["versions"]
    for key in (
        "moodify_package_version",
        "scan_profile_id",
        "scan_profile_hash",
        "plan_generator_version",
    ):
        assert versions[key]


def test_production_case_uses_algorithmic_authority(completed_case_dir: Path):
    production_case = json.loads(
        (completed_case_dir / "production_case.json").read_text(encoding="utf-8")
    )
    assert production_case["lifecycle_state"] == "COMPLETED"
    assert production_case["authority_state"] == "ALGORITHM"
    assert production_case["source_id"].startswith("sha256:")


def test_algorithmic_review_completed_without_human_input(completed_case_dir: Path):
    review = json.loads(
        (completed_case_dir / "06_human_review" / "review.json").read_text(encoding="utf-8")
    )
    assert review["reviewer_id"].startswith("algorithm:")
    assert len(review["ranking"]) == 4
    assert set(review["ranking"]) == {"SOURCE", "A", "B", "C"}
    assert review["completed_at"]
    scores = json.loads(
        (completed_case_dir / "06_human_review" / "algorithmic_scores.json").read_text(
            encoding="utf-8"
        )
    )
    assert scores["formula_version"]
    assert set(scores["scores"]) == {"SOURCE", "A", "B", "C"}


def test_completed_review_materializes_six_pairwise_rows(completed_case_dir: Path):
    record = build_case_dataset(completed_case_dir)
    assert record["case_id"] == CASE_ID
    assert len(record["pairwise_preferences"]) == 6
    assert set(record["candidates"]) == {"A", "B", "C"}
    for candidate in record["candidates"].values():
        assert set(candidate) == {"plan", "candidate", "after_metrics", "delta"}
    learning_dir = completed_case_dir / "07_learning"
    assert (learning_dir / "training_record.json").is_file()
    rows = list((learning_dir / "pairwise_preferences.jsonl").read_text().strip().splitlines())
    assert len(rows) == 6


def _valid_wav(tmp_path: Path, name: str = "valid.wav", duration_s: float = 2.0) -> Path:
    sr = 48000
    t = np.arange(int(sr * duration_s)) / sr
    x = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    path = tmp_path / name
    sf.write(path, x, sr)
    return path


def test_validate_source_audio_accepts_valid_wav(tmp_path: Path):
    wav = _valid_wav(tmp_path)
    validate_source_audio(wav)  # must not raise


def test_validate_source_audio_rejects_truncated_wav(tmp_path: Path):
    full = _valid_wav(tmp_path, "full.wav")
    truncated = tmp_path / "truncated.wav"
    truncated.write_bytes(full.read_bytes()[:128])
    with pytest.raises((AudioDecodeFailed, AudioEmpty)):
        validate_source_audio(truncated)


def test_validate_source_audio_rejects_silence(tmp_path: Path):
    sr = 48000
    t = np.arange(sr * 2) / sr
    x = np.zeros_like(t).astype(np.float32)
    wav = tmp_path / "silent.wav"
    sf.write(wav, x, sr)
    with pytest.raises(AudioEmpty, match="silent"):
        validate_source_audio(wav)


def test_validate_source_audio_accepts_fade_in_open(tmp_path: Path):
    """A produced master opening with a -90 dBFS fade-in must pass."""
    sr = 48000
    t = np.arange(sr * 2) / sr
    x = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    x[: int(0.5 * sr)] *= np.linspace(0.0, 0.003, int(0.5 * sr))  # fade to ~-90 dBFS
    wav = tmp_path / "fade_in.wav"
    sf.write(wav, x, sr)
    validate_source_audio(wav)  # must not raise
