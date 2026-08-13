"""Scientific listening stack — layer contract and Machine Finding mapping.

MFY_EAR_SCIENTIFIC_LISTENING_STACK_001:
- reuse validated auditory implementations; no algorithm duplication.
- three cost tiers: FAST / STANDARD / DEEP.
- every first-phase conclusion is an observable phenomenon mapped to a
  MachineFinding (allowed types from contracts.machine_finding); no aesthetic
  conclusions, no overall quality score.
"""

from __future__ import annotations

from enum import Enum

from moodify.auditory.profiles import ScanProfile
from moodify.contracts.machine_finding import FindingType

# ---------------------------------------------------------------------------
# Cost tiers (profile selection for the Case Runner)
# ---------------------------------------------------------------------------


class CostTier(str, Enum):
    FAST = "FAST"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


TIER_DEFAULT_PROFILE: dict[CostTier, str] = {
    CostTier.FAST: "MFY-WSE-SCAN-FAST-001",
    CostTier.STANDARD: "MFY-WSE-SCAN-PROFILE-001",
    CostTier.DEEP: "MFY-WSE-SCAN-DEEP-001",
}

TIER_BUDGET: dict[CostTier, str] = {
    CostTier.FAST: "approx 2-6s wall per 60s audio (22050 Hz, fft 2048)",
    CostTier.STANDARD: "approx 6-20s wall per 60s audio (48000 Hz, fft 8192)",
    CostTier.DEEP: "approx 20-90s wall per 60s audio (48000 Hz, fft 16384, finer timeline)",
}

# ---------------------------------------------------------------------------
# Layer contract: V1 metrics per layer (keys exist in scan metrics.json)
# ---------------------------------------------------------------------------


class Layer(str, Enum):
    WSE = "wse"  # waveform/spectral/energetic
    MSE = "mse"  # micro-structural/temporal
    PPE = "ppe"  # production/case evidence


LAYER_METRICS: dict[Layer, dict[str, str]] = {
    Layer.WSE: {
        "integrated_lufs": "LUFS",
        "loudness_range_lu": "LU",
        "true_peak_dbfs": "dBFS",
        "sample_peak_dbfs": "dBFS",
        "rms_dbfs": "dBFS",
        "crest_factor_db": "dB",
        "clipping_sample_ratio": "ratio",
        "silence_ratio": "ratio",
    },
    Layer.MSE: {
        "spectral_centroid_hz": "Hz",
        "spectral_rolloff_hz": "Hz",
        "spectral_flatness": "ratio",
        "spectral_flux": "energy",
        "temporal_energy_variance": "energy",
    },
    Layer.PPE: {
        "duration": "s",
        "channels": "ch",
        "sample_rate": "Hz",
        "source_sha256": "sha256",
        "profile_hash": "hash",
    },
}


def layer_metric_keys(layer: Layer) -> dict[str, str]:
    return LAYER_METRICS[layer]


# ---------------------------------------------------------------------------
# Machine Finding mapping (observable phenomena only)
# ---------------------------------------------------------------------------


def map_metrics_to_findings(
    metrics: dict,
    *,
    domain: str,
    clip_threshold_ratio: float = 1e-6,
    silence_threshold_ratio: float = 0.99,
) -> list[dict]:
    """Map a scan metric record to allowed Machine Finding candidates.

    Returns list of {"finding_type", "metric", "value", "confidence"}.
    No aesthetic conclusions are ever produced here.
    """
    findings: list[dict] = []

    def val(key: str) -> float | None:
        entry = metrics.get(key)
        if not entry or entry.get("value") is None:
            return None
        try:
            return float(entry["value"])
        except (TypeError, ValueError):
            return None

    clip_ratio = val("clipping_sample_ratio")
    if clip_ratio is not None and clip_ratio > clip_threshold_ratio:
        findings.append({
            "finding_type": FindingType.CLIPPING_EVENT,
            "metric": "clipping_sample_ratio",
            "value": clip_ratio,
            "confidence": min(1.0, 0.5 + clip_ratio * 10),
        })

    tp = val("true_peak_dbfs")
    if tp is not None and tp > -1.0:
        findings.append({
            "finding_type": FindingType.TRUE_PEAK_EVENT,
            "metric": "true_peak_dbfs",
            "value": tp,
            "confidence": 0.8,
        })

    silence = val("silence_ratio")
    if silence is not None and silence > silence_threshold_ratio:
        findings.append({
            "finding_type": FindingType.INSUFFICIENT_EVIDENCE,
            "metric": "silence_ratio",
            "value": silence,
            "confidence": 0.9,
        })

    spectral_flatness = val("spectral_flatness")
    if spectral_flatness is not None and spectral_flatness > 0.5:
        findings.append({
            "finding_type": FindingType.ENERGY_CHANGE,
            "metric": "spectral_flatness",
            "value": spectral_flatness,
            "confidence": 0.6,
        })

    for f in findings:
        f["domain"] = domain
    return findings


def map_comparison_to_findings(
    metric_delta: dict,
    *,
    domain: str,
    delta_threshold: float = 1.0,
) -> list[dict]:
    """Map a before/after comparison delta to allowed findings (baseline deviation)."""
    findings: list[dict] = []
    for key, delta in metric_delta.items():
        if not isinstance(delta, (int, float)):
            continue
        if abs(delta) >= delta_threshold:
            findings.append({
                "finding_type": FindingType.BASELINE_DEVIATION,
                "metric": key,
                "value": round(float(delta), 3),
                "confidence": 0.7,
                "domain": domain,
            })
    return findings


def resolve_tier_profile(tier: CostTier) -> ScanProfile:
    from moodify.auditory.profiles import get_profile

    return get_profile(TIER_DEFAULT_PROFILE[tier])
