"""Era Diagnostic report serialization (MFY-CR-P03).

Produces ``era_diagnostic.v0.1.json`` (machine) and ``ERA_DIAGNOSTIC_REPORT.md``
(human). Both are deterministic: findings are ordered by category and the JSON
uses sorted keys.
"""

from __future__ import annotations

import json
from typing import Any

from moodify.era_diagnostic.contract import (
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)

_CATEGORY_ORDER = [c for c in DiagnosticCategory]

_DISPLAY_STATUS = {
    FindingStatus.OBSERVED: "OBSERVED",
    FindingStatus.POSSIBLE_TECHNICAL_LIMITATION: "POSSIBLE_TECHNICAL_LIMITATION",
    FindingStatus.LIKELY_ARTISTIC_CHARACTER: "LIKELY_ARTISTIC_CHARACTER",
    FindingStatus.INSUFFICIENT_EVIDENCE: "INSUFFICIENT_EVIDENCE",
    FindingStatus.NOT_APPLICABLE: "NOT_APPLICABLE",
    FindingStatus.NOT_SUPPORTED_IN_V0_1: "NOT_SUPPORTED_IN_V0_1",
}


def _sorted(findings: list[EraDiagnosticFinding]) -> list[EraDiagnosticFinding]:
    order = {c: i for i, c in enumerate(_CATEGORY_ORDER)}
    return sorted(findings, key=lambda f: order[f.category])


def build_report_dict(
    findings: list[EraDiagnosticFinding],
    *,
    source_identifier: str | None = None,
    era_hint: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": "era_diagnostic.v0.1",
        "version": "era-diagnostic-v0.1",
        "source_identifier": source_identifier,
        "era_hint": era_hint,
        "note": "No reconstruction action was authorized by this diagnostic alone.",
        "findings": [f.to_dict() for f in _sorted(findings)],
    }


def dump_json(
    findings: list[EraDiagnosticFinding],
    out_path,
    *,
    source_identifier: str | None = None,
    era_hint: str | None = None,
) -> None:
    payload = build_report_dict(
        findings, source_identifier=source_identifier, era_hint=era_hint
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def build_markdown_report(
    findings: list[EraDiagnosticFinding],
    *,
    source_identifier: str | None = None,
    era_hint: str | None = None,
) -> str:
    lines = [
        "# Era Diagnostic Report v0.1",
        "",
        f"**Source:** {source_identifier or 'unknown'}",
    ]
    if era_hint:
        lines.append(f"**Era hint (metadata only, not a decision input):** {era_hint}")
    lines += ["", "> No reconstruction action was authorized by this diagnostic alone.", ""]

    for finding in _sorted(findings):
        name = finding.category.value
        status = _DISPLAY_STATUS[finding.status]
        confidence = finding.confidence.value if finding.confidence else "-"
        lines += [
            f"## {name} — {status} (confidence: {confidence})",
            "",
            finding.reasoning_summary,
            "",
            "Evidence:",
        ]
        for ref in finding.measurement_refs:
            lines.append(f"- {ref}")
        if finding.known_ambiguities:
            lines += ["", "Ambiguity:"]
            for a in finding.known_ambiguities:
                lines.append(f"- {a}")
        lines += [
            "",
            f"Requires human review: {'YES' if finding.requires_human_review else 'no'}",
            "Action: NONE_IN_P03",
            "",
        ]
    lines += ["---", "*Diagnosis only. It does not authorize processing.*"]
    return "\n".join(lines)


def dump_markdown(
    findings: list[EraDiagnosticFinding],
    out_path,
    *,
    source_identifier: str | None = None,
    era_hint: str | None = None,
) -> None:
    text = build_markdown_report(
        findings, source_identifier=source_identifier, era_hint=era_hint
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
