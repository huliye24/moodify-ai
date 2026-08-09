"""Feature registry for representation planes (MFY-PHASE1-DEPTH-003).

Every feature plane resolves to one Phase I-A metric definition from
the measurement registry (authority class, unit, algorithm version,
missing-value policy). Band definitions are centralized here; the
representation path uses exactly one band set.
"""

from __future__ import annotations

from typing import Any

from moodify.auditory.measurement_registry import load_registry

# Centralized canonical band definitions (representation authority).
BANDS: tuple[tuple[str, float, float], ...] = (
    ("sub", 20, 60),
    ("bass", 60, 120),
    ("low_mid", 120, 250),
    ("mid", 250, 500),
    ("core_mid", 500, 2000),
    ("presence", 2000, 5000),
    ("brilliance", 5000, 10000),
    ("air", 10000, 16000),
)

# feature plane -> Phase I-A metric id (for authority resolution)
PLANE_METRIC_MAP: dict[str, str] = {
    "sample_peak_db": "sample_peak_dbfs",
    "rms_db": "rms_dbfs",
    "clipping_ratio": "clipping_sample_ratio",
    "near_clipping_ratio": "near_clipping_sample_count",
    "silent": "silence_ratio",
    "stereo_correlation": "stereo_correlation",
    "mid_energy": "mid_energy_ratio",
    "side_energy": "side_energy_ratio",
    "spectral_centroid_hz": "spectral_centroid_hz",
    "hf_ratio": "band_energy_*",
    "hf_cutoff_estimate": "estimated_high_frequency_cutoff_hz",
    "crest_db": "crest_factor_db",
    "short_term_lufs": "integrated_lufs",
}


def resolve_metric(metric_id: str) -> dict[str, Any]:
    """Resolve a plane feature to its Phase I-A authority entry."""
    registry = load_registry()
    entry = registry["metrics"].get(metric_id)
    if entry is None:
        return {
            "metric_id": metric_id,
            "unit": "unknown",
            "authority_class": "UNRESOLVED",
            "algorithm_version": registry["algorithm_version"],
            "missing_value_policy": "UNAVAILABLE",
            "known_limitations": "metric not present in measurement registry",
        }
    return {
        "metric_id": metric_id,
        "unit": entry.get("unit", "unknown"),
        "authority_class": entry.get("authority_class", "UNKNOWN"),
        "algorithm_version": registry["algorithm_version"],
        "missing_value_policy": "UNAVAILABLE" if entry.get("authority_class") == "ESTIMATOR" else "measured",
        "known_limitations": entry.get("known_limitations"),
    }


def plane_meta(feature_name: str) -> dict[str, Any]:
    """Authority metadata for one plane feature."""
    metric_id = PLANE_METRIC_MAP.get(feature_name)
    if metric_id is None:
        return {"metric_id": feature_name, "authority_class": "DESCRIPTOR", "unit": "unknown"}
    return resolve_metric(metric_id)
