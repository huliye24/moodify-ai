"""Pairwise comparison dimensions over canonical auditory metrics.

Each dimension compares one family of measurements between candidate A and B
and yields A_BETTER / B_BETTER / TIE / INSUFFICIENT_EVIDENCE. Metrics that are
null/unavailable (e.g. stereo metrics on mono input) produce INSUFFICIENT_EVIDENCE
rather than fabricated numbers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricRef:
    key: str
    lower_is_better: bool
    tolerance: float = 0.0
    label: str = ""


def _value(metrics: dict[str, Any], key: str) -> float | None:
    entry = metrics.get(key)
    if not isinstance(entry, dict):
        return None
    value = entry.get("value")
    return float(value) if isinstance(value, (int, float)) and value == value else None


def _band_ratios(metrics: dict[str, Any]) -> list[float]:
    keys = (
        "sub_20_60_hz", "bass_60_120_hz", "low_mid_120_250_hz", "mid_250_500_hz",
        "core_mid_500_2000_hz", "presence_2000_5000_hz", "brilliance_5000_10000_hz",
        "air_10000_16000_hz",
    )
    values = [_value(metrics, key) for key in keys]
    return [v for v in values if v is not None]


def _band_entropy(ratios: list[float]) -> float:
    import math

    total = sum(ratios) or 1.0
    normalized = [r / total for r in ratios]
    return -sum(p * math.log(p) for p in normalized if p > 0) / math.log(len(normalized) or 1)


def _compare_metric(
    a: float | None,
    b: float | None,
    lower_is_better: bool,
    tolerance: float,
) -> tuple[str, float]:
    if a is None or b is None:
        return "INSUFFICIENT_EVIDENCE", 0.0
    if abs(a - b) <= tolerance:
        return "TIE", 0.5
    a_better = a < b if lower_is_better else a > b
    return ("A_BETTER" if a_better else "B_BETTER"), 1.0


def _aggregate(
    name: str,
    refs: list[MetricRef],
    a_metrics: dict[str, Any],
    b_metrics: dict[str, Any],
    explanation: str,
) -> tuple[str, float, tuple[str, ...]]:
    verdicts: list[str] = []
    used: list[str] = []
    missing = False
    for ref in refs:
        a, b = _value(a_metrics, ref.key), _value(b_metrics, ref.key)
        if a is None or b is None:
            missing = True
            used.append(ref.key)
            continue
        verdict, _ = _compare_metric(a, b, ref.lower_is_better, ref.tolerance)
        verdicts.append(verdict)
        used.append(ref.key)
    # Evidence must be complete for a dimension to carry weight.
    if missing:
        return "INSUFFICIENT_EVIDENCE", 0.0, tuple(used)
    if not verdicts:
        return "INSUFFICIENT_EVIDENCE", 0.0, tuple(refs[i].key for i in range(len(refs)))
    a_count = verdicts.count("A_BETTER")
    b_count = verdicts.count("B_BETTER")
    if a_count > b_count:
        return "A_BETTER", 0.8, tuple(used)
    if b_count > a_count:
        return "B_BETTER", 0.8, tuple(used)
    return "TIE", 0.4, tuple(used)


DIMENSION_DEFINITIONS: dict[str, tuple[list[MetricRef], str]] = {
    "signal_integrity": (
        [
            MetricRef("clipping_sample_ratio", lower_is_better=True, tolerance=1e-6, label="clipping"),
            MetricRef("near_clipping_sample_count", lower_is_better=True, tolerance=0, label="near_clipping"),
            MetricRef("invalid_sample_count", lower_is_better=True, tolerance=0, label="invalid_samples"),
            MetricRef("finite_sample_ratio", lower_is_better=False, tolerance=0.0, label="finite_ratio"),
            MetricRef("silence_ratio", lower_is_better=True, tolerance=0.01, label="silence"),
        ],
        "信号完整性：削波/无效样本/静音",
    ),
    "loudness": (
        [
            MetricRef("integrated_lufs", lower_is_better=False, tolerance=0.5, label="lufs"),
            MetricRef("true_peak_dbfs", lower_is_better=True, tolerance=0.2, label="true_peak"),
        ],
        "响度：靠近目标响度（-14 LUFS）、峰顶留有余量",
    ),
    "dynamics": (
        [
            MetricRef("crest_factor_db", lower_is_better=False, tolerance=0.5, label="crest"),
            MetricRef("loudness_range_lu", lower_is_better=False, tolerance=1.0, label="loudness_range"),
        ],
        "动态：压缩程度与动态范围",
    ),
    "spectral_balance": (
        [
            MetricRef("spectral_flatness", lower_is_better=False, tolerance=0.02, label="flatness"),
            MetricRef("estimated_high_frequency_cutoff_hz", lower_is_better=False, tolerance=500.0, label="hf_cutoff"),
            MetricRef("estimated_noise_floor_dbfs", lower_is_better=False, tolerance=1.0, label="noise_floor"),
        ],
        "频谱平衡：平坦度/高域截止/底噪",
    ),
    "stereo_phase": (
        [
            MetricRef("stereo_correlation", lower_is_better=True, tolerance=0.03, label="correlation"),
            MetricRef("negative_correlation_ratio", lower_is_better=True, tolerance=0.01, label="negative_correlation"),
            MetricRef("phase_risk_ratio", lower_is_better=True, tolerance=0.01, label="phase_risk"),
        ],
        "立体声/相位：相关性/反相风险",
    ),
}


def compare_dimensions(
    a_metrics: dict[str, Any],
    b_metrics: dict[str, Any],
    dimension_overrides: dict[str, tuple[list[MetricRef], str]] | None = None,
) -> list[Any]:
    """Compare two canonical metrics dicts across all defined dimensions."""
    from moodify.evaluation.pairwise.models import DimensionResult

    definitions = dimension_overrides or DIMENSION_DEFINITIONS
    results: list[DimensionResult] = []
    for name, (refs, explanation) in definitions.items():
        verdict, confidence, used_refs = _aggregate(name, refs, a_metrics, b_metrics, explanation)
        a_val = _value(a_metrics, refs[0].key)
        b_val = _value(b_metrics, refs[0].key)
        if name == "loudness":
            # Compare distance to the -14 LUFS target rather than raw level.
            a_lufs = _value(a_metrics, "integrated_lufs")
            b_lufs = _value(b_metrics, "integrated_lufs")
            if a_lufs is not None and b_lufs is not None:
                verdict, confidence = _compare_metric(
                    abs(a_lufs - (-14.0)), abs(b_lufs - (-14.0)), True, 0.5
                )
        if name == "spectral_balance":
            a_entropy = _band_entropy(_band_ratios(a_metrics))
            b_entropy = _band_entropy(_band_ratios(b_metrics))
            if a_entropy > 0 and b_entropy > 0:
                verdict, confidence = _compare_metric(a_entropy, b_entropy, False, 0.02)
        if name == "stereo_phase":
            a_channels = a_metrics.get("channels", {}).get("value")
            b_channels = b_metrics.get("channels", {}).get("value")
            if a_channels == 1 or b_channels == 1:
                verdict, confidence = "INSUFFICIENT_EVIDENCE", 0.0
        results.append(
            DimensionResult(
                dimension=name,
                candidate_a_value=a_val,
                candidate_b_value=b_val,
                relative_result=verdict,
                confidence=round(confidence, 3),
                evidence_refs=tuple(used_refs),
                explanation=explanation,
            )
        )
    return results
