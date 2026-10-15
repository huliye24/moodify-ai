"""Hear snapshot — what Moodify heard in one rendered field candidate.

This module **reuses** the existing auditory layer verbatim
(``moodify.auditory.metrics`` / ``.stereo`` / ``.comparison`` / ``.judgment``).
It reimplements no measurement: a second measurement implementation would be a
second measurement authority, which is exactly what the repository forbids.

v0 hearing is measurement + provenance + explicit uncertainty.  It produces no
artistic score, no "better/worse" verdict, and no aggregate number.  The
technical block is a **safety / regression guard only** — v0 has no approved
processing goal, so :func:`judge_candidate` never claims intended improvement.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from moodify.auditory.comparison import ScanEvidence, compute_deltas
from moodify.auditory.judgment import evaluate_risk_flags, judge
from moodify.auditory.metrics import compute_metrics
from moodify.auditory.models import MetricValue
from moodify.auditory.profiles import MFY_WSE_SCAN_PROFILE_001
from moodify.auditory.stereo import compute_stereo_metrics
from moodify.auditory.uncertainty import Uncertainty
from moodify.wavefield.models import HEAR_SCHEMA

#: Deltas worth carrying inline.  The full metric record is already in
#: ``metrics``; this list keeps a reader from having to scan forty rows to see
#: level, dynamics, spectral and stereo movement.
COMPARISON_METRICS: tuple[str, ...] = (
    "integrated_lufs",
    "true_peak_dbfs",
    "sample_peak_dbfs",
    "rms_dbfs",
    "crest_factor_db",
    "plr_db",
    "spectral_centroid_hz",
    "spectral_rolloff_85_hz",
    "spectral_flatness",
    "estimated_high_frequency_cutoff_hz",
    "stereo_correlation",
    "stereo_width_proxy",
    "side_to_mid_db",
    "mid_energy_ratio",
    "side_energy_ratio",
    "negative_correlation_ratio",
    "phase_risk_ratio",
    "bass_60_120_hz",
    "core_mid_500_2000_hz",
    "air_10000_16000_hz",
)

#: Claim class of every number in this file.  Declared so no reader can mistake
#: a stereo projection for a measured sound field.
CLAIM_CLASS = "PERCEPTUAL_VIRTUAL_FIELD"
CALIBRATION_STATUS = "UNCALIBRATED_ENGINEERING_DEFAULT"


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------


def measure_audio(samples: np.ndarray, sample_rate: int) -> dict:
    """Full metric record for one signal.

    Composes the same primitives that
    :func:`moodify.auditory.service.scan_audio` uses, so the resulting keys are
    byte-compatible with a scan report and can be consumed unchanged by
    :func:`moodify.auditory.judgment.evaluate_risk_flags`.  It skips the
    ffmpeg spectrogram stage, which hearing does not need.
    """
    x = np.asarray(samples)
    if x.ndim > 2:
        raise ValueError(f"expected mono/stereo audio, got shape {x.shape}")
    if x.size and not np.all(np.isfinite(x)):
        raise ValueError("cannot hear non-finite audio")

    metrics = compute_metrics(x, int(sample_rate), None)
    metrics.update(compute_stereo_metrics(x))

    frames = int(x.shape[0])
    channels = 1 if x.ndim == 1 else int(x.shape[1])
    duration_s = round(frames / float(sample_rate), 3) if sample_rate else 0.0
    metrics["duration"] = MetricValue(duration_s, "s", "soundfile").to_dict()
    metrics["channels"] = MetricValue(channels, "ch", "direct").to_dict()
    metrics["sample_rate"] = MetricValue(int(sample_rate), "Hz", "soundfile").to_dict()
    return metrics


def _metric_value(metrics: Mapping, key: str):
    entry = metrics.get(key)
    return entry.get("value") if isinstance(entry, dict) else None


def _scan_evidence(metrics: dict, sample_rate: int) -> ScanEvidence:
    return ScanEvidence(
        case_id="wavefield",
        profile=MFY_WSE_SCAN_PROFILE_001,
        profile_hash=MFY_WSE_SCAN_PROFILE_001.hash(),
        duration_s=float(_metric_value(metrics, "duration") or 0.0),
        channels=int(_metric_value(metrics, "channels") or 1),
        metrics=metrics,
        timeline=[],
        arrays={},
    )


# ---------------------------------------------------------------------------
# Technical gate (the v0 Judge boundary)
# ---------------------------------------------------------------------------


def judge_candidate(
    source_metrics: Mapping, candidate_metrics: Mapping, metric_delta: Mapping
) -> dict:
    """Run the existing conservative technical gate over one candidate.

    Returns the three fields the Wave Field contract records —
    ``technical_status``, ``blocking_flags``, ``warnings`` — plus the auditor's
    own verdict for provenance.  No artistic approval is ever granted here.
    """
    flags = evaluate_risk_flags(dict(metric_delta), dict(source_metrics), dict(candidate_metrics))
    verdict = judge(dict(metric_delta), dict(source_metrics), dict(candidate_metrics), None, flags)
    blocking = [f.code for f in flags if f.severity == "BLOCKING"]
    return {
        "technical_status": "BLOCKED" if blocking else "SAFE_TO_LISTEN",
        "basis": "safety / regression guard only — wavefield v0 declares no processing goal",
        "blocking_flags": blocking,
        "warnings": [f.code for f in flags if f.severity == "WARNING"],
        "informational_flags": [f.code for f in flags if f.severity == "INFO"],
        "workflow_decision": verdict.workflow_decision,
        "technical_assessment": verdict.technical_assessment,
        "reasons": list(verdict.reasons),
        "risk_flags": [f.to_dict() for f in flags],
        "human_listening_required": verdict.human_listening_required,
        "artistic_approval_granted": verdict.artistic_approval_granted,
    }


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------


def _uncertainties(metrics: Mapping, duration_s: float) -> list[dict]:
    uncertainty: list[Uncertainty] = [
        Uncertainty(
            "OUT_OF_SCOPE",
            "a single mono/stereo file supports a source-field / stereo-field "
            "projection only; this is not a measured three-dimensional sound "
            "pressure field",
        ),
        Uncertainty(
            "VALIDATION_LIMIT",
            "algorithmic-room-v0.1 is an uncalibrated engineering default; no "
            "listening calibration exists for these field parameters",
        ),
    ]
    unavailable = sorted(
        key
        for key, entry in metrics.items()
        if not key.startswith("_")
        and isinstance(entry, dict)
        and entry.get("status") == "UNAVAILABLE"
    )
    if unavailable:
        uncertainty.append(
            Uncertainty(
                "MEASUREMENT_UNCERTAINTY",
                f"metrics unavailable on this material: {', '.join(unavailable)}",
            )
        )
    if duration_s < 6.0:
        uncertainty.append(
            Uncertainty(
                "EVIDENCE_INCOMPLETE",
                "shorter than 6 s: loudness range (EBU Tech 3342) cannot be measured",
            )
        )
    return [item.to_dict() for item in uncertainty]


def hear_snapshot(
    *,
    candidate_id: str,
    field_id: str,
    candidate_samples: np.ndarray,
    candidate_sample_rate: int,
    source_samples: np.ndarray,
    source_sample_rate: int,
    source_sha256: str | None = None,
    candidate_sha256: str | None = None,
    render_result: Mapping | None = None,
    source_metrics: Mapping | None = None,
    is_reference: bool = False,
) -> dict:
    """Build the machine-readable hearing snapshot for one candidate.

    ``is_reference=True`` marks the ORIGINAL entry: it is the comparison
    baseline, so it carries no self-comparison and no technical verdict.
    """
    metrics = measure_audio(candidate_samples, candidate_sample_rate)

    provenance: dict = {
        "engine": (render_result or {}).get("field", {}).get("engine", None),
        "field_id": field_id,
        "claim_class": CLAIM_CLASS,
        "physically_exact_simulation": False,
        "calibration_status": CALIBRATION_STATUS,
        "engine_version": (render_result or {}).get("engine_version", None),
        "renderer": (render_result or {}).get("renderer", None),
        "source_sha256": source_sha256,
        "candidate_sha256": candidate_sha256,
    }

    if is_reference:
        technical = {
            "technical_status": "REFERENCE",
            "basis": "ORIGINAL is the comparison baseline",
            "blocking_flags": [],
            "warnings": [],
            "informational_flags": [],
            "workflow_decision": None,
            "technical_assessment": None,
            "reasons": [],
            "risk_flags": [],
            "human_listening_required": True,
            "artistic_approval_granted": False,
        }
        comparison = None
        duration_s = float(_metric_value(metrics, "duration") or 0.0)
    else:
        baseline = dict(source_metrics) if source_metrics is not None else measure_audio(
            source_samples, source_sample_rate
        )
        deltas = compute_deltas(
            _scan_evidence(baseline, source_sample_rate),
            _scan_evidence(metrics, candidate_sample_rate),
        )
        correction = deltas.normalization_gain_db if deltas.normalization_valid else None
        comparison = {
            "reference": "ORIGINAL",
            "normalization_gain_db": deltas.normalization_gain_db,
            "normalization_valid": deltas.normalization_valid,
            "normalization_method": deltas.normalized_method,
            # How much to attenuate/boost the candidate so its integrated
            # loudness matches the source while auditioning.  Recorded, never
            # hidden, and never written into the canonical render.
            "audition_correction_db": correction,
            "metric_delta": {
                key: deltas.metric_delta[key]
                for key in COMPARISON_METRICS
                if key in deltas.metric_delta
            },
            "normalized_band_delta": deltas.normalized_band_deltas,
        }
        technical = judge_candidate(baseline, metrics, deltas.metric_delta)
        duration_s = float(_metric_value(metrics, "duration") or 0.0)

    return {
        "schema": HEAR_SCHEMA,
        "candidate_id": candidate_id,
        "field_id": field_id,
        "is_reference": is_reference,
        "metrics": metrics,
        "source_comparison": comparison,
        "judge": technical,
        "uncertainty": _uncertainties(metrics, duration_s),
        "provenance": provenance,
    }


def hear_snapshot_for_file(
    *,
    candidate_id: str,
    field_id: str,
    candidate_path: str,
    source_path: str,
    render_result: Mapping | None = None,
    source_metrics: Mapping | None = None,
    is_reference: bool = False,
) -> dict:
    """Convenience wrapper that decodes both files and builds the snapshot."""
    from moodify.audio_io import load_audio

    cand, cand_sr = load_audio(candidate_path, always_2d=False)
    src, src_sr = load_audio(source_path, always_2d=False)
    return hear_snapshot(
        candidate_id=candidate_id,
        field_id=field_id,
        candidate_samples=cand,
        candidate_sample_rate=cand_sr,
        source_samples=src,
        source_sample_rate=src_sr,
        render_result=render_result,
        source_metrics=source_metrics,
        is_reference=is_reference,
    )


def summarize(metrics: Mapping) -> dict:
    """The handful of numbers the minimum UI shows, straight from the record."""
    stereo_available = not bool(metrics.get("_mono", False))
    return {
        "integrated_lufs": _metric_value(metrics, "integrated_lufs"),
        "true_peak_dbfs": _metric_value(metrics, "true_peak_dbfs"),
        "sample_peak_dbfs": _metric_value(metrics, "sample_peak_dbfs"),
        "crest_factor_db": _metric_value(metrics, "crest_factor_db"),
        "negative_correlation_ratio": _metric_value(metrics, "negative_correlation_ratio"),
        "phase_risk_ratio": _metric_value(metrics, "phase_risk_ratio"),
        "stereo_correlation": _metric_value(metrics, "stereo_correlation") if stereo_available else None,
        "side_to_mid_db": _metric_value(metrics, "side_to_mid_db") if stereo_available else None,
        "stereo_width_proxy": _metric_value(metrics, "stereo_width_proxy") if stereo_available else None,
        "duration_seconds": _metric_value(metrics, "duration"),
        "sample_rate": _metric_value(metrics, "sample_rate"),
        "channels": _metric_value(metrics, "channels"),
    }


def hearing_summaries(snapshots: Sequence[Mapping]) -> dict:
    """``{candidate_id: summary}`` for a list of snapshots (convenience for UIs)."""
    return {
        str(snapshot.get("candidate_id")): summarize(snapshot.get("metrics", {}))
        for snapshot in snapshots
    }
