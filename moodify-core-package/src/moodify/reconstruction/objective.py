"""Reconstruction objective layer (MFY-CR-P06, P04-absorbed).

Consumes Era Diagnostic findings that are safe for reconstruction per P03's
promotion rules (HIGH/MEDIUM consumed automatically; LOW findings may enter
only as bounded candidates in an explicit golden experiment — never as
automatic production). Produces deterministic A/B/C plans against the
existing MoodifyDSPChain parameter schema.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    FindingStatus,
)

RECONSTRUCTION_OBJECTIVE_POLICY_V1 = {
    "version": "reconstruction-objective-policy-v1",
    "schema_version": "1.0",
    "budget_class": "PROVISIONAL",
    "candidates": {
        "A": {
            "label": "A = Minimal",
            "intensity": 0.2,
            "params": {
                "P06_compression_ratio": 1.0,  # bypass always-on compressor (dynamics identity)
                "P11_reverb_dry_wet": 0.0,   # disable default 20% wet reverb (no space objective; IG-03 risk)
                "P15_high_shelf_gain": 0.5,
                "P14_high_shelf_freq": 10000.0,
            },
            "objective_refs": ["ED-01 bandwidth (LOW, bounded)"],
        },
        "B": {
            "label": "B = Balanced",
            "intensity": 0.5,
            "params": {
                "P06_compression_ratio": 1.0,
                "P11_reverb_dry_wet": 0.0,
                "P15_high_shelf_gain": 1.5,
                "P14_high_shelf_freq": 10000.0,
                "P02_vocal_presence_gain": 0.8,
                "P01_vocal_presence_freq": 3000.0,
            },
            "objective_refs": ["ED-01 bandwidth (LOW, bounded)", "vocal presence (proxy)"],
        },
        "C": {
            "label": "C = Upper Safe Boundary",
            "intensity": 1.0,
            "params": {
                "P06_compression_ratio": 1.0,
                "P11_reverb_dry_wet": 0.0,
                "P15_high_shelf_gain": 3.0,
                "P14_high_shelf_freq": 10000.0,
                "P02_vocal_presence_gain": 1.5,
                "P01_vocal_presence_freq": 3200.0,
                "P05_proximity_low_gain": 1.0,
                "P04_proximity_low_freq": 200.0,
            },
            "objective_refs": ["ED-01 bandwidth (LOW, bounded)",
                               "vocal presence (proxy)", "low-end warmth (proxy)"],
        },
    },
    "hard_gates": {
        "max_new_clipping_ratio": 0.00005,
        "max_duration_delta_s": 0.05,
        "max_loudness_delta_lufs": 3.0,
    },
}

_POLICY = RECONSTRUCTION_OBJECTIVE_POLICY_V1


def _plan_hash(params: dict[str, float]) -> str:
    payload = json.dumps(params, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def plan_from_findings(
    findings,
    *,
    source_sha256: str = "unknown",
    plan_generator_version: str = RECONSTRUCTION_OBJECTIVE_POLICY_V1["version"],
    include_low_confidence: bool = True,
) -> list[dict[str, Any]]:
    """Build deterministic A/B/C plans for the golden experiment.

    ``findings`` is the Era Diagnostic output (list of EraDiagnosticFinding).
    BYPASS decisions: findings with status LIKELY_ARTISTIC_CHARACTER or
    NOT_APPLICABLE never appear in objective refs; ED-06 (NOT_SUPPORTED)
    produces no objective. SOURCE is always plan #0.

    ``include_low_confidence=False`` applies P04 production semantics:
    LOW-confidence findings never authorise candidates; when no safe finding
    remains, only the SOURCE plan is produced (BYPASS on weak evidence).
    The golden experiment keeps the default (bounded candidates).
    """
    safe_refs: list[str] = []
    for f in findings:
        if f.status not in {
            FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
            FindingStatus.OBSERVED,
        }:
            continue
        if f.category == DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION:
            continue  # no validated detector -> no objective
        if not include_low_confidence and f.category == DiagnosticCategory.ED_02_PERSISTENT_NOISE:
            continue  # NOISE_REDUCTION unsupported in v0.1 engine (P04)
        if not include_low_confidence and f.confidence == ConfidenceLevel.LOW:
            continue  # diagnosis != authorisation on weak evidence (P04)
        safe_refs.append(f"{f.category.value}:{f.status.value}:{f.confidence.value if f.confidence else '-'}")

    plans: list[dict[str, Any]] = [{
        "candidate_id": "SOURCE",
        "label": "SOURCE",
        "intensity": 0.0,
        "params": {},
        "objective_refs": [],
        "plan_hash": "source",
    }]
    if not safe_refs and not include_low_confidence:
        return plans  # BYPASS: no authorised objective
    for candidate_id, cfg in _POLICY["candidates"].items():
        params = dict(cfg["params"])
        plans.append({
            "candidate_id": candidate_id,
            "label": cfg["label"],
            "intensity": cfg["intensity"],
            "params": params,
            "objective_refs": cfg["objective_refs"] + safe_refs,
            "plan_hash": _plan_hash(params),
        })
    return plans
