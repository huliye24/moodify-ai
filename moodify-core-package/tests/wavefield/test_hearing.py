"""HearSnapshot — the existing auditory layer, re-exposed and honestly bounded."""

from __future__ import annotations

import numpy as np

from moodify.auditory.judgment import evaluate_risk_flags
from moodify.auditory.stereo import compute_stereo_metrics
from moodify.wavefield.hearing import (
    CLAIM_CLASS,
    hear_snapshot,
    judge_candidate,
    measure_audio,
    summarize,
)
from moodify.wavefield.models import HEAR_SCHEMA
from moodify.wavefield.renderer import render_array
from moodify.wavefield.search import probe_fields


def _snapshot(source_wav, candidate_id: str = "B"):
    import soundfile as sf

    source, sr = sf.read(str(source_wav), always_2d=False)
    source = np.asarray(source)
    field = {field.field_id: field for field in probe_fields()}[f"field_{candidate_id}"]
    candidate, _ = render_array(source, sr, field)
    return hear_snapshot(
        candidate_id=candidate_id,
        field_id=field.field_id,
        candidate_samples=candidate,
        candidate_sample_rate=sr,
        source_samples=source,
        source_sample_rate=sr,
    )


def test_measure_audio_exposes_the_full_existing_metric_record(source_wav):
    import soundfile as sf

    samples, sr = sf.read(str(source_wav), always_2d=False)
    metrics = measure_audio(np.asarray(samples), sr)

    for key in (
        "integrated_lufs",
        "true_peak_dbfs",
        "sample_peak_dbfs",
        "rms_dbfs",
        "crest_factor_db",
        "plr_db",
        "spectral_centroid_hz",
        "stereo_correlation",
        "side_to_mid_db",
        "stereo_width_proxy",
        "negative_correlation_ratio",
        "phase_risk_ratio",
        "duration",
        "channels",
        "sample_rate",
    ):
        assert key in metrics, f"{key} missing from the hearing record"
        assert isinstance(metrics[key], dict)
        assert "value" in metrics[key]

    # measurements are the existing ones, not a second implementation
    assert metrics["stereo_correlation"] == compute_stereo_metrics(np.asarray(samples))[
        "stereo_correlation"
    ]


def test_measure_audio_rejects_non_finite_audio():
    try:
        measure_audio(np.array([0.0, np.nan], dtype=np.float32), 48000)
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("non-finite audio must not be measured")


def test_snapshot_has_the_documented_contract(source_wav):
    snapshot = _snapshot(source_wav)
    assert snapshot["schema"] == HEAR_SCHEMA == "moodify.hear/0.1"
    assert snapshot["candidate_id"] == "B"
    assert snapshot["field_id"] == "field_B"
    assert snapshot["is_reference"] is False
    assert set(snapshot) >= {
        "schema", "candidate_id", "field_id", "metrics",
        "source_comparison", "judge", "uncertainty", "provenance",
    }


def test_snapshot_carries_the_loudness_matching_strategy(source_wav):
    comparison = _snapshot(source_wav)["source_comparison"]
    assert comparison["reference"] == "ORIGINAL"
    assert comparison["normalization_valid"] is True
    assert comparison["normalization_method"] == "gain-to-before-LUFS"
    assert isinstance(comparison["audition_correction_db"], float)
    # the raw, un-normalised deltas stay visible too
    assert "integrated_lufs" in comparison["metric_delta"]
    assert "absolute_delta" in comparison["metric_delta"]["integrated_lufs"]


def test_snapshot_records_helper_uncertainty_honestly(source_wav):
    uncertainty = _snapshot(source_wav)["uncertainty"]
    reasons = {row["reason"] for row in uncertainty}
    assert "OUT_OF_SCOPE" in reasons, "a stereo projection must not look like a sound field"
    assert "VALIDATION_LIMIT" in reasons, "the uncalibrated engine must be declared"

    provenance = _snapshot(source_wav)["provenance"]
    assert provenance["claim_class"] == CLAIM_CLASS == "PERCEPTUAL_VIRTUAL_FIELD"
    assert provenance["physically_exact_simulation"] is False
    assert provenance["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"


def test_short_material_declares_incomplete_evidence():
    sr = 48000
    t = np.arange(sr) / sr  # 1 s: below the 6 s EBU Tech 3342 floor
    short = np.stack([0.3 * np.sin(2 * np.pi * 220 * t)] * 2, axis=1).astype(np.float32)
    snapshot = hear_snapshot(
        candidate_id="A",
        field_id="field_A",
        candidate_samples=short,
        candidate_sample_rate=sr,
        source_samples=short,
        source_sample_rate=sr,
    )
    reasons = {row["reason"] for row in snapshot["uncertainty"]}
    assert "EVIDENCE_INCOMPLETE" in reasons


def test_technical_judgment_consumes_candidate_measurements(source_wav):
    """The gate must be the existing one, and its output must be usable."""
    snapshot = _snapshot(source_wav)
    judge_block = snapshot["judge"]
    assert judge_block["technical_status"] in {"SAFE_TO_LISTEN", "BLOCKED"}
    assert set(judge_block) >= {
        "technical_status", "blocking_flags", "warnings",
        "workflow_decision", "risk_flags", "artistic_approval_granted",
    }
    assert judge_block["artistic_approval_granted"] is False
    assert judge_block["human_listening_required"] is True


def test_judge_candidate_matches_a_direct_call_to_the_existing_gate(source_wav):
    import soundfile as sf

    source, sr = sf.read(str(source_wav), always_2d=False)
    source = np.asarray(source)
    field = probe_fields()[2]
    candidate, _ = render_array(source, sr, field)

    source_metrics = measure_audio(source, sr)
    candidate_metrics = measure_audio(candidate, sr)
    from moodify.auditory.comparison import ScanEvidence, compute_deltas
    from moodify.auditory.profiles import MFY_WSE_SCAN_PROFILE_001

    def evidence(metrics):
        return ScanEvidence(
            case_id="x", profile=MFY_WSE_SCAN_PROFILE_001,
            profile_hash=MFY_WSE_SCAN_PROFILE_001.hash(),
            duration_s=metrics["duration"]["value"], channels=metrics["channels"]["value"],
            metrics=metrics, timeline=[], arrays={},
        )

    deltas = compute_deltas(evidence(source_metrics), evidence(candidate_metrics))
    direct = evaluate_risk_flags(deltas.metric_delta, source_metrics, candidate_metrics)
    block = judge_candidate(source_metrics, candidate_metrics, deltas.metric_delta)

    assert {flag.code for flag in direct} == {row["code"] for row in block["risk_flags"]}
    assert block["blocking_flags"] == [f.code for f in direct if f.severity == "BLOCKING"]


def test_original_reference_carries_no_self_comparison(source_wav):
    import soundfile as sf

    source, sr = sf.read(str(source_wav), always_2d=False)
    source = np.asarray(source)
    snapshot = hear_snapshot(
        candidate_id="ORIGINAL",
        field_id=None,
        candidate_samples=source,
        candidate_sample_rate=sr,
        source_samples=source,
        source_sample_rate=sr,
        is_reference=True,
    )
    assert snapshot["is_reference"] is True
    assert snapshot["source_comparison"] is None
    assert snapshot["judge"]["technical_status"] == "REFERENCE"
    assert snapshot["metrics"]["integrated_lufs"]["value"] is not None


def test_summarize_exposes_only_measurements(source_wav):
    import soundfile as sf

    samples, sr = sf.read(str(source_wav), always_2d=False)
    summary = summarize(measure_audio(np.asarray(samples), sr))
    assert summary["integrated_lufs"] is not None
    assert summary["channels"] == 2
    assert "score" not in " ".join(summary), "no artistic score may be invented in v0"
