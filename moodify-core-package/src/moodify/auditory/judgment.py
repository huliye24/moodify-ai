"""Conservative technical judgment (DSK-MFY-AUDITORY-SCAN-001).

Moodify never grants artistic approval; it only decides whether a
candidate passes to human listening. Rules are versioned and recorded.

Since judgment-rules-v1.1 every threshold also carries provenance
(``THRESHOLD_PROVENANCE``): where its value came from, when it was fixed,
and whether calibration evidence exists. Provenance-only discipline: this
layer records trust level, it never recalibrates a value.
"""

from __future__ import annotations

import json
from pathlib import Path

from moodify.auditory.models import Judgment, RiskFlag

JUDGMENT_RULES_VERSION = "1.1"

# Universal technical risk thresholds (configurable + versioned).
# Values are frozen since their introduction (5452ff44, 2026-08-02, AS-001);
# v1.1 adds provenance metadata only. Any value change is a recalibration and
# requires its own human-decision record and experiment evidence.
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

# --- Threshold provenance (Layer C: 来源化与校准) ---------------------------
# Every threshold declares where its value came from, when it was fixed, and
# whether calibration evidence exists. Source classes:
#
#   STANDARD      — value traceable to a named published standard
#   EXPERIMENTAL  — value derived from a repo lab experiment (auditory.lab /
#                   physics sensitivity line); the graduation target
#   DEFAULT       — engineering default chosen in-repo, no calibration yet
#
# Calibration statuses: CALIBRATED, DEFAULT_UNCALIBRATED. Status 2026-10-02:
# 0 STANDARD / 0 EXPERIMENTAL / 16 DEFAULT — the table is byte-identical
# since its introduction, and no threshold has been through the lab
# calibration line yet. This honesty is the point: uncalibrated limits are
# published as such instead of borrowing credibility from the BS.1770
# measurement layer underneath them.

CALIBRATION_STANDARD = "STANDARD"
CALIBRATION_EXPERIMENTAL = "EXPERIMENTAL"
CALIBRATION_DEFAULT = "DEFAULT"
STATUS_CALIBRATED = "CALIBRATED"
STATUS_DEFAULT_UNCALIBRATED = "DEFAULT_UNCALIBRATED"
THRESHOLD_PROVENANCE_VERSION = "threshold-provenance-v1"
# 5452ff44 (2026-08-02, AS-001) introduced the table; all later commits carry
# the identical value set (verified 2026-10-02 over the full commit history).
_PROVENANCE_DATE = "2026-08-02"
_PROVENANCE_COMMIT = "5452ff44"

THRESHOLD_PROVENANCE: dict[str, dict] = {
    "true_peak_margin_reduced": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering margin on the ITU-R BS.1770 true-peak "
                  "measurement; delivery practice (EBU R128 / streaming "
                  "-1 dBTP ceilings) informs the direction, but the 0.5 dB "
                  "early-warning margin was chosen in-repo.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "excessive_loudness_increase": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default. LUFS measurement is ITU-R BS.1770; "
                  "the 4 LU relative-increase risk level comes from neither "
                  "a standard nor a repo experiment.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "excessive_dynamic_compression": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default on crest-factor dynamics; the 4 dB "
                  "reduction level is not calibrated against listening "
                  "evidence. Lab DYNAMIC_COMPRESSION ladders exist but no "
                  "derivation has been performed.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "crest_factor_collapse": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default absolute crest floor; no standard "
                  "defines a crest floor and no experiment derived 4 dB.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "new_clipping": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": False,
        "source": "Definitional invariant: any new full-scale sample is "
                  "flagged. The value is fixed by definition; calibration "
                  "is not applicable.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "low_frequency_overaccumulation": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default for low-band energy-ratio growth; no "
                  "calibration experiment performed.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "high_frequency_overaccumulation": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default for high-band energy-ratio growth; no "
                  "calibration experiment performed.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "new_high_frequency_cutoff": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default for cutoff reduction; lab LOWPASS "
                  "ladders can produce crossing stimuli but no derivation "
                  "has been performed.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "stereo_phase_risk_increased": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default; the phase-risk metric is repo-defined "
                  "(no external standard), threshold not calibrated.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "negative_correlation_increased": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default; negative-correlation ratio is a "
                  "repo-defined proxy, threshold not calibrated.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "duration_changed": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering tolerance; mirrors DURATION_TOLERANCE_S in "
                  "auditory/comparison.py (AS-001 rescan consistency), not "
                  "derived from a standard.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "channel_layout_changed": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": False,
        "source": "Definitional invariant: channel identity must be "
                  "preserved. Calibration is not applicable.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "sample_rate_changed": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": False,
        "source": "Definitional invariant: sample rate must be preserved. "
                  "Calibration is not applicable.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "silence_structure_changed": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default for silence-ratio change; lab "
                  "SILENCE_INSERT ladders exist but no derivation has been "
                  "performed.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "invalid_audio_samples": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": False,
        "source": "Definitional invariant: non-finite (NaN/Inf) audio "
                  "samples are defects. Calibration is not applicable.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
    "analysis_confidence_low": {
        "source_class": CALIBRATION_DEFAULT,
        "calibration_status": STATUS_DEFAULT_UNCALIBRATED,
        "calibratable": True,
        "source": "Engineering default measurement-health gate; the 0.999 "
                  "finite-sample floor was chosen in-repo.",
        "date": _PROVENANCE_DATE, "introduced_in": _PROVENANCE_COMMIT,
    },
}


def calibration_summary() -> dict:
    """Machine-readable trust summary over ``THRESHOLD_PROVENANCE``."""
    by_class = {
        CALIBRATION_STANDARD: 0,
        CALIBRATION_EXPERIMENTAL: 0,
        CALIBRATION_DEFAULT: 0,
    }
    uncalibrated: list[str] = []
    for key, prov in THRESHOLD_PROVENANCE.items():
        by_class[prov["source_class"]] += 1
        if prov["calibration_status"] == STATUS_DEFAULT_UNCALIBRATED:
            uncalibrated.append(key)
    calibrated = sum(
        1 for p in THRESHOLD_PROVENANCE.values()
        if p["calibration_status"] == STATUS_CALIBRATED
    )
    return {
        "registry_version": THRESHOLD_PROVENANCE_VERSION,
        "rules_total": len(THRESHOLD_PROVENANCE),
        "calibrated": calibrated,
        "default_uncalibrated": len(uncalibrated),
        "by_source_class": by_class,
        "uncalibrated_rules": uncalibrated,
        "note": "阈值来源化（Layer C）只记录信任级别，不重校准数值；"
                "DEFAULT_UNCALIBRATED 的阈值是工程默认值，"
                "不得当作经过听感校准的限值消费。",
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
    tp_margin = t["true_peak_margin_reduced"]["min_margin_db"]
    if tp_d is not None and tp_a is not None and tp_a > -tp_margin and tp_d < 0:
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

    duration_d = delta("duration")
    if duration_d is not None and abs(duration_d) > t["duration_changed"]["max_abs_delta_s"]:
        flags.append(RiskFlag("DURATION_CHANGED", "BLOCKING",
                              "candidate duration changed beyond tolerance", "duration",
                              val(before_metrics, "duration"), val(after_metrics, "duration")))

    channels_d = delta("channels")
    if channels_d is not None and abs(channels_d) > t["channel_layout_changed"]["max_delta"]:
        flags.append(RiskFlag("CHANNEL_LAYOUT_CHANGED", "BLOCKING",
                              "candidate channel layout changed", "channels",
                              val(before_metrics, "channels"), val(after_metrics, "channels")))

    sample_rate_d = delta("sample_rate")
    if sample_rate_d is not None and sample_rate_d != 0:
        flags.append(RiskFlag("SAMPLE_RATE_CHANGED", "BLOCKING",
                              "candidate sample rate changed", "sample_rate",
                              val(before_metrics, "sample_rate"), val(after_metrics, "sample_rate")))

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
    "DURATION_CHANGED": "TECHNICAL_RISK",
    "CHANNEL_LAYOUT_CHANGED": "TECHNICAL_RISK",
    "SAMPLE_RATE_CHANGED": "TECHNICAL_RISK",
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
    "duration": "s",
    "channels": "count",
    "sample_rate": "Hz",
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
        "threshold_provenance_version": THRESHOLD_PROVENANCE_VERSION,
        "threshold_provenance": THRESHOLD_PROVENANCE,
        "calibration_summary": calibration_summary(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
