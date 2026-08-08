from __future__ import annotations

from math import isfinite
from typing import Any

from .models import GateIssue, GateResult


def _scan_non_finite(value: Any, path: str = "$") -> list[str]:
    bad: list[str] = []
    if isinstance(value, float) and not isfinite(value):
        bad.append(path)
    elif isinstance(value, dict):
        for key, child in value.items():
            bad.extend(_scan_non_finite(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            bad.extend(_scan_non_finite(child, f"{path}[{index}]"))
    return bad


def evaluate_report(report: dict[str, Any], deep_expected: bool = False) -> GateResult:
    issues: list[GateIssue] = []

    duration = report.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        issues.append(
            GateIssue(
                code="OCEAN_REQUIRED_DURATION",
                severity="error",
                message="Ocean report has no positive duration.",
                path="$.duration",
            )
        )

    if not report.get("name"):
        issues.append(
            GateIssue(
                code="OCEAN_NAME_MISSING",
                severity="warning",
                message="Ocean report has no source name.",
                path="$.name",
            )
        )

    classification = report.get("classification") or {}
    confidence = classification.get("confidence")
    if classification and isinstance(confidence, (int, float)) and confidence < 0.6:
        issues.append(
            GateIssue(
                code="OCEAN_LOW_CLASSIFICATION_CONFIDENCE",
                severity="warning",
                message=f"Classification confidence is low: {confidence}.",
                path="$.classification.confidence",
            )
        )

    if deep_expected and not report.get("deepVersion"):
        issues.append(
            GateIssue(
                code="OCEAN_DEEP_OUTPUT_MISSING",
                severity="error",
                message="Deep analysis was requested but deepVersion is missing.",
                path="$.deepVersion",
            )
        )

    if report.get("stemNotes") and not report.get("stemTimeline"):
        issues.append(
            GateIssue(
                code="OCEAN_STEM_TIMELINE_MISSING",
                severity="warning",
                message="Stem notes exist without a stem activity timeline.",
                path="$.stemTimeline",
            )
        )

    notes = report.get("notes") or []
    declared_total = report.get("total_notes", report.get("totalNotes"))
    if isinstance(declared_total, int) and declared_total != len(notes):
        issues.append(
            GateIssue(
                code="OCEAN_NOTE_COUNT_MISMATCH",
                severity="warning",
                message=(
                    f"Declared note count {declared_total} does not match "
                    f"actual list length {len(notes)}."
                ),
                path="$.notes",
            )
        )

    non_finite = _scan_non_finite(report)
    for path in non_finite[:25]:
        issues.append(
            GateIssue(
                code="OCEAN_NON_FINITE_NUMBER",
                severity="error",
                message="Report contains NaN or Infinity.",
                path=path,
            )
        )

    if report.get("notes"):
        issues.append(
            GateIssue(
                code="OCEAN_VELOCITY_SEMANTICS",
                severity="info",
                message=(
                    "MIDI velocity from basic-pitch must be treated as model "
                    "confidence proxy, not acoustic loudness."
                ),
                path="$.notes[*].velocity",
            )
        )

    experimental_fields = [
        key
        for key in ("voiceTexture", "voiceTimbre", "voiceSegments", "vocalParts")
        if report.get(key)
    ]
    if experimental_fields:
        issues.append(
            GateIssue(
                code="OCEAN_EXPERIMENTAL_LABELS",
                severity="info",
                message=(
                    "Voice and part labels are experimental observations and "
                    "must not be promoted to artistic ground truth."
                ),
                path="$",
            )
        )

    severities = {issue.severity for issue in issues}
    if "error" in severities:
        verdict = "FAIL"
    elif "warning" in severities:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return GateResult(
        verdict=verdict,
        issues=issues,
        metrics={
            "note_count": len(notes),
            "stem_count": len(report.get("stemNotes") or {}),
            "has_voice": bool(
                report.get("voiceProfile")
                or report.get("voiceTimbre")
                or report.get("voiceSegments")
            ),
            "has_lyrics": bool(report.get("lyrics")),
            "deep_version": report.get("deepVersion"),
        },
    )
