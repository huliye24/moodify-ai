"""Era Diagnostic engine v0.1 (MFY-CR-P03).

Decision principles (from 02_DIAGNOSTIC_MODEL.md):
- Diagnose before reconstruct; era is context, not a preset.
- A POSSIBLE_TECHNICAL_LIMITATION needs >= 1 primary measurement + >= 1
  corroborating measurement or temporal pattern + a known ambiguity statement.
- A single proxy never produces HIGH confidence.
- Uncertainty reduces intervention: LOW confidence is never automatic authority.
- No finding authorizes reconstruction (P03 outputs no RECONSTRUCT_NOW).
"""

from __future__ import annotations

from datetime import datetime, timezone

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)
from moodify.era_diagnostic.thresholds import ERA_DIAGNOSTIC_POLICY_V1

_VERSION = ERA_DIAGNOSTIC_POLICY_V1["version"]
_TH = ERA_DIAGNOSTIC_POLICY_V1["thresholds"]
_ELIGIBLE = ERA_DIAGNOSTIC_POLICY_V1["metric_eligibility"]

_DISALLOWED_STATUS_FOR_CONFIDENCE = {
    FindingStatus.NOT_APPLICABLE,
    FindingStatus.NOT_SUPPORTED_IN_V0_1,
}


def _metric(metrics: dict, name: str) -> float | int | None:
    entry = metrics.get(name)
    if not isinstance(entry, dict):
        return None
    value = entry.get("value")
    if value is None or not isinstance(value, (int, float)):
        return None
    return value


def _human_review(status: FindingStatus, confidence: ConfidenceLevel | None) -> bool:
    if status not in {FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
                      FindingStatus.LIKELY_ARTISTIC_CHARACTER}:
        return False
    return confidence == ConfidenceLevel.LOW


# ---------------------------------------------------------------------------
# Detectors. Each detector declares its input metric names; a policy test
# enforces that every declared input is ELIGIBLE_FOR_DIAGNOSTIC.
# ---------------------------------------------------------------------------

def detect_bandwidth(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-01 — possible bandwidth limitation from medium/transfer/source loss."""
    cutoff = _metric(metrics, "estimated_high_frequency_cutoff_hz")
    rolloff95 = _metric(metrics, "spectral_rolloff_95_hz")
    presence = _metric(metrics, "presence_2000_5000_hz")
    t = _TH["bandwidth"]

    if cutoff is None:
        return _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        "cutoff estimator unavailable", ["estimated_high_frequency_cutoff_hz"],
                        ConfidenceLevel.LOW, ctx, ["estimator missing from metric record"])

    if cutoff >= t["clean_cutoff_hz"]:
        return _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
                        FindingStatus.NOT_APPLICABLE,
                        "no bandwidth limitation observed (HF cutoff >= 16 kHz)",
                        ["estimated_high_frequency_cutoff_hz"], None, ctx, [])

    corroborated = rolloff95 is not None and rolloff95 <= cutoff * (1.0 / t["rolloff_95_corrob_ratio"])
    dark_by_nature = presence is not None and presence < t["presence_band_min_ratio"]

    if dark_by_nature:
        return _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
                        FindingStatus.LIKELY_ARTISTIC_CHARACTER,
                        f"low HF cutoff (~{cutoff:.0f} Hz) but presence band is nearly empty; "
                        "source is likely dark/sparse by arrangement or instrument character",
                        ["estimated_high_frequency_cutoff_hz", "presence_2000_5000_hz"],
                        ConfidenceLevel.LOW, ctx,
                        ["dark mix or sparse arrangement is an artistic choice; "
                         "cannot be distinguished from technical loss without more evidence"])

    if not corroborated:
        return _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        f"low HF cutoff (~{cutoff:.0f} Hz) but no corroborating rolloff pattern",
                        ["estimated_high_frequency_cutoff_hz", "spectral_rolloff_95_hz"],
                        ConfidenceLevel.LOW, ctx,
                        ["rolloff estimator may be unstable; single-proxy evidence"])

    if cutoff <= t["severe_cutoff_hz"]:
        confidence = ConfidenceLevel.HIGH
    elif cutoff <= t["strong_cutoff_hz"]:
        confidence = ConfidenceLevel.MEDIUM
    else:
        confidence = ConfidenceLevel.LOW
    return _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
                    FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
                    f"HF cutoff ~{cutoff:.0f} Hz corroborated by rolloff-95 "
                    f"({rolloff95:.0f} Hz); consistent with bandwidth-limited chain",
                    ["estimated_high_frequency_cutoff_hz", "spectral_rolloff_95_hz"],
                    confidence, ctx,
                    ["could be arrangement-dependent (dark production); "
                     "cutoff estimator is a proxy, not a universal truth"])


def detect_noise(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-02 — persistent hiss/hum/broadband noise that is more technical than musical."""
    floor = _metric(metrics, "estimated_noise_floor_dbfs")
    silence = _metric(metrics, "silence_ratio")
    flatness = _metric(metrics, "spectral_flatness")
    t = _TH["noise"]

    if floor is None:
        return _finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        "noise floor estimator unavailable", ["estimated_noise_floor_dbfs"],
                        ConfidenceLevel.LOW, ctx, ["estimator missing from metric record"])

    if floor < t["elevated_floor_dbfs"]:
        return _finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE,
                        FindingStatus.NOT_APPLICABLE,
                        f"no elevated noise floor observed (p10 frame RMS ~{floor:.1f} dBFS)",
                        ["estimated_noise_floor_dbfs"], None, ctx, [])

    if silence is None or silence < t["min_silence_ratio"]:
        return _finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        f"elevated floor (~{floor:.1f} dBFS) but no reliable quiet windows "
                        "(silence_ratio insufficient); cannot separate noise from music texture",
                        ["estimated_noise_floor_dbfs", "silence_ratio"],
                        ConfidenceLevel.LOW, ctx,
                        ["music without quiet regions makes noise-vs-texture "
                         "distinction unreliable"])

    if floor >= t["strong_floor_dbfs"]:
        confidence = ConfidenceLevel.MEDIUM
    else:
        confidence = ConfidenceLevel.LOW

    if flatness is not None and flatness < 0.05:
        ambiguity = ("low spectral flatness suggests tonal content; could be hum "
                     "(technical) or a musical tone (artistic)")
    else:
        ambiguity = ("tape texture, air and reverb tails may be artistic rather than noise")
    return _finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE,
                    FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
                    f"elevated noise floor (~{floor:.1f} dBFS) with quiet windows present",
                    ["estimated_noise_floor_dbfs", "silence_ratio"],
                    confidence, ctx, [ambiguity])


def detect_dynamics(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-03 — dynamic constraint/damage from clipping, over-compression or transfer."""
    clip = _metric(metrics, "clipping_sample_ratio")
    tp = _metric(metrics, "true_peak_dbfs")
    lra = _metric(metrics, "loudness_range_lu")
    crest = _metric(metrics, "crest_factor_db")
    t = _TH["dynamic"]

    if clip is None:
        return _finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        "clipping estimator unavailable", ["clipping_sample_ratio"],
                        ConfidenceLevel.LOW, ctx, ["estimator missing from metric record"])

    if clip >= t["clipping_ratio"]:
        at_ceiling = tp is not None and tp >= t["peak_ceiling_dbfs"]
        hard_ceiling = tp is not None and tp >= t["peak_hard_ceiling_dbfs"]
        if hard_ceiling or (clip >= t["strong_clipping_ratio"] and at_ceiling):
            confidence = ConfidenceLevel.MEDIUM
        elif at_ceiling:
            confidence = ConfidenceLevel.LOW
        else:
            confidence = ConfidenceLevel.LOW
            return _finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
                            FindingStatus.OBSERVED,
                            f"clipped samples present ({clip:.2e} ratio) but peaks not at ceiling; "
                            "may be intentional distortion",
                            ["clipping_sample_ratio", "true_peak_dbfs"],
                            confidence, ctx,
                            ["distorted production may be intentional saturation"])
        return _finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
                        FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
                        f"clipping observed ({clip:.2e} ratio) with peaks at/above "
                        f"{tp:.1f} dBFS; consistent with damaged or hotly-mastered transfer",
                        ["clipping_sample_ratio", "true_peak_dbfs"],
                        confidence, ctx,
                        ["clipping may be intentional distortion in some productions"])

    low_lra = lra is not None and lra < t["low_lra_lu"]
    low_crest = crest is not None and crest < t["low_crest_db"]
    if low_lra and low_crest:
        return _finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
                        FindingStatus.OBSERVED,
                        f"low dynamics (LRA {lra:.1f} LU, crest {crest:.1f} dB) but no clipping "
                        "evidence; compression aesthetic cannot be called a defect",
                        ["loudness_range_lu", "crest_factor_db"],
                        ConfidenceLevel.LOW, ctx,
                        ["compressed genre aesthetic is a deliberate production choice"])

    return _finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
                    FindingStatus.NOT_APPLICABLE,
                    "no dynamic constraint/damage evidence (no clipping, normal dynamics)",
                    ["clipping_sample_ratio"], None, ctx, [])


def detect_stereo(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-04 — stereo/phase limitation from mono transfer, collapse or phase defects."""
    corr = _metric(metrics, "stereo_correlation")
    phase_risk = _metric(metrics, "phase_risk_ratio")
    neg_corr = _metric(metrics, "negative_correlation_ratio")
    t = _TH["stereo"]

    if corr is None:
        return _finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        "stereo correlation unavailable", ["stereo_correlation"],
                        ConfidenceLevel.LOW, ctx, ["stereo metrics missing"])

    if corr >= t["mono_correlation"]:
        return _finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION,
                        FindingStatus.LIKELY_ARTISTIC_CHARACTER,
                        f"essentially mono signal (correlation {corr:.4f}); "
                        "mono is an artistic choice, not automatically a defect",
                        ["stereo_correlation"], ConfidenceLevel.LOW, ctx,
                        ["could be a mono transfer, but mono itself cannot be "
                         "called technical damage without more evidence"])

    phase_anomaly = (phase_risk is not None and phase_risk >= t["phase_risk_ratio"]) or \
                    (neg_corr is not None and neg_corr >= t["negative_corr_ratio"])
    if phase_anomaly:
        corroborated = (phase_risk is not None and phase_risk >= t["phase_risk_ratio"]) and \
                       (neg_corr is not None and neg_corr >= t["negative_corr_ratio"])
        confidence = ConfidenceLevel.MEDIUM if corroborated else ConfidenceLevel.LOW
        return _finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION,
                        FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
                        f"phase anomalies present (phase_risk {phase_risk or 0:.3f}, "
                        f"negative_correlation {neg_corr or 0:.3f}); possible fold/phase defect",
                        ["phase_risk_ratio", "negative_correlation_ratio"],
                        confidence, ctx,
                        ["wide or phasey productions may be intentional"])

    if corr >= t["narrow_correlation"]:
        return _finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION,
                        FindingStatus.OBSERVED,
                        f"narrow stereo (correlation {corr:.3f}); NARROW_BY_CHARACTER "
                        "vs POSSIBLE_TECHNICAL_COLLAPSE cannot be distinguished in v0.1",
                        ["stereo_correlation"], ConfidenceLevel.LOW, ctx,
                        ["narrow vintage stereo may be character or collapse; "
                         "insufficient evidence either way"])

    return _finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION,
                    FindingStatus.NOT_APPLICABLE,
                    f"no stereo/phase limitation evidence (correlation {corr:.3f})",
                    ["stereo_correlation"], None, ctx, [])


def detect_congestion(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-05 — possible spectral congestion. v0.1 is observational only: it
    may say 'possibly congested' but never that EQ is indicated."""
    flatness = _metric(metrics, "spectral_flatness")
    core_mid = _metric(metrics, "core_mid_500_2000_hz")
    t = _TH["congestion"]

    if flatness is None:
        return _finding(DiagnosticCategory.ED_05_SPECTRAL_CONGESTION,
                        FindingStatus.INSUFFICIENT_EVIDENCE,
                        "spectral flatness unavailable", ["spectral_flatness"],
                        ConfidenceLevel.LOW, ctx, ["descriptor missing"])

    peaky = flatness < t["peaky_flatness"]
    if peaky and core_mid is not None and core_mid > 0.3:
        return _finding(DiagnosticCategory.ED_05_SPECTRAL_CONGESTION,
                        FindingStatus.OBSERVED,
                        f"spectrally dense (flatness {flatness:.3f}, core-mid "
                        f"{core_mid:.2f}); possible congestion observed — "
                        "no defect claim in v0.1",
                        ["spectral_flatness", "core_mid_500_2000_hz"],
                        ConfidenceLevel.LOW, ctx,
                        ["dense arrangement is an artistic choice; congestion "
                         "cannot be separated from arrangement density in v0.1"])

    return _finding(DiagnosticCategory.ED_05_SPECTRAL_CONGESTION,
                    FindingStatus.NOT_APPLICABLE,
                    "no congestion signal observed", ["spectral_flatness"], None, ctx, [])


def detect_transfer(metrics: dict, ctx: dict) -> EraDiagnosticFinding:
    """ED-06 — transfer/encoding degradation.

    v0.1 has no validated detector for codec/transcode artifacts, so the
    category is NOT_SUPPORTED_IN_V0_1 by design. A low sample rate is recorded
    as an observation only, never a defect claim.
    """
    sr = _metric(metrics, "sample_rate")
    t = _TH["transfer"]

    if sr is not None and sr < t["low_sample_rate_hz"]:
        return _finding(DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION,
                        FindingStatus.OBSERVED,
                        f"source sample rate {sr} Hz is below 44.1 kHz; possible "
                        "downsampled/legacy transfer — recorded, not a defect claim",
                        ["sample_rate"], ConfidenceLevel.LOW, ctx,
                        ["low sample rate may be the original medium (e.g. 32 kHz "
                         "game/telephony audio) rather than a loss"])

    return _finding(DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION,
                    FindingStatus.NOT_SUPPORTED_IN_V0_1,
                    "no validated transfer/encoding detector in v0.1; "
                    "codec/transcode degradation is NOT_SUPPORTED",
                    ["sample_rate"], None, ctx,
                    ["reliable block/codec artifact detection is deferred"])


_DETECTORS = (
    detect_bandwidth,
    detect_noise,
    detect_dynamics,
    detect_stereo,
    detect_congestion,
    detect_transfer,
)

def _detector_inputs(detector) -> tuple[str, ...]:
    import inspect

    source = inspect.getsource(detector)
    return tuple(sorted({m for m in _ELIGIBLE if f'"{m}"' in source}))


DETECTOR_INPUTS: dict[str, tuple[str, ...]] = {
    detector.__name__: _detector_inputs(detector)
    for detector in _DETECTORS
}


def _finding(category, status, reasoning, refs, confidence, ctx, ambiguities) -> EraDiagnosticFinding:
    created_at = ctx["created_at"]
    return EraDiagnosticFinding(
        category=category,
        status=status,
        finding_id=f"{category.value}-{ctx['run_index']}",
        reasoning_summary=reasoning,
        measurement_refs=tuple(refs),
        confidence=confidence,
        known_ambiguities=tuple(ambiguities),
        scope=ctx.get("scope", "era-diagnostic-v0.1"),
        requires_human_review=_human_review(status, confidence),
        production_case_id=ctx.get("production_case_id"),
        evidence_refs=ctx.get("evidence_refs", ()),
        uncertainty_reason=ctx.get("uncertainty_reason"),
        created_at=created_at,
        version=ctx.get("version", "era-diagnostic-v0.1"),
    )


def run_era_diagnostic(
    metrics: dict,
    *,
    production_case_id: str | None = None,
    scope: str = "era-diagnostic-v0.1",
    created_at: str | None = None,
    evidence_refs: tuple[str, ...] = (),
    uncertainty_reason: str | None = None,
) -> list[EraDiagnosticFinding]:
    """Run the v0.1 diagnostic over a metric record (the same dict shape
    produced by ``moodify.auditory.metrics.compute_metrics``). Returns
    findings ordered by category (ED-01..ED-06).

    No finding authorizes processing.
    """
    ctx = {
        "created_at": created_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_index": 0,
        "scope": scope,
        "production_case_id": production_case_id,
        "evidence_refs": evidence_refs,
        "uncertainty_reason": uncertainty_reason,
        "version": "era-diagnostic-v0.1",
    }
    findings: list[EraDiagnosticFinding] = []
    for idx, detector in enumerate(_DETECTORS, start=1):
        ctx["run_index"] = idx
        findings.append(detector(metrics, ctx))
    return findings
