"""Conservative technical judgment (DSK-MFY-AUDITORY-SCAN-001).

Moodify never grants artistic approval; it only decides whether a
candidate passes to human listening. Rules are versioned and recorded.
"""

from __future__ import annotations

import json
from pathlib import Path

from moodify.auditory.models import Judgment, RiskFlag

JUDGMENT_RULES_VERSION = "1.0"

# Universal technical risk thresholds (configurable + versioned)
UNIVERSAL_THRESHOLDS = {
    "true_peak_margin_reduced": {"metric": "true_peak_dbfs", "min_margin_db": 0.5},
    "excessive_loudness_increase": {"metric": "integrated_lufs", "max_increase_db": 4.0},
    "excessive_dynamic_compression": {"metric": "crest_factor_db", "max_reduction_db": 4.0},
    "crest_factor_collapse": {"metric": "crest_factor_db", "min_crest_db": 4.0},
    "new_clipping": {"metric": "clipping_sample_count", "max_count": 0},
    "low_frequency_overaccumulation": {"metric": "bass_60_120_hz", "max_increase_ratio": 0.03},
    "high_frequency_overaccumulation": {"metric": "brilliance_5000_10000_hz", "max_increase_ratio": 0.05},
    "new_high_frequency_cutoff": {"metric": "estimated_high_frequency_cutoff_hz", "max_reduction_hz": 3000.0},
    "stereo_phase_risk_increased": {"metric": "phase_risk_ratio", "max_increase": 0.02},
    "negative_correlation_increased": {"metric": "negative_correlation_ratio", "max_increase": 0.02},
    "duration_changed": {"metric": "duration", "max_abs_delta_s": 0.050},
    "channel_layout_changed": {"metric": "channels", "max_delta": 0},
    "sample_rate_changed": {"metric": "sample_rate", "max_delta": 0},
    "silence_structure_changed": {"metric": "silence_ratio", "max_abs_delta": 0.05},
    "invalid_audio_samples": {"metric": "invalid_sample_count", "max_count": 0},
    "analysis_confidence_low": {"metric": "finite_sample_ratio", "min_ratio": 0.999},
}


def evaluate_risk_flags(metric_delta: dict, before_metrics: dict, after_metrics: dict) -> list[RiskFlag]:
    flags: list[RiskFlag] = []

    def val(metrics: dict, key: str):
        entry = metrics.get(key)
        return entry.get("value") if isinstance(entry, dict) else None

    def delta(key: str):
        d = metric_delta.get(key)
        return d.get("absolute_delta") if d else None

    t = UNIVERSAL_THRESHOLDS

    clip_after = val(after_metrics, "clipping_sample_count")
    clip_before = val(before_metrics, "clipping_sample_count")
    if clip_after is not None and clip_before is not None:
        if clip_after > t["new_clipping"]["max_count"] and clip_after > clip_before:
            flags.append(RiskFlag("NEW_CLIPPING", "BLOCKING", "candidate introduces new clipping",
                                  "clipping_sample_count", clip_before, clip_after))
        elif clip_after > t["new_clipping"]["max_count"] and clip_after == clip_before:
            flags.append(RiskFlag("NEW_CLIPPING", "WARNING", "clipping persists",
                                  "clipping_sample_count", clip_before, clip_after))

    tp_d = delta("true_peak_dbfs")
    tp_a = val(after_metrics, "true_peak_dbfs")
    if tp_d is not None and tp_a is not None and tp_a > -0.5 and tp_d < 0:
        flags.append(RiskFlag("TRUE_PEAK_MARGIN_REDUCED", "WARNING",
                              "true peak margin reduced toward 0 dBFS",
                              "true_peak_dbfs", val(before_metrics, "true_peak_dbfs"), tp_a))

    lufs_d = delta("integrated_lufs")
    if lufs_d is not None and lufs_d > t["excessive_loudness_increase"]["max_increase_db"]:
        flags.append(RiskFlag("EXCESSIVE_LOUDNESS_INCREASE", "WARNING",
                              "integrated loudness increased beyond threshold",
                              "integrated_lufs", val(before_metrics, "integrated_lufs"),
                              val(after_metrics, "integrated_lufs")))

    crest_d = delta("crest_factor_db")
    crest_a = val(after_metrics, "crest_factor_db")
    if crest_d is not None and crest_d < -t["excessive_dynamic_compression"]["max_reduction_db"]:
        flags.append(RiskFlag("EXCESSIVE_DYNAMIC_COMPRESSION", "WARNING",
                              "crest factor reduced beyond threshold",
                              "crest_factor_db", val(before_metrics, "crest_factor_db"), crest_a))
    if crest_a is not None and crest_a < t["crest_factor_collapse"]["min_crest_db"]:
        flags.append(RiskFlag("CREST_FACTOR_COLLAPSE", "WARNING",
                              "crest factor collapsed", "crest_factor_db", None, crest_a))

    for code, spec in [
        ("LOW_FREQUENCY_OVERACCUMULATION", "bass_60_120_hz"),
        ("HIGH_FREQUENCY_OVERACCUMULATION", "brilliance_5000_10000_hz"),
    ]:
        d = delta(spec)
        if d is not None and d > UNIVERSAL_THRESHOLDS[code.lower()]["max_increase_ratio"]:
            flags.append(RiskFlag(code, "WARNING", f"{spec} ratio increased",
                                  spec, val(before_metrics, spec), val(after_metrics, spec)))

    cutoff_d = delta("estimated_high_frequency_cutoff_hz")
    if cutoff_d is not None and cutoff_d < -t["new_high_frequency_cutoff"]["max_reduction_hz"]:
        flags.append(RiskFlag("NEW_HIGH_FREQUENCY_CUTOFF", "WARNING",
                              "high-frequency cutoff dropped", "estimated_high_frequency_cutoff_hz",
                              val(before_metrics, "estimated_high_frequency_cutoff_hz"),
                              val(after_metrics, "estimated_high_frequency_cutoff_hz")))

    phase_d = delta("phase_risk_ratio")
    if phase_d is not None and phase_d > t["stereo_phase_risk_increased"]["max_increase"]:
        flags.append(RiskFlag("STEREO_PHASE_RISK_INCREASED", "BLOCKING",
                              "stereo phase risk increased", "phase_risk_ratio",
                              val(before_metrics, "phase_risk_ratio"), val(after_metrics, "phase_risk_ratio")))

    neg_d = delta("negative_correlation_ratio")
    if neg_d is not None and neg_d > t["negative_correlation_increased"]["max_increase"]:
        flags.append(RiskFlag("NEGATIVE_CORRELATION_INCREASED", "WARNING",
                              "negative correlation increased", "negative_correlation_ratio",
                              val(before_metrics, "negative_correlation_ratio"),
                              val(after_metrics, "negative_correlation_ratio")))

    silence_d = delta("silence_ratio")
    if silence_d is not None and abs(silence_d) > t["silence_structure_changed"]["max_abs_delta"]:
        flags.append(RiskFlag("SILENCE_STRUCTURE_CHANGED", "INFO",
                              "silence structure changed", "silence_ratio",
                              val(before_metrics, "silence_ratio"), val(after_metrics, "silence_ratio")))

    invalid_a = val(after_metrics, "invalid_sample_count")
    if invalid_a is not None and invalid_a > 0:
        flags.append(RiskFlag("INVALID_AUDIO_SAMPLES", "BLOCKING",
                              "candidate contains invalid samples", "invalid_sample_count", None, invalid_a))

    finite_a = val(after_metrics, "finite_sample_ratio")
    if finite_a is not None and finite_a < t["analysis_confidence_low"]["min_ratio"]:
        flags.append(RiskFlag("ANALYSIS_CONFIDENCE_LOW", "WARNING",
                              "analysis confidence low", "finite_sample_ratio", None, finite_a))

    return [_enrich_risk_flag(f) for f in flags]


# 判断契约 (05_JUDGMENT_CONTRACT) 字段补全：classification 映射与证据引用
_CLASSIFICATION_BY_CODE = {
    "SILENCE_STRUCTURE_CHANGED": "INFORMATIONAL",
    "ANALYSIS_CONFIDENCE_LOW": "INSUFFICIENT_EVIDENCE",
    "NEW_CLIPPING": "TECHNICAL_RISK",
    "INVALID_AUDIO_SAMPLES": "TECHNICAL_RISK",
    "TRUE_PEAK_MARGIN_REDUCED": "TECHNICAL_RISK",
    "EXCESSIVE_LOUDNESS_INCREASE": "TECHNICAL_RISK",
    "EXCESSIVE_DYNAMIC_COMPRESSION": "TECHNICAL_RISK",
    "CREST_FACTOR_COLLAPSE": "TECHNICAL_RISK",
    "LOW_FREQUENCY_OVERACCUMULATION": "LIKELY_ARTIFACT",
    "HIGH_FREQUENCY_OVERACCUMULATION": "LIKELY_ARTIFACT",
    "NEW_HIGH_FREQUENCY_CUTOFF": "LIKELY_ARTIFACT",
    "STEREO_PHASE_RISK_INCREASED": "TECHNICAL_RISK",
    "NEGATIVE_CORRELATION_INCREASED": "TECHNICAL_RISK",
}

_UNIT_BY_METRIC = {
    "integrated_lufs": "LUFS",
    "true_peak_dbfs": "dBTP",
    "crest_factor_db": "dB",
    "clipping_sample_count": "count",
    "invalid_sample_count": "count",
    "estimated_high_frequency_cutoff_hz": "Hz",
    "bass_60_120_hz": "ratio",
    "brilliance_5000_10000_hz": "ratio",
    "phase_risk_ratio": "ratio",
    "negative_correlation_ratio": "ratio",
    "silence_ratio": "ratio",
    "finite_sample_ratio": "ratio",
}


def _enrich_risk_flag(flag: RiskFlag) -> RiskFlag:
    """按判断契约补全 RiskFlag 的可选字段；BLOCKING 必须有证据引用。"""
    rule_key = flag.code.lower()
    reference_basis = rule_key if rule_key in UNIVERSAL_THRESHOLDS else flag.metric
    evidence_refs = ["metrics.json", "judgment_rules.json"]
    if flag.severity == "BLOCKING" and not flag.evidence_refs:
        evidence_refs.append("scan_manifest.json")
    return RiskFlag(
        code=flag.code,
        severity=flag.severity,
        message=flag.message,
        metric=flag.metric,
        before=flag.before,
        after=flag.after,
        threshold=flag.threshold,
        label=flag.message,
        observed_value=flag.after if flag.after is not None else flag.before,
        unit=_UNIT_BY_METRIC.get(flag.metric or "", None),
        reference_basis=reference_basis,
        confidence=0.9 if flag.severity != "INFO" else 0.5,
        classification=_CLASSIFICATION_BY_CODE.get(flag.code, "UNCERTAIN"),
        rule_or_model_version=f"judgment-rules-v{JUDGMENT_RULES_VERSION}",
        evidence_refs=evidence_refs,
    )


def evaluate_processing_plan(plan: dict, metric_delta: dict, before_metrics: dict, after_metrics: dict) -> tuple[list[str], list[str]]:
    """Return (goals_met, guardrail_failures) for a validated plan."""
    goals_met: list[str] = []
    guardrail_failures: list[str] = []
    goals = plan.get("technical_goals", [])
    guardrails = plan.get("guardrails", [])

    for goal in goals:
        gid = goal.get("goal_id")
        metric = goal.get("metric")
        direction = goal.get("desired_direction")
        min_change = goal.get("minimum_meaningful_change", 0.0)
        d = metric_delta.get(metric)
        if not d:
            continue
        delta_val = d.get("absolute_delta")
        if delta_val is None:
            continue
        if direction == "DECREASE" and delta_val <= -min_change:
            goals_met.append(gid)
        elif direction == "INCREASE" and delta_val >= min_change:
            goals_met.append(gid)

    for gr in guardrails:
        gid = gr.get("guardrail_id")
        metric = gr.get("metric")
        comparator = gr.get("comparator")
        threshold = gr.get("threshold")
        severity = gr.get("severity", "WARNING")
        d = metric_delta.get(metric)
        if not d:
            continue
        delta_val = d.get("absolute_delta")
        before_v = d.get("before")
        if delta_val is None:
            continue
        failed = False
        if comparator == "EQUAL" and delta_val != threshold:
            failed = True
        elif comparator == "BASELINE_DELTA_LE" and delta_val > threshold:
            failed = True
        elif comparator == "BASELINE_DELTA_GE" and delta_val < threshold:
            failed = True
        elif comparator == "VALUE_LE" and before_v is not None and d.get("after", before_v) > threshold:
            failed = True
        if failed and severity == "BLOCKING":
            guardrail_failures.append(gid)
    return goals_met, guardrail_failures


def judge(
    metric_delta: dict,
    before_metrics: dict,
    after_metrics: dict,
    plan: dict | None,
    risk_flags: list[RiskFlag],
) -> Judgment:
    blocking = [f for f in risk_flags if f.severity == "BLOCKING"]
    if blocking:
        return Judgment(
            technical_assessment="DEGRADED",
            workflow_decision="REJECT_TECHNICAL",
            reasons=[f"blocking guardrail: {f.code}" for f in blocking],
            guardrail_failures=[f.code for f in blocking],
            risk_flags=risk_flags,
        )

    if plan is None:
        # describe changes only; never claim intended improvement
        return Judgment(
            technical_assessment="UNCERTAIN",
            workflow_decision="INCONCLUSIVE",
            reasons=["no processing plan; changes described but goals not demonstrated"],
            risk_flags=risk_flags,
        )

    goals_met, guardrail_failures = evaluate_processing_plan(plan, metric_delta, before_metrics, after_metrics)

    if guardrail_failures:
        return Judgment(
            technical_assessment="DEGRADED",
            workflow_decision="REJECT_TECHNICAL",
            reasons=[f"guardrail failed: {g}" for g in guardrail_failures],
            guardrail_failures=guardrail_failures,
            risk_flags=risk_flags,
        )

    if goals_met:
        return Judgment(
            technical_assessment="IMPROVED",
            workflow_decision="PASS_TO_LISTENING",
            reasons=[f"goal met: {g}" for g in goals_met],
            goals_met=goals_met,
            risk_flags=risk_flags,
        )

    return Judgment(
        technical_assessment="NEUTRAL",
        workflow_decision="INCONCLUSIVE",
        reasons=["measurable changes but no approved technical goal demonstrated"],
        risk_flags=risk_flags,
    )


def write_judgment_rules(path: Path) -> None:
    path.write_text(json.dumps({
        "judgment_rules_version": JUDGMENT_RULES_VERSION,
        "universal_thresholds": UNIVERSAL_THRESHOLDS,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
