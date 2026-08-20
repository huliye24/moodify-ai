"""Versioned intervention registry (MFY_PRESERVE_IDENTITY_INTERVENTION_001).

The registry is the pre-registration contract: primitives are declared with
scope, max strength, identity risk, failure state and default enablement
BEFORE any case runs. "Processing more" is never a success metric.
"""

from __future__ import annotations

import json
from typing import Any

from moodify.intervention.primitives import PRIMITIVES
from moodify.intervention.pipeline import INTERVENTION_VERSION


def build_registry() -> dict[str, Any]:
    """Machine-readable registry: contracts + version."""
    primitives = []
    for pid in sorted(PRIMITIVES):
        p = PRIMITIVES[pid]
        c = p.contract
        primitives.append(
            {
                "primitive_id": c.primitive_id,
                "version": c.version,
                "scope": c.scope,
                "max_strength": c.max_strength,
                "identity_risk": c.identity_risk,
                "failure_state": c.failure_state,
                "default_enabled": c.default_enabled,
                "notes": c.notes,
            }
        )
    return {
        "schema": "intervention-registry-v1",
        "package": "MFY_PRESERVE_IDENTITY_INTERVENTION_001",
        "pipeline_version": INTERVENTION_VERSION,
        "principle": "pre-registered conservative candidates; processing more is not success; identity gate before selection; HUMAN_REQUIRED on uncertainty",
        "primitives": primitives,
    }


def export_registry_json(path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(build_registry(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
