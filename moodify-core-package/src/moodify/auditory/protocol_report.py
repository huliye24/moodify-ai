"""MSP/0.2 analysis report assembly (report.json / report.md / report.html).

Builds the protocol-level analysis report from a persisted 1.0 case bundle
(``release.analyze_to_case``). Design authority:
``docs/plan/2026-10-02_MSP02_ANALYSIS_JOB_AND_DISPLAY_DESIGN.md``.

Three load-bearing choices come from POSC_011 (Judgment Beyond Metrics) and
Canon v2.1:

- every measurement carries a ``visibility`` string declaring what the metric
  can and cannot see (POSC_011: "a metric is only credible within the limits
  of the blindness that makes it possible");
- ``judgment_boundary`` records the evaluation layers explicitly, and layers
  that were never promised are written as ``NOT_PROMISED`` rather than omitted
  (the user's 2026-10-02 decision: emotion/musical judgment is out of scope);
- ``plan.status`` is always ``DRAFT_PLAN_NOT_EXECUTED`` — the report proposes
  post-processing, it never executes it (Canon invariant 9: "Generated is not
  finished").
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import ValidationError, validate as jsonschema_validate

from moodify.auditory.judgment import (
    JUDGMENT_RULES_VERSION,
    THRESHOLD_PROVENANCE,
    UNIVERSAL_THRESHOLDS,
    calibration_summary,
)

REPORT_SCHEMA_VERSION = "moodify.msp_report/0.2"

# Visibility registry (POSC_011). One entry per metric the scan can emit; a
# metric without an entry is rendered without a visibility line rather than
# with an invented one.
VISIBILITY: dict[str, str] = {
    "integrated_lufs": "能看到全曲门限后的稳态响度；看不到响度随段落的叙事分布，也不判断该响度是否适合特定平台或审美",
    "loudness_range_lu": "能看到响度分布跨度（LRA）；看不到动态处理是风格还是损伤，短于 6s 的素材不可用",
    "true_peak_dbfs": "能看到 4x 过采样重建峰值裕量；看不到后续有损编码是否引入新的intersample peak",
    "sample_peak_dbfs": "能看到采样点峰值；看不到采样点之间的真峰（对照 true_peak_dbfs）",
    "rms_dbfs": "能看到平均信号能量；看不到响度感知（K 计权见 integrated_lufs）",
    "crest_factor_db": "能看到峰均比（动态压缩的代理指标）；看不到压缩是音乐风格还是技术损伤",
    "plr_db": "能看到真峰与 RMS 的差值；与 crest_factor_db 一样不判断动态的因果",
    "clipping_sample_count": "能看到 ≥0.999 满幅样本数；看不到软削波、模拟饱和或限幅器先期损伤",
    "clipping_sample_ratio": "能看到满幅样本占比；同 clipping_sample_count 的盲区",
    "near_clipping_sample_count": "能看到 0.95–0.999 区间样本数；该数值本身不定罪（可能是正常母带余量策略）",
    "dc_offset_left": "能看到左声道直流偏置；看不到偏置来自录音链还是下游处理",
    "dc_offset_right": "能看到右声道直流偏置；看不到偏置来自录音链还是下游处理",
    "silence_ratio": "能看到 -60 dBFS 以下窗口占比；看不到留白是音乐意图还是缺陷",
    "longest_silence_seconds": "能看到最长连续静音时长；看不到该静音在曲式中的位置与功能",
    "invalid_sample_count": "能看到非有限（NaN/Inf）样本数；看不到极低电平下的数值异常",
    "finite_sample_ratio": "能看到有限样本占比（分析置信度代理）；只反映数值完整性",
    "spectral_centroid_hz": "能看到功率加权中心频率（明暗代理）；看不到音色是否正确或讨喜",
    "spectral_rolloff_85_hz": "能看到 85% 能量累积边界；不定位具体频段问题（结合频段比读取）",
    "spectral_rolloff_95_hz": "能看到 95% 能量累积边界；不定位具体频段问题（结合频段比读取）",
    "spectral_flatness": "能看到噪声性/纯音性整体倾向；看不到具体哪个频带偏离",
    "spectral_flux": "能看到平均帧间谱变化（活动度代理）；看不到节奏或瞬态的语义",
    "estimated_high_frequency_cutoff_hz": "能看到 99.5% 能量截止频率；看不到截止是母带选择还是低质量编码残留",
    "estimated_noise_floor_dbfs": "能看到 p10 帧电平（本底噪声代理）；看不到噪声类型（嘶声/嗡声/量化噪声）",
    "stereo_correlation": "能看到声道间线性相关；看不到声像的具体布局与听感宽度",
    "mid_energy_ratio": "能看到中信号能量占比；看不到单声道兼容性的听感后果",
    "side_energy_ratio": "能看到侧信号能量占比；看不到单声道兼容性的听感后果",
    "side_to_mid_db": "能看到侧/中能量差（宽度代理）；不等于听感宽度",
    "stereo_width_proxy": "能看到 1-|相关| 宽度代理；不等于听感宽度",
    "negative_correlation_ratio": "能看到负相关帧占比（相位风险代理）；看不到哪个频段/时刻在反相（查 timeline）",
    "phase_risk_ratio": "能看到低相关帧占比（相位风险代理）；看不到哪个频段/时刻在反相（查 timeline）",
    "duration": "能看到媒体时长；不判断时长变化的原因",
    "channels": "能看到声道数；不判断布局选择的意图",
    "sample_rate": "能看到采样率；不判断重采样历史",
}

# Metric groups for display; a metric outside every group falls back to "other".
METRIC_GROUPS: dict[str, str] = {
    "integrated_lufs": "loudness", "loudness_range_lu": "loudness",
    "true_peak_dbfs": "loudness", "sample_peak_dbfs": "loudness",
    "rms_dbfs": "loudness", "crest_factor_db": "loudness", "plr_db": "loudness",
    "clipping_sample_count": "integrity", "clipping_sample_ratio": "integrity",
    "near_clipping_sample_count": "integrity", "dc_offset_left": "integrity",
    "dc_offset_right": "integrity", "silence_ratio": "integrity",
    "longest_silence_seconds": "integrity", "invalid_sample_count": "integrity",
    "finite_sample_ratio": "integrity",
    "spectral_centroid_hz": "spectral", "spectral_rolloff_85_hz": "spectral",
    "spectral_rolloff_95_hz": "spectral", "spectral_flatness": "spectral",
    "spectral_flux": "spectral", "estimated_high_frequency_cutoff_hz": "spectral",
    "estimated_noise_floor_dbfs": "spectral",
    "stereo_correlation": "stereo", "mid_energy_ratio": "stereo",
    "side_energy_ratio": "stereo", "side_to_mid_db": "stereo",
    "stereo_width_proxy": "stereo", "negative_correlation_ratio": "stereo",
    "phase_risk_ratio": "stereo",
    "duration": "format", "channels": "format", "sample_rate": "format",
}

GROUP_LABELS = {
    "loudness": "响度与动态",
    "integrity": "信号完整性",
    "spectral": "频谱",
    "bands": "频段能量占比",
    "stereo": "立体声",
    "format": "格式",
    "other": "其他",
}

_BAND_METRICS = (
    "sub_20_60_hz", "bass_60_120_hz", "low_mid_120_250_hz", "mid_250_500_hz",
    "core_mid_500_2000_hz", "presence_2000_5000_hz", "brilliance_5000_10000_hz",
    "air_10000_16000_hz", "ultrasonic_16000_24000_hz",
)

# Absolute checks for the standalone analysis path. The delta rules in
# judgment.py need a before/after pair; a single analyzed source has none, so
# the report layer applies the absolute reading of the same versioned
# thresholds. Only checks whose limits already exist in UNIVERSAL_THRESHOLDS
# are implemented here — no new thresholds in this layer.
_ABSOLUTE_CHECK_VERSION = f"judgment-rules-v{JUDGMENT_RULES_VERSION}-absolute"
_TP_MARGIN_DB = UNIVERSAL_THRESHOLDS["true_peak_margin_reduced"]["min_margin_db"]

# Findings carry the calibration status of the threshold that produced them
# (Layer C provenance), so consumers see the trust level inside the report.
_CALIBRATION_BY_FINDING_CODE = {
    "CLIPPING_PRESENT": "new_clipping",
    "TRUE_PEAK_MARGIN_EXCEEDED": "true_peak_margin_reduced",
}


def _calibration_fields(rule_key: str | None) -> dict:
    prov = THRESHOLD_PROVENANCE.get(rule_key) if rule_key else None
    if prov is None:
        return {"reference_basis": rule_key, "calibration_status": None,
                "threshold_source_class": None}
    return {
        "reference_basis": rule_key,
        "calibration_status": prov["calibration_status"],
        "threshold_source_class": prov["source_class"],
    }


def _absolute_flags(metrics: dict) -> list[dict]:
    flags: list[dict] = []

    def value(name: str):
        entry = metrics.get(name)
        return entry.get("value") if isinstance(entry, dict) else None

    clipping = value("clipping_sample_count")
    if clipping is not None and clipping > 0:
        flags.append({
            "code": "CLIPPING_PRESENT", "severity": "BLOCKING",
            "message": "source contains full-scale samples",
            "metric": "clipping_sample_count", "observed_value": clipping,
            "unit": "count", "classification": "TECHNICAL_RISK", "confidence": 0.9,
            **_calibration_fields(_CALIBRATION_BY_FINDING_CODE["CLIPPING_PRESENT"]),
        })
    true_peak = value("true_peak_dbfs")
    if true_peak is not None and true_peak > -_TP_MARGIN_DB:
        flags.append({
            "code": "TRUE_PEAK_MARGIN_EXCEEDED", "severity": "WARNING",
            "message": f"true peak margin below {_TP_MARGIN_DB:g} dB",
            "metric": "true_peak_dbfs", "observed_value": true_peak,
            "unit": "dBFS", "classification": "TECHNICAL_RISK", "confidence": 0.9,
            **_calibration_fields(_CALIBRATION_BY_FINDING_CODE["TRUE_PEAK_MARGIN_EXCEEDED"]),
        })
    return flags


# Conservative post-processing drafts. A finding maps to a graph node draft
# only when the intervention is standard, reversible, and does not require a
# musical decision. Everything else stays unmapped on purpose.
_PLAN_NODE_DRAFTS: dict[str, dict] = {
    "TRUE_PEAK_MARGIN_EXCEEDED": {
        "op": "limiter",
        "params": {"ceiling_dbfs": -1.0},
        "reason": f"true peak margin below {_TP_MARGIN_DB:g} dB; a -1 dBFS "
                  "ceiling restores inter-sample headroom without touching "
                  "tonal balance",
    },
}

_UNMAPPABLE_NOTES = {
    "CLIPPING_PRESENT": "clipping cannot be repaired by limiting; repair "
                        "requires a remix/re-render decision upstream",
}


def analyze_workflow_decision(flags: list[dict]) -> tuple[str, list[str]]:
    """Workflow language for a standalone source (no processing context)."""
    blocking = [f["code"] for f in flags if f["severity"] == "BLOCKING"]
    warnings = [f["code"] for f in flags if f["severity"] == "WARNING"]
    if blocking:
        return "REMEDIATION_REQUIRED", [f"blocking: {code}" for code in blocking]
    if warnings:
        return "REVIEW_RECOMMENDED", [f"warning: {code}" for code in warnings]
    return "NO_TECHNICAL_BLOCKERS", []


def _plan(findings: list[dict], source: str) -> dict:
    nodes: list[dict] = []
    notes: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        code = finding["code"]
        draft = _PLAN_NODE_DRAFTS.get(code)
        if draft is not None and code not in seen:
            seen.add(code)
            nodes.append({
                "op": draft["op"],
                "params": dict(draft["params"]),
                "reason": draft["reason"],
                "evidence_refs": [code],
                "reversible": True,
            })
        elif code in _UNMAPPABLE_NOTES and code not in seen:
            seen.add(code)
            notes.append(f"{code}: {_UNMAPPABLE_NOTES[code]}")
    next_actions = [
        "moodify protocol process <job.json>  # "
        '{"protocol": "moodify.sound/0.2", "type": "process", "source": '
        f'"{source}", "preset": "<preset>", "output_dir": "<dir>"}}'
    ]
    return {
        "status": "DRAFT_PLAN_NOT_EXECUTED",
        "nodes": nodes,
        "next_actions": next_actions,
        "notes": notes,
    }


def _measurements(metrics: dict) -> list[dict]:
    rows: list[dict] = []
    for name in sorted(metrics):
        item = metrics[name]
        if not isinstance(item, dict):
            continue
        value = item.get("value")
        if value is not None and not isinstance(value, (int, float)):
            # non-numeric probe fields (e.g. source_sha256) are reported in
            # source/provenance, not as measurements
            continue
        row = {
            "id": name,
            "value": value,
            "unit": item.get("unit"),
            "method": item.get("method"),
            "status": item.get("status", "VALID"),
            "warnings": list(item.get("warnings") or []),
        }
        if name in VISIBILITY:
            row["visibility"] = VISIBILITY[name]
        if name in _BAND_METRICS:
            row["group"] = "bands"
        else:
            row["group"] = METRIC_GROUPS.get(name, "other")
        rows.append(row)
    return rows


def _findings(metrics: dict) -> list[dict]:
    from moodify.auditory.judgment import evaluate_risk_flags

    rows: list[dict] = []
    for flag in evaluate_risk_flags({}, {}, metrics):
        rows.append({
            "code": flag.code,
            "severity": flag.severity,
            "message": flag.message,
            "metric": flag.metric,
            "observed_value": flag.observed_value,
            "unit": flag.unit,
            "classification": flag.classification,
            "confidence": flag.confidence,
            "evidence_refs": list(flag.evidence_refs),
            "check": "delta_rule",
            **_calibration_fields(flag.reference_basis),
        })
    for flag in _absolute_flags(metrics):
        rows.append({
            **flag,
            "evidence_refs": ["metrics.json"],
            "check": "absolute_rule",
        })
    return rows


MSP_REPORT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Moodify MSP 0.2 analysis report",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "protocol", "report_schema_version", "generated_at", "job", "case",
        "source", "representation", "measurements", "findings", "plan",
        "judgment_boundary", "technical_state", "provenance",
    ],
    "properties": {
        "protocol": {"const": "moodify.sound/0.2"},
        "report_schema_version": {"const": REPORT_SCHEMA_VERSION},
        "generated_at": {"type": "string"},
        "job": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "source"],
            "properties": {
                "type": {"enum": ["analyze", "compare"]},
                "source": {"type": "string"},
            },
        },
        "case": {
            "type": "object",
            "additionalProperties": False,
            "required": ["case_id"],
            "properties": {
                "case_id": {"type": "string"},
                "case_root": {"type": "string"},
            },
        },
        "source": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "sha256"],
            "properties": {
                "name": {"type": "string"},
                "sha256": {"type": "string"},
                "duration_s": {"type": ["number", "null"]},
                "channels": {"type": ["integer", "null"]},
                "sample_rate": {"type": ["integer", "null"]},
            },
        },
        "representation": {
            "type": "object",
            "additionalProperties": False,
            "required": ["profile", "spectrograms", "timeline_path",
                         "timeline_windows", "stft_arrays"],
            "properties": {
                "profile": {"type": "string"},
                "spectrograms": {"type": "array", "items": {"type": "string"}},
                "timeline_path": {"type": ["string", "null"]},
                "timeline_windows": {"type": ["integer", "null"]},
                "stft_arrays": {"type": ["string", "null"]},
            },
        },
        "measurements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "value", "unit", "method", "status",
                             "warnings", "group"],
                "properties": {
                    "id": {"type": "string"},
                    "value": {"type": ["number", "null"]},
                    "unit": {"type": ["string", "null"]},
                    "method": {"type": ["string", "null"]},
                    "status": {"type": "string"},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                    "visibility": {"type": "string"},
                    "group": {"type": "string"},
                },
            },
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["code", "severity", "message", "metric",
                             "observed_value", "unit", "classification",
                             "confidence", "evidence_refs", "check"],
                "properties": {
                    "code": {"type": "string"},
                    "severity": {"enum": ["INFO", "WARNING", "BLOCKING"]},
                    "message": {"type": "string"},
                    "metric": {"type": ["string", "null"]},
                    "observed_value": {"type": ["number", "null"]},
                    "unit": {"type": ["string", "null"]},
                    "classification": {"type": "string"},
                    "confidence": {"type": ["number", "null"]},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    "check": {"enum": ["delta_rule", "absolute_rule"]},
                    "reference_basis": {"type": ["string", "null"]},
                    "calibration_status": {"type": ["string", "null"]},
                    "threshold_source_class": {"type": ["string", "null"]},
                },
            },
        },
        "plan": {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "nodes", "next_actions", "notes"],
            "properties": {
                "status": {"const": "DRAFT_PLAN_NOT_EXECUTED"},
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["op", "params", "reason", "evidence_refs",
                                     "reversible"],
                        "properties": {
                            "op": {"type": "string"},
                            "params": {"type": "object"},
                            "reason": {"type": "string"},
                            "evidence_refs": {"type": "array",
                                              "items": {"type": "string"}},
                            "reversible": {"type": "boolean"},
                        },
                    },
                },
                "next_actions": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        },
        "judgment_boundary": {
            "type": "object",
            "additionalProperties": False,
            "required": ["layer1_measurement", "layer2_comparison",
                         "layer3_musical_judgment", "layer4_production_judgment",
                         "layer5_cultural_judgment"],
            "properties": {
                "layer1_measurement": {"enum": ["EXECUTED", "NOT_RUN", "NOT_PROMISED"]},
                "layer2_comparison": {"enum": ["EXECUTED", "NOT_RUN", "NOT_PROMISED"]},
                "layer3_musical_judgment": {"enum": ["EXECUTED", "NOT_RUN", "NOT_PROMISED"]},
                "layer4_production_judgment": {"enum": ["EXECUTED", "NOT_RUN", "NOT_PROMISED"]},
                "layer5_cultural_judgment": {"enum": ["EXECUTED", "NOT_RUN", "NOT_PROMISED"]},
            },
        },
        "technical_state": {
            "type": "object",
            "additionalProperties": False,
            "required": ["overall", "workflow_decision", "reasons"],
            "properties": {
                "overall": {"enum": ["OK", "RISK", "PARTIAL"]},
                "workflow_decision": {"type": "string"},
                "reasons": {"type": "array", "items": {"type": "string"}},
            },
        },
        "provenance": {
            "type": "object",
            "additionalProperties": False,
            "required": ["core_version", "profile_id", "profile_parameters_sha256",
                         "judgment_rules_version", "ffmpeg"],
            "properties": {
                "core_version": {"type": "string"},
                "profile_id": {"type": "string"},
                "profile_parameters_sha256": {"type": "string"},
                "judgment_rules_version": {"type": "string"},
                "judgment_calibration": {
                    "type": "object",
                    "required": ["registry_version", "rules_total", "calibrated",
                                 "default_uncalibrated", "by_source_class",
                                 "uncalibrated_rules", "note"],
                    "properties": {
                        "registry_version": {"type": "string"},
                        "rules_total": {"type": "integer"},
                        "calibrated": {"type": "integer"},
                        "default_uncalibrated": {"type": "integer"},
                        "by_source_class": {"type": "object"},
                        "uncalibrated_rules": {"type": "array",
                                               "items": {"type": "string"}},
                        "note": {"type": "string"},
                    },
                },
                "ffmpeg": {"type": "string"},
            },
        },
        "comparison": {
            "type": "object",
            "additionalProperties": False,
            "required": ["reference", "loudness_normalization", "metric_deltas",
                         "band_deltas", "delta_spectrograms", "pair_checks",
                         "visibility_note"],
            "properties": {
                "reference": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name", "sha256", "case_id", "case_root"],
                    "properties": {
                        "name": {"type": "string"},
                        "sha256": {"type": "string"},
                        "case_id": {"type": "string"},
                        "case_root": {"type": "string"},
                        "duration_s": {"type": ["number", "null"]},
                        "channels": {"type": ["integer", "null"]},
                        "sample_rate": {"type": ["integer", "null"]},
                    },
                },
                "loudness_normalization": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["gain_db", "valid", "method"],
                    "properties": {
                        "gain_db": {"type": ["number", "null"]},
                        "valid": {"type": "boolean"},
                        "method": {"type": "string"},
                    },
                },
                "metric_deltas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "before", "after", "absolute_delta",
                                     "unit", "direction"],
                        "properties": {
                            "id": {"type": "string"},
                            "before": {"type": ["number", "null"]},
                            "after": {"type": ["number", "null"]},
                            "absolute_delta": {"type": ["number", "null"]},
                            "relative_delta": {"type": ["number", "null"]},
                            "unit": {"type": ["string", "null"]},
                            "direction": {"enum": ["INCREASE", "DECREASE", "UNCHANGED"]},
                            "visibility": {"type": "string"},
                            "group": {"type": "string"},
                        },
                    },
                },
                "band_deltas": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["raw", "normalized"],
                    "properties": {
                        "raw": {"type": "object",
                                "additionalProperties": {"type": ["number", "null"]}},
                        "normalized": {"type": "object",
                                       "additionalProperties": {"type": ["number", "null"]}},
                    },
                },
                "delta_spectrograms": {"type": "array", "items": {"type": "string"}},
                "pair_checks": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["profile_hash_match", "duration_within_tolerance",
                                 "channels_match", "duration_tolerance_s"],
                    "properties": {
                        "profile_hash_match": {"type": "boolean"},
                        "duration_within_tolerance": {"type": "boolean"},
                        "channels_match": {"type": "boolean"},
                        "duration_tolerance_s": {"type": "number"},
                    },
                },
                "visibility_note": {"type": "string"},
            },
        },
    },
    # A compare job must carry its comparison evidence; analyze reports must
    # not (the boundary between L1-only and L1+L2 stays machine-checkable).
    "allOf": [{
        "if": {"properties": {"job": {"properties": {"type": {"const": "compare"}}}},
               "required": ["job"]},
        "then": {"required": ["comparison"]},
        "else": {"not": {"required": ["comparison"]}},
    }],
}


class ReportError(ValueError):
    """Raised when a 0.2 report cannot be assembled or fails schema validation."""


L2_VISIBILITY_NOTE = (
    "对比层只描述候选相对参考的相对变化方向与幅度（响度对齐后）。"
    "“变化是否更好”的显著性阈值属于 Layer C 校准，本层不判断；"
    "听感结论仍需人类或算法评审权威。"
)


def _load_case_bundle(case_root: Path) -> tuple[dict, dict, dict]:
    """Load (case, metrics, auditory_report) or fail closed."""
    case_root = case_root.resolve()
    case_path = case_root / "case.json"
    metrics_path = case_root / "scan" / "metrics.json"
    auditory_path = case_root / "auditory_report.json"
    for path in (case_path, metrics_path, auditory_path):
        if not path.is_file():
            raise ReportError(f"case bundle is missing {path.name}: {case_root}")
    return (
        json.loads(case_path.read_text(encoding="utf-8")),
        json.loads(metrics_path.read_text(encoding="utf-8")),
        json.loads(auditory_path.read_text(encoding="utf-8")),
    )


def build_protocol_report(case_root: Path) -> dict:
    """Assemble, schema-validate and persist ``report.json`` for a 1.0 case."""
    report = _assemble_report(case_root, job_type="analyze")
    case_root = case_root.resolve()
    (case_root / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return report


def _assemble_report(
    case_root: Path,
    *,
    job_type: str,
    comparison: dict | None = None,
    candidate_case_root: Path | None = None,
) -> dict:
    from moodify.auditory.decode import ffmpeg_version
    from moodify.release import PRODUCT_VERSION, PROFILE_ID
    from moodify.auditory.profiles import get_profile

    case_root = case_root.resolve()
    case, metrics, auditory = _load_case_bundle(case_root)

    findings = _findings(metrics)
    decision, reasons = analyze_workflow_decision(findings)
    source_name = auditory.get("source_name") or case_root.name
    sha256 = auditory.get("source_sha256") or case.get("source_id") or "sha256:unknown"

    spectrograms = ["scan/spectrum_linear.png", "scan/spectrum_log.png"]
    timeline_path = case_root / "scan" / "timeline_metrics.jsonl"
    timeline_windows = None
    if timeline_path.is_file():
        timeline_windows = sum(
            1 for line in timeline_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    profile = get_profile(PROFILE_ID)
    job_source = auditory.get("source_name", "")
    # The compare report's subject is the candidate; its bundle still lives in
    # the candidate case root, so the persisted report carries the root path
    # for re-render image loading.
    case_block: dict = {"case_id": case.get("case_id", "")}
    if job_type == "compare":
        case_block["case_root"] = str((candidate_case_root or case_root).resolve())
    report = {
        "protocol": "moodify.sound/0.2",
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "job": {"type": job_type, "source": job_source},
        "case": case_block,
        "source": {
            "name": source_name,
            "sha256": sha256,
            "duration_s": _metric_value(metrics, "duration"),
            "channels": _metric_value(metrics, "channels"),
            "sample_rate": _metric_value(metrics, "sample_rate"),
        },
        "representation": {
            "profile": PROFILE_ID,
            "spectrograms": spectrograms,
            "timeline_path": "scan/timeline_metrics.jsonl" if timeline_windows else None,
            "timeline_windows": timeline_windows,
            "stft_arrays": "scan/analysis_data.npz" if (case_root / "scan" / "analysis_data.npz").is_file() else None,
        },
        "measurements": _measurements(metrics),
        "findings": findings,
        "plan": _plan(findings, job_source),
        "judgment_boundary": {
            "layer1_measurement": "EXECUTED",
            "layer2_comparison": "EXECUTED" if comparison is not None else "NOT_RUN",
            "layer3_musical_judgment": "NOT_PROMISED",
            "layer4_production_judgment": "NOT_PROMISED",
            "layer5_cultural_judgment": "NOT_PROMISED",
        },
        "technical_state": {
            "overall": auditory.get("overall_status", "PARTIAL"),
            "workflow_decision": decision,
            "reasons": reasons,
        },
        "provenance": {
            "core_version": PRODUCT_VERSION,
            "profile_id": PROFILE_ID,
            "profile_parameters_sha256": "sha256:"
            + hashlib.sha256(profile.canonical().encode("utf-8")).hexdigest(),
            "judgment_rules_version": JUDGMENT_RULES_VERSION,
            "judgment_calibration": calibration_summary(),
            "ffmpeg": ffmpeg_version(),
        },
    }
    if comparison is not None:
        report["comparison"] = comparison
    try:
        jsonschema_validate(report, MSP_REPORT_SCHEMA)
    except ValidationError as exc:
        raise ReportError(f"protocol report failed schema validation: {exc.message}") from exc
    return report


def _comparison_section(
    deltas,
    reference_evidence,
    *,
    reference_name: str,
    reference_sha256: str,
    reference_case_root: Path,
    pair_checks: dict,
) -> dict:
    """Build the schema-shaped ``comparison`` section from a DeltaResult."""
    rows: list[dict] = []
    for key, entry in deltas.metric_delta.items():
        row = {
            "id": key,
            "before": entry["before"],
            "after": entry["after"],
            "absolute_delta": entry["absolute_delta"],
            "relative_delta": entry.get("relative_delta"),
            "unit": entry["unit"],
            "direction": entry["direction"],
            "group": "bands" if key in _BAND_METRICS else METRIC_GROUPS.get(key, "other"),
        }
        if key in VISIBILITY:
            row["visibility"] = VISIBILITY[key]
        rows.append(row)
    metrics = reference_evidence.metrics
    reference_block = {
        "name": reference_name,
        "sha256": reference_sha256,
        "case_id": reference_evidence.case_id,
        "case_root": str(reference_case_root.resolve()),
        "duration_s": _metric_value(metrics, "duration"),
        "channels": _metric_value(metrics, "channels"),
        "sample_rate": _metric_value(metrics, "sample_rate"),
    }
    return {
        "reference": reference_block,
        "loudness_normalization": {
            "gain_db": deltas.normalization_gain_db if deltas.normalization_valid else None,
            "valid": deltas.normalization_valid,
            "method": deltas.normalized_method,
        },
        "metric_deltas": rows,
        "band_deltas": {
            "raw": deltas.raw_band_deltas,
            "normalized": deltas.normalized_band_deltas,
        },
        "delta_spectrograms": ["delta_spectrum_linear.png", "delta_spectrum_log.png"],
        "pair_checks": pair_checks,
        "visibility_note": L2_VISIBILITY_NOTE,
    }


def build_compare_report(
    compare_root: Path,
    *,
    candidate_case_root: Path,
    reference_case_root: Path,
    reference_evidence,
    deltas,
    pair_checks: dict,
) -> dict:
    """Assemble, schema-validate and persist a 0.2 ``compare`` report.

    The report subject is the candidate; the reference enters only through the
    comparison section. *compare_root* must already exist (the caller renders
    delta spectrograms into it first).
    """
    compare_root = compare_root.resolve()
    candidate_case_root = candidate_case_root.resolve()
    reference_case_root = reference_case_root.resolve()
    ref_case, _ref_metrics, ref_auditory = _load_case_bundle(reference_case_root)
    comparison = _comparison_section(
        deltas,
        reference_evidence,
        reference_name=ref_auditory.get("source_name") or reference_case_root.name,
        reference_sha256=(ref_auditory.get("source_sha256")
                          or ref_case.get("source_id") or "sha256:unknown"),
        reference_case_root=reference_case_root,
        pair_checks=pair_checks,
    )
    report = _assemble_report(
        candidate_case_root,
        job_type="compare",
        comparison=comparison,
        candidate_case_root=candidate_case_root,
    )
    (compare_root / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return report


def _metric_value(metrics: dict, name: str):
    entry = metrics.get(name)
    if isinstance(entry, dict):
        return entry.get("value")
    return None


def write_report_bundle(case_root: Path, *, rewrite_json: bool = True) -> dict:
    """Assemble report.json and render its markdown/HTML twins.

    ``rewrite_json=False`` re-renders the twins from an existing report.json
    (the ``moodify report`` command), leaving the validated JSON untouched.
    """
    from moodify.auditory.report_render import render_report_html, render_report_markdown

    case_root = case_root.resolve()
    report_path = case_root / "report.json"
    if rewrite_json or not report_path.is_file():
        report = build_protocol_report(case_root)
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if "comparison" in report:
            # compare reports keep their images across three roots; re-render
            # them through the compare-aware loader
            return write_compare_bundle(case_root, report)
    images: dict[str, bytes] = {}
    for name in report["representation"]["spectrograms"]:
        path = case_root / name
        if path.is_file():
            images[name] = path.read_bytes()
    (case_root / "report.md").write_text(
        render_report_markdown(report), encoding="utf-8")
    (case_root / "report.html").write_text(
        render_report_html(report, images), encoding="utf-8")
    return report


def write_compare_bundle(compare_root: Path, report: dict) -> dict:
    """Render a compare report's markdown/HTML twins from assembled JSON.

    Image namespaces in a compare report:
    - ``scan/spectrum_*.png``      — candidate spectrograms, from ``case.case_root``
    - ``reference/scan/spectrum_*``— reference spectrograms, from
      ``comparison.reference.case_root``
    - ``delta_spectrum_*.png``     — delta images, from the compare root itself
    """
    from moodify.auditory.report_render import render_report_html, render_report_markdown

    compare_root = compare_root.resolve()
    candidate_root = Path(report["case"]["case_root"])
    reference_root = Path(report["comparison"]["reference"]["case_root"])
    images: dict[str, bytes] = {}
    for name in report["representation"]["spectrograms"]:
        path = candidate_root / name
        if path.is_file():
            images[name] = path.read_bytes()
    for name in report["comparison"]["delta_spectrograms"]:
        path = compare_root / name
        if path.is_file():
            images[name] = path.read_bytes()
    for name in ("scan/spectrum_linear.png", "scan/spectrum_log.png"):
        path = reference_root / name
        if path.is_file():
            images[f"reference/{name}"] = path.read_bytes()
    (compare_root / "report.md").write_text(
        render_report_markdown(report), encoding="utf-8")
    (compare_root / "report.html").write_text(
        render_report_html(report, images), encoding="utf-8")
    return report
