"""Threshold sensitivity verification (Layer C 证明: 敏感性报告).

Pure-arithmetic verification over the real judgment code path: for every
rule in ``UNIVERSAL_THRESHOLDS`` this module sweeps the driving quantity and
records where the rule's verdict flips, then compares the observed flip
point against the declared threshold. No audio, no DSP — the input to a
sweep is a synthetic metric delta; the code under test is the production
``evaluate_risk_flags``.

It also maps each rule to the ``auditory.lab`` perturbation ladders that can
produce stimuli crossing the declared threshold (the bridge to the lab
calibration line). The mapping documents reachability only; deriving a
calibrated value from ladder runs is future work and deliberately not
claimed here. ``comparable=False`` marks pairs whose ladder parameter and
threshold live in different units, so "the ladder exceeds the threshold"
would be a guess, not a measurement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from moodify.auditory.judgment import (
    JUDGMENT_RULES_VERSION,
    UNIVERSAL_THRESHOLDS,
)

SENSITIVITY_VERSION = "threshold-sensitivity-v1"

# Binary-search precision for float flip points (iterations on a float64
# bracket; 80 halvings converge to the ulp).
_BISECT_ITERATIONS = 80
# Relative tolerance when comparing an observed flip point to the declared
# threshold value.
_MATCH_TOLERANCE = 1e-6


def _metrics(**pairs) -> dict:
    return {key: {"value": value} for key, value in pairs.items()}


def _delta(**pairs) -> dict:
    return {key: {"absolute_delta": value} for key, value in pairs.items()}


def _fires(code: str, metric_delta: dict, before: dict, after: dict) -> bool:
    from moodify.auditory.judgment import evaluate_risk_flags

    # flag codes are the upper-case form of the rule key (NEW_CLIPPING etc.)
    wanted = code.upper()
    return any(
        flag.code == wanted
        for flag in evaluate_risk_flags(metric_delta, before, after)
    )


def _bisect_flip(code: str, build, lo: float, hi: float) -> float | None:
    """Locate the flip point of ``code`` inside a monotone segment."""
    def fires(value: float) -> bool:
        metric_delta, before, after = build(value)
        return _fires(code, metric_delta, before, after)

    f_lo, f_hi = fires(lo), fires(hi)
    if f_lo == f_hi:
        return None
    for _ in range(_BISECT_ITERATIONS):
        mid = (lo + hi) / 2
        if fires(mid) == f_lo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _match(observed: float | None, declared: float) -> bool:
    if observed is None:
        return False
    return abs(observed - declared) <= max(abs(declared) * _MATCH_TOLERANCE, 1e-9)


def _sweep_rule(code: str, spec: dict) -> dict:
    """Sweep one rule; returns its sensitivity record."""
    build = spec["build"]
    entry: dict = {
        "rule": code,
        "metric": UNIVERSAL_THRESHOLDS[code]["metric"],
        "probe": spec["probe"],
    }
    flips: list[dict] = []
    all_match = True
    if "probes" in spec:
        # Discrete/definitional rules: probe declared integer boundaries.
        smallest_firing = None
        for value, expected in spec["probes"]:
            metric_delta, before, after = build(value)
            fired = _fires(code, metric_delta, before, after)
            if fired != expected:
                all_match = False
            if fired and smallest_firing is None:
                smallest_firing = value
        entry["declared_flip"] = spec["declared_flip"]
        entry["observed_flip"] = smallest_firing
        entry["match"] = all_match
        entry["method"] = "discrete_probes"
        return entry
    for segment in spec["segments"]:
        observed = _bisect_flip(code, build, segment["lo"], segment["hi"])
        ok = _match(observed, segment["declared_flip"])
        all_match = all_match and ok
        flips.append({
            "bracket": [segment["lo"], segment["hi"]],
            "declared_flip": segment["declared_flip"],
            "observed_flip": None if observed is None else round(observed, 12),
            "match": ok,
        })
    entry["segments"] = flips
    entry["match"] = all_match
    entry["method"] = "bisection"
    return entry


# Sweep table. Each builder constructs (metric_delta, before, after) so that
# only the target rule's driving quantity moves; other rules stay neutral or
# are ignored because detection is code-scoped.
def _sweep_table() -> dict[str, dict]:
    tp_margin = UNIVERSAL_THRESHOLDS["true_peak_margin_reduced"]["min_margin_db"]
    return {
        # after true peak crosses the early-warning margin while margin shrinks
        "true_peak_margin_reduced": {
            "probe": "after_true_peak_dbfs (before=-0.1, delta<0)",
            "build": lambda v: (
                _delta(true_peak_dbfs=v + 0.1),
                _metrics(true_peak_dbfs=-0.1),
                _metrics(true_peak_dbfs=v),
            ),
            "segments": [
                {"lo": -2.0 * tp_margin - 0.4, "hi": -0.2,
                 "declared_flip": -tp_margin},
            ],
        },
        "excessive_loudness_increase": {
            "probe": "integrated_lufs delta (before=-14)",
            "build": lambda v: (
                _delta(integrated_lufs=v),
                _metrics(integrated_lufs=-14.0),
                _metrics(integrated_lufs=-14.0 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 2.0 * UNIVERSAL_THRESHOLDS["excessive_loudness_increase"]["max_increase_db"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["excessive_loudness_increase"]["max_increase_db"]},
            ],
        },
        "excessive_dynamic_compression": {
            "probe": "crest_factor_db delta (before=10)",
            "build": lambda v: (
                _delta(crest_factor_db=v),
                _metrics(crest_factor_db=10.0),
                _metrics(crest_factor_db=10.0 + v),
            ),
            "segments": [
                {"lo": -2.0 * UNIVERSAL_THRESHOLDS["excessive_dynamic_compression"]["max_reduction_db"], "hi": -0.5,
                 "declared_flip": -UNIVERSAL_THRESHOLDS["excessive_dynamic_compression"]["max_reduction_db"]},
            ],
        },
        "crest_factor_collapse": {
            "probe": "after crest_factor_db (before=10)",
            "build": lambda v: (
                _delta(crest_factor_db=v - 10.0),
                _metrics(crest_factor_db=10.0),
                _metrics(crest_factor_db=v),
            ),
            "segments": [
                {"lo": 0.5, "hi": 2.0 * UNIVERSAL_THRESHOLDS["crest_factor_collapse"]["min_crest_db"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["crest_factor_collapse"]["min_crest_db"]},
            ],
        },
        "new_clipping": {
            "probe": "after clipping_sample_count (before=0)",
            "build": lambda v: (
                _delta(clipping_sample_count=float(v)),
                _metrics(clipping_sample_count=0),
                _metrics(clipping_sample_count=v),
            ),
            "probes": [(0, False), (1, True), (5, True)],
            "declared_flip": "> max_count (0) → first firing value 1",
        },
        "low_frequency_overaccumulation": {
            "probe": "bass_60_120_hz delta (before=0.10)",
            "build": lambda v: (
                _delta(bass_60_120_hz=v),
                _metrics(bass_60_120_hz=0.10),
                _metrics(bass_60_120_hz=0.10 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 2.0 * UNIVERSAL_THRESHOLDS["low_frequency_overaccumulation"]["max_increase_ratio"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["low_frequency_overaccumulation"]["max_increase_ratio"]},
            ],
        },
        "high_frequency_overaccumulation": {
            "probe": "brilliance_5000_10000_hz delta (before=0.08)",
            "build": lambda v: (
                _delta(brilliance_5000_10000_hz=v),
                _metrics(brilliance_5000_10000_hz=0.08),
                _metrics(brilliance_5000_10000_hz=0.08 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 2.0 * UNIVERSAL_THRESHOLDS["high_frequency_overaccumulation"]["max_increase_ratio"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["high_frequency_overaccumulation"]["max_increase_ratio"]},
            ],
        },
        "new_high_frequency_cutoff": {
            "probe": "estimated_high_frequency_cutoff_hz delta (before=15000)",
            "build": lambda v: (
                _delta(estimated_high_frequency_cutoff_hz=v),
                _metrics(estimated_high_frequency_cutoff_hz=15000.0),
                _metrics(estimated_high_frequency_cutoff_hz=15000.0 + v),
            ),
            "segments": [
                {"lo": -2.0 * UNIVERSAL_THRESHOLDS["new_high_frequency_cutoff"]["max_reduction_hz"], "hi": -100.0,
                 "declared_flip": -UNIVERSAL_THRESHOLDS["new_high_frequency_cutoff"]["max_reduction_hz"]},
            ],
        },
        "stereo_phase_risk_increased": {
            "probe": "phase_risk_ratio delta (before=0.05)",
            "build": lambda v: (
                _delta(phase_risk_ratio=v),
                _metrics(phase_risk_ratio=0.05),
                _metrics(phase_risk_ratio=0.05 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 2.0 * UNIVERSAL_THRESHOLDS["stereo_phase_risk_increased"]["max_increase"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["stereo_phase_risk_increased"]["max_increase"]},
            ],
        },
        "negative_correlation_increased": {
            "probe": "negative_correlation_ratio delta (before=0.02)",
            "build": lambda v: (
                _delta(negative_correlation_ratio=v),
                _metrics(negative_correlation_ratio=0.02),
                _metrics(negative_correlation_ratio=0.02 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 2.0 * UNIVERSAL_THRESHOLDS["negative_correlation_increased"]["max_increase"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["negative_correlation_increased"]["max_increase"]},
            ],
        },
        "duration_changed": {
            "probe": "duration delta (before=180); symmetric |delta| rule",
            "build": lambda v: (
                _delta(duration=v),
                _metrics(duration=180.0),
                _metrics(duration=180.0 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 4.0 * UNIVERSAL_THRESHOLDS["duration_changed"]["max_abs_delta_s"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["duration_changed"]["max_abs_delta_s"]},
                {"lo": -4.0 * UNIVERSAL_THRESHOLDS["duration_changed"]["max_abs_delta_s"], "hi": 0.0,
                 "declared_flip": -UNIVERSAL_THRESHOLDS["duration_changed"]["max_abs_delta_s"]},
            ],
        },
        "channel_layout_changed": {
            "probe": "channels delta (before=2)",
            "build": lambda v: (
                _delta(channels=v),
                _metrics(channels=2),
                _metrics(channels=2 + v),
            ),
            "probes": [(0, False), (1, True), (-1, True)],
            "declared_flip": "!= 0 → first firing value 1",
        },
        "sample_rate_changed": {
            "probe": "sample_rate delta (before=44100)",
            "build": lambda v: (
                _delta(sample_rate=v),
                _metrics(sample_rate=44100),
                _metrics(sample_rate=44100 + v),
            ),
            "probes": [(0, False), (1, True), (3900, True)],
            "declared_flip": "!= 0 → first firing value 1",
        },
        "silence_structure_changed": {
            "probe": "silence_ratio delta (before=0.10); symmetric |delta| rule",
            "build": lambda v: (
                _delta(silence_ratio=v),
                _metrics(silence_ratio=0.10),
                _metrics(silence_ratio=0.10 + v),
            ),
            "segments": [
                {"lo": 0.0, "hi": 4.0 * UNIVERSAL_THRESHOLDS["silence_structure_changed"]["max_abs_delta"],
                 "declared_flip": UNIVERSAL_THRESHOLDS["silence_structure_changed"]["max_abs_delta"]},
                {"lo": -4.0 * UNIVERSAL_THRESHOLDS["silence_structure_changed"]["max_abs_delta"], "hi": 0.0,
                 "declared_flip": -UNIVERSAL_THRESHOLDS["silence_structure_changed"]["max_abs_delta"]},
            ],
        },
        "invalid_audio_samples": {
            "probe": "after invalid_sample_count (before=0)",
            "build": lambda v: (
                _delta(invalid_sample_count=float(v)),
                _metrics(invalid_sample_count=0),
                _metrics(invalid_sample_count=v),
            ),
            "probes": [(0, False), (1, True)],
            "declared_flip": "> max_count (0) → first firing value 1",
        },
        "analysis_confidence_low": {
            "probe": "after finite_sample_ratio",
            "build": lambda v: (
                {},
                _metrics(finite_sample_ratio=1.0),
                _metrics(finite_sample_ratio=v),
            ),
            "segments": [
                {"lo": 0.9, "hi": 1.0,
                 "declared_flip": UNIVERSAL_THRESHOLDS["analysis_confidence_low"]["min_ratio"]},
            ],
        },
    }


# --- Lab calibration bridge -------------------------------------------------
# Rule -> auditory.lab perturbation ladders able to produce stimuli crossing
# the declared threshold. Reachability only; no threshold value is derived
# from these ladders yet. ``comparable=False`` means ladder parameter and
# threshold live in different units, so reachability would need a run, not an
# arithmetic comparison.

def _lab_calibration_bridge() -> dict:
    from moodify.auditory.lab.perturbations import LADDERS

    def ladder_of(operator: str) -> list[dict]:
        return LADDERS.get(operator, [])

    return {
        "purpose": "可达性映射：记录哪些 lab 阶梯能产生越过阈值的刺激；"
                   "由阶梯运行推导校准值是 lab 校准线的后续工作，本层不声称。",
        "rules": {
            "new_clipping": {"operator": "HARD_CLIP", "ladder": ladder_of("HARD_CLIP"),
                             "comparable": True,
                             "note": "阶梯满幅削波必然越过 max_count=0（定义性规则，无需校准）"},
            "true_peak_margin_reduced": {"operator": "NEAR_CLIP", "ladder": ladder_of("NEAR_CLIP"),
                                          "comparable": False,
                                          "note": "阶梯参数是削波阈值，与真峰余量阈值不同单位"},
            "excessive_loudness_increase": {"operator": "GAIN_STEP", "param": "gain_db",
                                             "ladder": ladder_of("GAIN_STEP"),
                                             "comparable": True,
                                             "note": "阶梯 gain_db (8/12 dB) 越过 max_increase_db=4.0："
                                                     "lab 可产生跨阈值刺激"},
            "excessive_dynamic_compression": {"operator": "DYNAMIC_COMPRESSION", "param": "ratio",
                                               "ladder": ladder_of("DYNAMIC_COMPRESSION"),
                                               "comparable": False,
                                               "note": "压缩比与 crest 降幅不同单位，可达性需运行推导"},
            "crest_factor_collapse": {"operator": "DYNAMIC_COMPRESSION", "param": "ratio",
                                       "ladder": ladder_of("DYNAMIC_COMPRESSION"),
                                       "comparable": False, "note": "同上"},
            "new_high_frequency_cutoff": {"operator": "LOWPASS", "param": "cutoff_hz",
                                           "ladder": ladder_of("LOWPASS"),
                                           "comparable": False,
                                           "note": "截止频率与截止降幅 delta 不同单位"},
            "stereo_phase_risk_increased": {"operator": "ANTIPHASE_REGION", "ladder": ladder_of("ANTIPHASE_REGION"),
                                             "comparable": False, "note": "区域长度与相位风险比值不同单位"},
            "negative_correlation_increased": {"operator": "ANTIPHASE_REGION",
                                                "ladder": ladder_of("ANTIPHASE_REGION"),
                                                "comparable": False, "note": "同上"},
            "silence_structure_changed": {"operator": "SILENCE_INSERT", "param": "duration_ms",
                                           "ladder": ladder_of("SILENCE_INSERT"),
                                           "comparable": False,
                                           "note": "插入时长与 silence_ratio delta 不同单位"},
            "duration_changed": {"operator": "SILENCE_INSERT", "param": "duration_ms",
                                  "ladder": ladder_of("SILENCE_INSERT"),
                                  "comparable": True,
                                  "note": "插入时长（300/600/1000 ms）越过 ±50 ms 容差"},
            "low_frequency_overaccumulation": {"operator": None, "comparable": False,
                                                "note": "lab 尚无针对低频能量堆积的算子"},
            "high_frequency_overaccumulation": {"operator": None, "comparable": False,
                                                 "note": "lab 尚无针对高频能量堆积的算子"},
            "analysis_confidence_low": {"operator": None, "comparable": False,
                                         "note": "lab 尚无对应算子；测量健康门"
                                                 "不是刺激属性"},
            "channel_layout_changed": {"operator": None, "comparable": False,
                                        "note": "定义性不变量，不适用校准"},
            "sample_rate_changed": {"operator": None, "comparable": False,
                                     "note": "定义性不变量，不适用校准"},
            "invalid_audio_samples": {"operator": None, "comparable": False,
                                       "note": "定义性不变量，不适用校准"},
        },
    }


def build_sensitivity_report() -> dict:
    """Sweep every rule through the production judgment path."""
    table = _sweep_table()
    missing = sorted(set(UNIVERSAL_THRESHOLDS) - set(table))
    extra = sorted(set(table) - set(UNIVERSAL_THRESHOLDS))
    if missing or extra:
        raise RuntimeError(
            f"sweep table out of sync with UNIVERSAL_THRESHOLDS: missing={missing} extra={extra}"
        )
    rules = [_sweep_rule(code, table[code]) for code in UNIVERSAL_THRESHOLDS]
    verified = sum(1 for entry in rules if entry["match"])
    return {
        "sensitivity_version": SENSITIVITY_VERSION,
        "judgment_rules_version": JUDGMENT_RULES_VERSION,
        "code_under_test": "moodify.auditory.judgment.evaluate_risk_flags",
        "method": "翻转点扫描：对每条规则沿其驱动量做单调段二分（或离散探测），"
                  "观测裁决翻转点并与声明阈值比对；无音频、无 DSP。",
        "rules": rules,
        "lab_calibration_bridge": _lab_calibration_bridge(),
        "summary": {
            "rules_total": len(rules),
            "flip_points_verified": verified,
            "all_match": verified == len(rules),
        },
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    report = build_sensitivity_report()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if argv:
        Path(argv[0]).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
