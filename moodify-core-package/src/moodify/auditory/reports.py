"""Comparison reports, the four-image contact sheet, and the Phase I auditory report
(DSK-MFY-AUDITORY-SCAN-001 / MFY-PHASE1-FREEZE-001)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


_SECTION_METRICS = {
    "loudness_dynamics": {"integrated_lufs", "crest_factor_db", "true_peak_dbfs"},
    "spectral_balance": {"bass_60_120_hz", "brilliance_5000_10000_hz"},
    "low_frequency": {"bass_60_120_hz"},
    "high_frequency_cutoff": {"estimated_high_frequency_cutoff_hz"},
    "stereo_field": {"negative_correlation_ratio"},
    "phase": {"phase_risk_ratio"},
    "transients": {"crest_factor_db"},
    "artifact_detection": {"clipping_sample_count", "invalid_sample_count"},
    "musical_structure": set(),
}


def _metric_is_valid(metrics: dict, name: str) -> bool:
    value = metrics.get(name)
    if isinstance(value, dict):
        return value.get("value") is not None and value.get("status", "VALID") == "VALID"
    return value is not None


def _derive_sections(metrics: dict, findings: list[dict]) -> dict[str, str]:
    sections: dict[str, str] = {}
    finding_metrics = {
        finding.get("metric")
        for finding in findings
        if finding.get("severity") in {"WARNING", "BLOCKING", "HIGH", "CRITICAL"}
    }
    for section, required in _SECTION_METRICS.items():
        if not required:
            sections[section] = "UNKNOWN"
        elif not all(_metric_is_valid(metrics, name) for name in required):
            sections[section] = "UNKNOWN"
        elif required & finding_metrics:
            sections[section] = "RISK"
        else:
            sections[section] = "PASS"
    return sections


def build_auditory_report(
    out_path: Path,
    *,
    source_name: str,
    case_id: str,
    source_sha256: str,
    analysis_version: str,
    overall_status: str,
    metrics: dict,
    findings: list[dict],
    evidence_index: dict,
    summary: str,
    overall_confidence: float | None = None,
) -> dict:
    """Phase I 机器可读听觉报告（06_AUDITORY_REPORT_SPEC）。human + machine 双形态之一。

    每条 finding 必须携带 evidence_refs；HIGH/CRITICAL 判断若缺证据引用则标记
    UNKNOWN 状态而非静默通过（08_ACCEPTANCE_TESTS 失败语义）。
    """
    sections = _derive_sections(metrics, findings)
    unresolved = []
    for finding in findings:
        refs = finding.get("evidence_refs") or []
        missing_refs = [ref for ref in refs if ref not in evidence_index]
        if finding.get("severity") in {"BLOCKING", "HIGH", "CRITICAL"} and (
            not refs or missing_refs
        ):
            unresolved.append({"code": finding.get("code"), "missing_refs": missing_refs})
    if unresolved or "UNKNOWN" in sections.values():
        overall_status = "PARTIAL"
    elif any(value == "RISK" for value in sections.values()):
        overall_status = "RISK"
    report = {
        "report_id": f"report-{case_id}",
        "case_id": case_id,
        "source_name": source_name,
        "source_sha256": source_sha256,
        "analysis_version": analysis_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "overall_confidence": overall_confidence,
        "summary": summary,
        "sections": sections,
        "findings": findings,
        "evidence_index": evidence_index,
        "unresolved_evidence_findings": [item["code"] for item in unresolved],
        "unresolved_evidence_details": unresolved,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report



def build_contact_sheet(
    before_linear: Path,
    after_linear: Path,
    before_log: Path,
    after_log: Path,
    out_path: Path,
    *,
    case_id: str,
    source_sha_short: str,
    candidate_sha_short: str,
    profile_id: str,
) -> None:
    """Four-image contact sheet: before/after x linear/log."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.image import imread

    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    panels = [
        (axes[0, 0], before_linear, "BEFORE — LINEAR FREQUENCY"),
        (axes[0, 1], after_linear, "AFTER — LINEAR FREQUENCY"),
        (axes[1, 0], before_log, "BEFORE — LOG FREQUENCY"),
        (axes[1, 1], after_log, "AFTER — LOG FREQUENCY"),
    ]
    for ax, path, title in panels:
        img = imread(str(path))
        ax.imshow(img)
        ax.set_title(title, fontsize=11)
        ax.axis("off")
    fig.suptitle(
        f"case={case_id}  source={source_sha_short}  candidate={candidate_sha_short}\n"
        f"profile={profile_id}  generated={datetime.now(timezone.utc).isoformat()}",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def build_comparison_report(
    out_path: Path,
    *,
    case_id: str,
    candidate_id: str,
    profile_id: str,
    profile_hash: str,
    metric_delta: dict,
    judgment: dict,
    normalization: dict,
    raw_band_deltas: dict,
    normalized_band_deltas: dict,
    plan_id: str | None,
    judgment_rules: dict,
    source_sha256: str,
    candidate_sha256: str,
) -> None:
    report = {
        "case_id": case_id,
        "candidate_id": candidate_id,
        "scan_profile_id": profile_id,
        "scan_profile_hash": profile_hash,
        "processing_plan_id": plan_id,
        "normalization": normalization,
        "raw_band_deltas": raw_band_deltas,
        "normalized_band_deltas": normalized_band_deltas,
        "metrics_delta": metric_delta,
        "judgment": judgment,
        "judgment_rules": judgment_rules,
        "source_sha256": source_sha256,
        "candidate_sha256": candidate_sha256,
        "human_listening_required": True,
        "artistic_approval_granted": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
