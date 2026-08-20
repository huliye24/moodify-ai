"""Deterministic evidence bundle (MFY-PHASE1-DEPTH-004).

Compact JSON bundle with a logical hash computed from canonical semantic
content (not container metadata). Same semantic input -> same hash.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from moodify.auditory.evidence.models import JudgmentEvidence

BUNDLE_VERSION = "evidence-bundle-v1"


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def logical_hash(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_bundle(evidence: JudgmentEvidence, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build the deterministic bundle dict (manifest + sections)."""
    # Identity fields (uuid ids) are excluded from the semantic hash so
    # identical content produces an identical logical hash (G12).
    semantic = {
        "classification": evidence.classification,
        "evidence_state": evidence.evidence_state,
        "workflow_decision": evidence.workflow_decision,
        "nodes": [
            {  # ref may carry uuid identity; scale/epistemic are semantic
                "kind": node.kind,
                "data": node.data,
                "scale": node.scale,
                "epistemic_state": node.epistemic_state,
            }
            for node in evidence.nodes
        ],
        "uncertainties": [dict(u) for u in evidence.uncertainties],
        "conflicts": [c.to_dict() for c in evidence.conflicts],
        "coverage": evidence.coverage.to_dict() if evidence.coverage else None,
        "rule_versions": dict(evidence.rule_versions),
        "epistemic_state": evidence.epistemic_state,
        **(extra or {}),
    }
    bundle = {
        "bundle_version": BUNDLE_VERSION,
        "logical_hash": logical_hash(semantic),
        "judgment": {
            "judgment_id": evidence.judgment_id,
            "classification": evidence.classification,
            "evidence_state": evidence.evidence_state,
            "workflow_decision": evidence.workflow_decision,
        },
        "coverage": semantic["coverage"],
        "uncertainties": semantic["uncertainties"],
        "conflicts": semantic["conflicts"],
        "refs": {
            "source": [n.to_dict() for n in evidence.nodes if n.kind == "SOURCE"],
            "profile": [n.to_dict() for n in evidence.nodes if n.kind == "PROFILE"],
            "measurements": [n.to_dict() for n in evidence.nodes if n.kind == "MEASUREMENT"],
            "events": [n.to_dict() for n in evidence.nodes if n.kind == "EVENT"],
            "rules": [n.to_dict() for n in evidence.nodes if n.kind == "RULE"],
        },
    }
    return bundle


def save_bundle(bundle: dict[str, Any], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
