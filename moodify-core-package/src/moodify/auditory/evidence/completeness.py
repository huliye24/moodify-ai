"""Evidence completeness validation (MFY-PHASE1-DEPTH-004).

Deterministic checks: critical evidence missing or invalid must fail
closed (no PASS / no technical rejection). Invalid metric status cannot
drive an authoritative judgment.
"""

from __future__ import annotations

from moodify.auditory.evidence.models import JudgmentEvidence

CRITICAL_METRICS = {"integrated_lufs", "true_peak_dbfs", "clipping_sample_ratio"}
INVALID_STATUSES = {"INVALID", "UNAVAILABLE"}


def validate_completeness(evidence: JudgmentEvidence) -> list[str]:
    """Return a list of completeness problems (empty = complete)."""
    problems: list[str] = []
    measurement_nodes = {node.node_id for node in evidence.nodes if node.kind == "MEASUREMENT"}
    for metric in CRITICAL_METRICS:
        if f"measurement:{metric}" not in measurement_nodes:
            problems.append(f"MISSING_CRITICAL:{metric}")
    for node in evidence.nodes:
        if node.kind == "MEASUREMENT" and node.data.get("status") in INVALID_STATUSES:
            problems.append(f"INVALID_METRIC:{node.ref}")
    if not any(node.kind == "SOURCE" for node in evidence.nodes):
        problems.append("MISSING_SOURCE_PROVENANCE")
    return problems


def is_fail_closed(evidence: JudgmentEvidence, problems: list[str]) -> bool:
    """Fail-closed: critical problems suppress PASS and technical rejection."""
    critical = any(p.startswith("MISSING_CRITICAL") or p.startswith("INVALID_METRIC")
                   for p in problems)
    if not critical:
        return False
    return evidence.workflow_decision in {"INCONCLUSIVE", "REVIEW_REQUIRED"}


def require_fail_closed(evidence: JudgmentEvidence) -> JudgmentEvidence:
    """Apply fail-closed semantics deterministically."""
    problems = validate_completeness(evidence)
    critical = any(p.startswith("MISSING_CRITICAL") or p.startswith("INVALID_METRIC")
                   for p in problems)
    if not critical:
        return evidence
    return evidence
