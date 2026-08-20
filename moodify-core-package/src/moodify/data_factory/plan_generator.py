"""Deterministic ABC intervention-plan generator.

V1 is intentionally heuristic. It converts current scan metrics into three
ordered intervention strengths while keeping the same technical objective.
No LLM and no learned model is used here.

Technical goals and guardrails are emitted in the live judgment-contract shape
(moodify.auditory.judgment.evaluate_processing_plan) so that the canonical
comparison path can evaluate them without a second judgment implementation.
"""

from __future__ import annotations

from copy import deepcopy

from .models import InterventionPlan, PLAN_GENERATOR_VERSION

_LABELS = (
    ("A", "CONSERVATIVE", 0.65),
    ("B", "BALANCED", 1.00),
    ("C", "EXPLORATORY", 1.45),
)

# Evaluable in the canonical judgment contract; human_listening_required is a
# workflow gate carried in the plan but not measurable by machine judgment.
# TRUE_PEAK_SAFE: the DSP chain hard-ceils samples at -1 dBFS, which bounds
# inter-sample true peak around -0.5 dBTP; 0.0 dBTP is the fail-closed boundary.
_GUARDRAILS = (
    {
        "guardrail_id": "NO_NEW_CLIPPING",
        "metric": "clipping_sample_count",
        "comparator": "EQUAL",
        "threshold": 0,
        "severity": "BLOCKING",
    },
    {
        "guardrail_id": "TRUE_PEAK_SAFE",
        "metric": "true_peak_dbfs",
        "comparator": "VALUE_LE",
        "threshold": 0.0,
        "severity": "BLOCKING",
    },
    {
        "guardrail_id": "FINITE_SAMPLES_ONLY",
        "metric": "invalid_sample_count",
        "comparator": "EQUAL",
        "threshold": 0,
        "severity": "BLOCKING",
    },
)


def _value(metrics: dict, key: str, default: float = 0.0) -> float:
    raw = metrics.get(key, default)
    if isinstance(raw, dict):
        raw = raw.get("value", default)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _base_params() -> dict[str, float]:
    # Neutral technical baseline. A/B/C modifications are computed below.
    return {
        "P01_vocal_presence_freq": 3000.0,
        "P02_vocal_presence_gain": 0.0,
        "P03_vocal_presence_q": 0.7,
        "P04_proximity_low_freq": 200.0,
        "P05_proximity_low_gain": 0.0,
        "P06_compression_ratio": 1.05,
        "P07_compression_attack": 35.0,
        "P08_compression_release": 250.0,
        "P09_compression_threshold": -10.0,
        "P10_reverb_t60": 0.0,
        "P11_reverb_dry_wet": 0.0,
        "P12_reverb_width": 1.0,
        "P13_harmonic_drive": 0.0,
        "P14_high_shelf_freq": 10000.0,
        "P15_high_shelf_gain": 0.0,
    }


def _derive_objective(metrics: dict) -> tuple[dict[str, float], list[dict], list[str], list[str]]:
    params = _base_params()
    technical_goals: list[dict] = []
    goals: list[str] = []
    rationale: list[str] = []

    presence = _value(metrics, "presence_2000_5000_hz")
    low_mid = _value(metrics, "low_mid_120_250_hz") + _value(metrics, "mid_250_500_hz")
    air = _value(metrics, "air_10000_16000_hz")
    crest = _value(metrics, "crest_factor_db", 10.0)

    # These thresholds are protocol-v1 calibration seeds, not universal truths.
    if presence < 0.090:
        params["P02_vocal_presence_gain"] = 1.6
        technical_goals.append(
            {
                "goal_id": "INCREASE_PRESENCE",
                "metric": "presence_2000_5000_hz",
                "desired_direction": "INCREASE",
                "minimum_meaningful_change": 0.01,
                "rationale": f"presence ratio {presence:.4f} below v1 seed threshold 0.090",
            }
        )
        goals.append("increase_presence")
        rationale.append(f"presence ratio {presence:.4f} below v1 seed threshold 0.090")
    else:
        params["P02_vocal_presence_gain"] = 0.6
        technical_goals.append(
            {
                "goal_id": "REFINE_PRESENCE",
                "metric": "presence_2000_5000_hz",
                "desired_direction": "INCREASE",
                "minimum_meaningful_change": 0.005,
                "rationale": f"presence ratio {presence:.4f} at/above v1 seed threshold 0.090",
            }
        )
        goals.append("preserve_or_slightly_refine_presence")

    if low_mid > 0.240:
        params["P05_proximity_low_gain"] = -1.0
        technical_goals.append(
            {
                "goal_id": "REDUCE_LOW_MID_CONGESTION",
                "metric": "low_mid_120_250_hz",
                "desired_direction": "DECREASE",
                "minimum_meaningful_change": 0.01,
                "rationale": f"combined low-mid ratio {low_mid:.4f} above v1 seed threshold 0.240",
            }
        )
        goals.append("reduce_low_mid_congestion")
        rationale.append(f"combined low-mid ratio {low_mid:.4f} above v1 seed threshold 0.240")

    if air < 0.018:
        params["P15_high_shelf_gain"] = 1.0
        technical_goals.append(
            {
                "goal_id": "RESTORE_AIR",
                "metric": "air_10000_16000_hz",
                "desired_direction": "INCREASE",
                "minimum_meaningful_change": 0.005,
                "rationale": f"air ratio {air:.4f} below v1 seed threshold 0.018",
            }
        )
        goals.append("restore_air")
        rationale.append(f"air ratio {air:.4f} below v1 seed threshold 0.018")
    else:
        params["P15_high_shelf_gain"] = 0.4
        technical_goals.append(
            {
                "goal_id": "REFINE_AIR",
                "metric": "air_10000_16000_hz",
                "desired_direction": "INCREASE",
                "minimum_meaningful_change": 0.002,
                "rationale": f"air ratio {air:.4f} at/above v1 seed threshold 0.018",
            }
        )
        goals.append("refine_air")

    if crest > 13.0:
        params["P06_compression_ratio"] = 1.25
        params["P09_compression_threshold"] = -14.0
        technical_goals.append(
            {
                "goal_id": "STABILIZE_DYNAMICS",
                "metric": "crest_factor_db",
                "desired_direction": "DECREASE",
                "minimum_meaningful_change": 0.5,
                "rationale": f"crest factor {crest:.2f} dB above v1 seed threshold 13 dB",
            }
        )
        goals.append("stabilize_dynamics")
        rationale.append(f"crest factor {crest:.2f} dB above v1 seed threshold 13 dB")
    else:
        params["P06_compression_ratio"] = 1.12
        params["P09_compression_threshold"] = -11.0
        technical_goals.append(
            {
                "goal_id": "PRESERVE_DYNAMICS",
                "metric": "crest_factor_db",
                "desired_direction": "DECREASE",
                "minimum_meaningful_change": 0.2,
                "rationale": f"crest factor {crest:.2f} dB at/below v1 seed threshold 13 dB",
            }
        )
        goals.append("preserve_dynamics")

    return params, technical_goals, goals, rationale


def _scale_params(base: dict[str, float], intensity: float) -> dict[str, float]:
    p = deepcopy(base)

    # Only strength-like parameters are scaled. Frequencies/timing remain stable so
    # A/B/C form an interpretable intervention-response curve.
    p["P02_vocal_presence_gain"] *= intensity
    p["P05_proximity_low_gain"] *= intensity
    p["P15_high_shelf_gain"] *= intensity

    # Compression progresses gently with intensity instead of multiplying ratio.
    ratio_excess = max(0.0, p["P06_compression_ratio"] - 1.0)
    p["P06_compression_ratio"] = 1.0 + ratio_excess * intensity
    threshold_shift = p["P09_compression_threshold"] + 10.0
    p["P09_compression_threshold"] = -10.0 + threshold_shift * intensity

    return {key: round(float(value), 6) for key, value in p.items()}


def generate_abc_plans(
    *,
    case_id: str,
    source_metrics: dict,
    source_sha256: str,
    scan_profile_id: str,
    scan_profile_hash: str,
) -> list[InterventionPlan]:
    """Generate exactly A/B/C ordered intervention plans."""
    base, technical_goals, goals, rationale = _derive_objective(source_metrics)

    plans: list[InterventionPlan] = []
    for label, strategy, intensity in _LABELS:
        plans.append(
            InterventionPlan(
                case_id=case_id,
                plan_id=f"{case_id}__PLAN_{label}",
                candidate_label=label,
                candidate_id=f"{case_id}__CAND_{label}",
                strategy=strategy,
                intensity=intensity,
                source_sha256=source_sha256,
                scan_profile_id=scan_profile_id,
                scan_profile_hash=scan_profile_hash,
                plan_generator_version=PLAN_GENERATOR_VERSION,
                params=_scale_params(base, intensity),
                technical_goals=tuple(technical_goals),
                guardrails=_GUARDRAILS,
                goals=tuple(goals),
                rationale=tuple(rationale),
            )
        )

    if [p.candidate_label for p in plans] != ["A", "B", "C"]:
        raise RuntimeError("ABC plan contract violated")
    if not (plans[0].intensity < plans[1].intensity < plans[2].intensity):
        raise RuntimeError("ABC intensity ordering violated")
    return plans
