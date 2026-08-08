from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import soundfile as sf

from pwrm.audio import measure_audio
from pwrm.baselines import train_baselines
from pwrm.candidates import generate_candidates
from pwrm.deepseek_pack import build_deepseek_pack
from pwrm.pilot_gate import evaluate_pilot
from pwrm.records import audit_records


ROOT = Path(__file__).resolve().parents[1]


def _features(sign: float) -> dict[str, float]:
    return {
        "lufs_i": -14.0 + 0.02 * sign,
        "true_peak_dbTP": -3.0,
        "rms_dbFS": -16.0 + sign,
        "crest_db": 8.0 + sign,
        "low_ratio": 0.30 + 0.01 * sign,
        "mid_ratio": 0.50,
        "high_ratio": 0.20 - 0.01 * sign,
        "transient_strength": 0.10 + 0.01 * sign,
        "clarity_proxy": 0.60 + 0.02 * sign,
    }


def _record(index: int, split: str, winner: str) -> dict:
    hash_value = f"{index:064x}"[-64:]
    return {
        "pair_id": f"pair-{index}",
        "source": {"track_id": f"track-{index}", "audio_sha256": hash_value},
        "candidate_a": {
            "candidate_id": f"a-{index}",
            "audio_sha256": hash_value,
            "processing_chain": [],
            "features": _features(1 if winner == "A" else -1),
        },
        "candidate_b": {
            "candidate_id": f"b-{index}",
            "audio_sha256": hash_value,
            "processing_chain": [],
            "features": _features(-1 if winner == "A" else 1),
        },
        "constraints": {"lufs_delta": 0.04, "clarity_delta": 0.02},
        "context": {"playback_system": "reference-headphones", "randomized_order": True},
        "labels": [
            {"annotator_id": f"rater-{j}", "preference": winner, "confidence": 4}
            for j in range(3)
        ],
        "governance": {
            "dataset_split": split,
            "rubric_version": "power-v0.1",
            "created_at": "2026-07-24T00:00:00Z",
        },
    }


def test_audio_and_candidate_generation(tmp_path: Path) -> None:
    sample_rate = 48000
    time = np.arange(sample_rate * 2) / sample_rate
    audio = 0.1 * np.sin(2 * np.pi * 220 * time)
    source = tmp_path / "source.wav"
    sf.write(source, audio, sample_rate)
    metrics = measure_audio(source)
    assert -30 < metrics.lufs_i < -10

    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "candidate_id": "gentle",
                        "processing_chain": [{"op": "saturation", "drive": 0.1}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    results = generate_candidates(source, plan, tmp_path / "candidates")
    assert len(results) == 1
    assert abs(results[0].loudness_delta_lu) <= 0.1


def test_audit_baselines_gate_and_deepseek_pack(tmp_path: Path) -> None:
    records = [
        _record(i, "train" if i < 12 else "test", "A" if i % 2 == 0 else "B")
        for i in range(20)
    ]
    schema = json.loads((ROOT / "schemas" / "power_pair_record_v0.2.json").read_text())
    summary, anomalies = audit_records(records, schema)
    assert anomalies == []
    assert summary["mean_decisive_pair_agreement"] == 1.0

    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "audit_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    baseline = train_baselines(records, evidence)
    assert baseline["interpretable_acoustic"]["accuracy"] == 1.0

    pilot = evaluate_pilot(summary)
    assert pilot["decision"] == "go"
    (evidence / "pilot_summary.json").write_text(json.dumps(pilot), encoding="utf-8")
    result = build_deepseek_pack(evidence, tmp_path / "deepseek")
    assert result["task_count"] == 4

    leaked = deepcopy(records)
    extra = deepcopy(leaked[0])
    extra["pair_id"] = "leaked-pair"
    extra["governance"]["dataset_split"] = "test"
    leaked.append(extra)
    _, anomalies = audit_records(leaked, schema)
    assert any(item["kind"] == "track_split_leakage" for item in anomalies)
