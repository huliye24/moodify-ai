"""Evidence resolution (MFY-PHASE1-DEPTH-004).

Assembles a JudgmentEvidence from a technical judgment, a Phase I-C
representation, Phase I-B events and source provenance. Lineage:
JUDGMENT -> EVENT/WINDOW -> MEASUREMENT -> PROFILE -> SOURCE -> RULE.
No audio transforms are re-run here (G13); everything consumes existing
artifacts.
"""

from __future__ import annotations

from typing import Any

from moodify.auditory.evidence.models import (
    Conflict,
    Coverage,
    EvidenceNode,
    JudgmentEvidence,
)
from moodify.auditory.evidence.scale import scale_for_duration_ms
from moodify.auditory.structure import StructureContext, annotate_event_with_structure
from moodify.auditory.uncertainty import Uncertainty

CLASSIFICATION_MAP = {
    "DEGRADED": "TECHNICAL_RISK",
    "REJECT_TECHNICAL": "TECHNICAL_RISK",
    "UNCERTAIN": "UNCERTAIN",
    "INCONCLUSIVE": "UNCERTAIN",
    "NEUTRAL": "NO_MEASURED_RISK",
    "IMPROVED": "INFORMATIONAL",
}


def assemble_judgment_evidence(
    judgment: Any,
    source_sha256: str,
    representation: Any | None = None,
    events: list[Any] | None = None,
    rule_versions: dict[str, str] | None = None,
    evaluated_domains: tuple[str, ...] = ("integrity", "level", "spectrum", "stereo"),
    channels: int = 2,
    structure: StructureContext | None = None,
) -> JudgmentEvidence:
    """Build the evidence graph for one judgment.

    structure (Chapter II §14): optional MSE context; when provided and
    reliable, EVENT nodes are annotated with section labels and boundary
    flags. Unreliable structure annotates nothing and records an
    uncertainty instead of fabricating certainty.
    """
    nodes: list[EvidenceNode] = []
    nodes.append(EvidenceNode(
        node_id="source", kind="SOURCE",
        ref=f"sha256:{source_sha256}",
        data={"source_sha256": source_sha256},
        epistemic_state="OBSERVED",
    ))
    if representation is not None:
        nodes.append(EvidenceNode(
            node_id="representation", kind="PROFILE",
            ref=representation.representation_id,
            data={
                "representation_version": representation.representation_version,
                "profile_ids": dict(representation.profile_ids),
            },
            scale="WHOLE_TRACK",
            epistemic_state="OBSERVED",
        ))

    rule_versions = dict(rule_versions or {})
    event_nodes = 0
    for event in events or []:
        event_id = getattr(event, "event_id", "")
        start_ms = getattr(event, "start_ms", 0)
        end_ms = getattr(event, "end_ms", 0)
        event_type = getattr(event, "event_type", "UNKNOWN")
        data: dict[str, Any] = {
            "event_type": event_type,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "evidence_windows": list(getattr(event, "evidence_windows", ())),
            "profile_id": getattr(event, "profile_id", ""),
        }
        if structure is not None:
            if structure.is_reliable:
                data.update(annotate_event_with_structure(event, structure))
        scale = scale_for_duration_ms(max(end_ms - start_ms, 0.0))
        epistemic = (
            "ASSOCIATED"
            if "CORRELATION" in event_type or "PHASE" in event_type
            else "INFERRED"
        )
        nodes.append(EvidenceNode(
            node_id=f"event:{event_id}", kind="EVENT",
            ref=event_id,
            data=data,
            scale=scale,
            epistemic_state=epistemic,
        ))
        event_nodes += 1
        rule_id = f"rule:{getattr(event, 'event_type', 'UNKNOWN')}"
        rule_versions.setdefault(rule_id, "temporal-hearing-v1")
        nodes.append(EvidenceNode(
            node_id=rule_id, kind="RULE",
            ref=rule_id,
            data={"rule_version": rule_versions.get(rule_id, "")},
        ))
    if representation is not None:
        for metric_key, metric in representation.global_summary.get("metrics", {}).items():
            if isinstance(metric, dict) and metric.get("value") is not None:
                nodes.append(EvidenceNode(
                    node_id=f"measurement:{metric_key}", kind="MEASUREMENT",
                    ref=metric_key,
                    data={
                        "value": metric["value"],
                        "unit": metric.get("unit", ""),
                        "method": metric.get("method", ""),
                        "status": metric.get("status", "VALID"),
                    },
                    scale="WHOLE_TRACK",
                    epistemic_state="OBSERVED",
                ))

    coverage = Coverage(
        evaluated_domains=evaluated_domains,
        unevaluated_domains=tuple(
            domain for domain in ("integrity", "level", "spectrum", "stereo")
            if domain not in evaluated_domains
        ),
    )

    uncertainties: list[Uncertainty] = []
    if structure is not None and not structure.is_reliable:
        uncertainties.append(Uncertainty(
            "PROFILE_UNCERTAINTY",
            "structural context below confidence threshold; no structural annotation applied",
        ))
    if events and not rule_versions:
        uncertainties.append(Uncertainty(
            "EVIDENCE_INCOMPLETE", "events present but rule versions unresolved",
        ))
    if channels < 2:
        uncertainties.append(Uncertainty(
            "OUT_OF_SCOPE", "stereo/phase conclusions unavailable on mono input",
        ))
    if not events and representation is None:
        uncertainties.append(Uncertainty(
            "EVIDENCE_INCOMPLETE", "no events and no representation resolved",
        ))

    classification = _classify(judgment)
    evidence_state, workflow, fail_closed = _evidence_state(
        judgment, events, uncertainties, rule_versions,
    )

    conflicts = _conflicts(judgment, source_sha256, representation, rule_versions)
    if conflicts:
        evidence_state = "CONFLICTING" if evidence_state != "INVALID" else evidence_state
        uncertainties.append(Uncertainty(
            "CONFLICTING_EVIDENCE", "; ".join(c.detail for c in conflicts[:3]),
        ))

    judgment_epistemic = (
        "UNKNOWN" if evidence_state in {"INVALID", "INSUFFICIENT"} else "INFERRED"
    )
    evidence = JudgmentEvidence(
        judgment_id=getattr(judgment, "judgment_id", "jud-1"),
        classification=classification,
        evidence_state=evidence_state,
        workflow_decision=workflow,
        nodes=tuple(nodes),
        uncertainties=tuple(uncertainties),
        conflicts=tuple(conflicts),
        coverage=coverage,
        rule_versions=rule_versions,
        epistemic_state=judgment_epistemic,
    )
    # Fail-closed: critical missing/invalid evidence suppresses PASS and
    # technical rejection (G4/G5).
    from moodify.auditory.evidence.completeness import validate_completeness

    problems = validate_completeness(evidence)
    critical = any(p.startswith("MISSING_CRITICAL") or p.startswith("INVALID_METRIC")
                   for p in problems)
    if critical:
        evidence = JudgmentEvidence(
            judgment_id=evidence.judgment_id,
            classification="UNCERTAIN",
            evidence_state="INSUFFICIENT",
            workflow_decision="INCONCLUSIVE",
            nodes=evidence.nodes,
            uncertainties=tuple(evidence.uncertainties) + (
                Uncertainty("EVIDENCE_INCOMPLETE", "; ".join(problems[:3])),
            ),
            conflicts=evidence.conflicts,
            coverage=evidence.coverage,
            rule_versions=evidence.rule_versions,
            epistemic_state="UNKNOWN",
        )
    return evidence


def _classify(judgment: Any) -> str:
    assessment = getattr(judgment, "technical_assessment", "") or ""
    decision = getattr(judgment, "workflow_decision", "") or ""
    return CLASSIFICATION_MAP.get(assessment) or CLASSIFICATION_MAP.get(decision, "UNCERTAIN")


def _evidence_state(judgment: Any, events: list[Any], uncertainties: list[Uncertainty],
                    rule_versions: dict[str, str]) -> tuple[str, str, bool]:
    """Evidence state, workflow decision and fail-closed flag.

    Fail-closed: missing critical evidence or unresolved rule versions
    cannot yield PASS_TO_LISTENING or REJECT_TECHNICAL.
    """
    blocking_events = [
        event for event in (events or [])
        if getattr(event, "event_type", "") in {"CLIPPING_CLUSTER", "NEGATIVE_CORRELATION_REGION"}
    ]
    rules_resolved = all(rule_versions.values()) if rule_versions else True
    missing_rule = bool(blocking_events) and not rules_resolved
    incomplete = any(u.reason == "EVIDENCE_INCOMPLETE" for u in uncertainties)

    if missing_rule or incomplete:
        return "INSUFFICIENT", "INCONCLUSIVE", True

    if blocking_events:
        return "SUPPORTED", "REJECT_TECHNICAL", False

    assessment = getattr(judgment, "technical_assessment", "")
    if assessment == "DEGRADED":
        return "SUPPORTED", "REJECT_TECHNICAL", False
    if assessment == "UNCERTAIN":
        return "PARTIAL", "INCONCLUSIVE", False
    return "SUPPORTED", "PASS_TO_LISTENING", False


def _conflicts(judgment: Any, source_sha256: str, representation: Any | None,
               rule_versions: dict[str, str]) -> list[Conflict]:
    conflicts: list[Conflict] = []
    if representation is not None:
        rep_hash = representation.source_sha256
        if rep_hash and rep_hash != source_sha256:
            conflicts.append(Conflict("SOURCE_LINEAGE",
                                      f"representation source {rep_hash[:8]} != judgment source {source_sha256[:8]}"))
    if getattr(judgment, "artistic_approval_granted", False):
        conflicts.append(Conflict("RULE", "machine artistic approval attempted (forbidden)"))
    return conflicts
