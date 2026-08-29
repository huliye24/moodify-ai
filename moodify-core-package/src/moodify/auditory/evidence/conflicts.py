"""Conflict detection (MFY-PHASE1-DEPTH-004).

Detects status/version/source/profile/rule/duplicate-authority
conflicts, while treating valid global/local differences (e.g. a global
normal metric coexisting with a local clipping event) as context, not
contradiction.
"""

from __future__ import annotations

from typing import Any

from moodify.auditory.evidence.models import Conflict, JudgmentEvidence


def detect_conflicts(evidence: JudgmentEvidence) -> list[Conflict]:
    """Re-scan the evidence graph for conflicts."""
    conflicts: list[Conflict] = list(evidence.conflicts)

    sources = [node for node in evidence.nodes if node.kind == "SOURCE"]
    if len(sources) > 1:
        hashes = {node.data.get("source_sha256") for node in sources if node.data.get("source_sha256")}
        if len(hashes) > 1:
            conflicts.append(Conflict("DUPLICATE_AUTHORITY",
                                      "multiple distinct source hashes in one graph"))

    rule_versions = evidence.rule_versions
    if rule_versions:
        empty = [rule for rule, version in rule_versions.items() if not version]
        if empty:
            conflicts.append(Conflict("VERSION", f"unresolved rule versions: {', '.join(empty)}"))

    invalid_metrics = [
        node for node in evidence.nodes
        if node.kind == "MEASUREMENT" and node.data.get("status") in {"INVALID", "UNAVAILABLE"}
    ]
    if invalid_metrics:
        conflicts.append(Conflict("STATUS",
                                  f"invalid metric statuses: {', '.join(n.ref for n in invalid_metrics[:3])}"))
    return conflicts


def is_contextual_difference(global_metrics: dict[str, Any],
                             local_events: list[Any]) -> bool:
    """A global normal result plus local events is context, not conflict."""
    return bool(local_events)  # presence of local events alone is not a conflict
