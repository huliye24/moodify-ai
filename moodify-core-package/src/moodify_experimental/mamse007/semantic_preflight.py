"""Semantic preflight for PCA feature selection.

Verifies each feature's implementation semantics against the expected
registry semantics BEFORE any basis fit. Conflicting features are excluded
from the basis with a reason. v0.1 ships a versioned rule table with the
two known repo blockers; canonical definitions are NOT modified here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Versioned knowledge of canonical feature semantics. Rules are checked by
# feature name; registry_id is what the canonical registry claims.
# Reason codes:
#   IMPL_IS_LINEAR_ENERGY_NOT_RATIO  -> S1 mid/side energy blocker
#   IMPL_IS_RMS_PROXY_NOT_LUFS       -> S2 short_term_lufs blocker
#   UNIT_UNRESOLVED                  -> no confirmed semantics (Risk D)
DEFAULT_SEMANTIC_RULES: dict[str, dict[str, Any]] = {
    "mid_energy": {
        "registry_id": "mid_energy_ratio",
        "registry_unit": "ratio",
        "registry_authority_class": "STANDARD",
        "implementation_semantics": "linear mean-square energy",
        "expected_semantics": "mid energy / total energy (ratio)",
        "status": "SEMANTIC_CONFLICT",
        "reason": "IMPL_IS_LINEAR_ENERGY_NOT_RATIO",
    },
    "side_energy": {
        "registry_id": "side_energy_ratio",
        "registry_unit": "ratio",
        "registry_authority_class": "STANDARD",
        "implementation_semantics": "linear mean-square energy",
        "expected_semantics": "side energy / total energy (ratio)",
        "status": "SEMANTIC_CONFLICT",
        "reason": "IMPL_IS_LINEAR_ENERGY_NOT_RATIO",
    },
    "short_term_lufs": {
        "registry_id": "integrated_lufs",
        "registry_unit": "LUFS",
        "registry_authority_class": "STANDARD_COMPLIANT",
        "implementation_semantics": "RMS dB level proxy (K-weighting deferred)",
        "expected_semantics": "K-weighted gated LUFS",
        "status": "SEMANTIC_CONFLICT",
        "reason": "IMPL_IS_RMS_PROXY_NOT_LUFS",
    },
}


@dataclass(frozen=True)
class FeatureSemanticRecord:
    feature_name: str
    registry_metric_id: str | None
    registry_unit: str | None
    registry_authority_class: str | None
    implementation_semantics: str | None
    expected_semantics: str | None
    status: str  # OK | SEMANTIC_CONFLICT | UNRESOLVED
    reason: str | None

    def to_dict(self) -> dict:
        return {
            "feature_name": self.feature_name,
            "registry_metric_id": self.registry_metric_id,
            "registry_unit": self.registry_unit,
            "registry_authority_class": self.registry_authority_class,
            "implementation_semantics": self.implementation_semantics,
            "expected_semantics": self.expected_semantics,
            "status": self.status,
            "reason": self.reason,
        }


def preflight_features(
    feature_names: tuple[str, ...],
    *,
    known_conflicts: dict[str, dict[str, Any]] | None = None,
) -> list[FeatureSemanticRecord]:
    """Evaluate semantics for each feature.

    `known_conflicts` defaults to DEFAULT_SEMANTIC_RULES (the audited repo
    blockers). Features without a rule are UNRESOLVED (unit not confirmed),
    which blocks them from a frozen corpus basis unless explicitly allowed.
    """
    rules = known_conflicts if known_conflicts is not None else DEFAULT_SEMANTIC_RULES
    records: list[FeatureSemanticRecord] = []
    for name in feature_names:
        rule = rules.get(name)
        if rule is None:
            records.append(FeatureSemanticRecord(
                feature_name=name, registry_metric_id=None, registry_unit=None,
                registry_authority_class=None, implementation_semantics=None,
                expected_semantics=None, status="UNRESOLVED", reason="UNIT_UNRESOLVED",
            ))
            continue
        records.append(FeatureSemanticRecord(
            feature_name=name,
            registry_metric_id=rule["registry_id"],
            registry_unit=rule["registry_unit"],
            registry_authority_class=rule["registry_authority_class"],
            implementation_semantics=rule["implementation_semantics"],
            expected_semantics=rule["expected_semantics"],
            status=rule["status"],
            reason=rule.get("reason"),
        ))
    return records


def basis_eligible_feature_names(
    records: list[FeatureSemanticRecord],
    *,
    allow_unresolved: bool = False,
) -> tuple[tuple[str, ...], tuple[dict, ...]]:
    """Return (retained names, dropped records) after semantic gating.

    SEMANTIC_CONFLICT always excluded. UNRESOLVED excluded unless explicitly
    allowed (research exploratory path only; never for a frozen basis).
    """
    retained: list[str] = []
    dropped: list[dict] = []
    for r in records:
        if r.status == "OK":
            retained.append(r.feature_name)
        elif r.status == "SEMANTIC_CONFLICT":
            dropped.append({"feature": r.feature_name, "reason": r.reason, "status": r.status})
        elif r.status == "UNRESOLVED" and allow_unresolved:
            retained.append(r.feature_name)
            dropped.append({"feature": r.feature_name, "reason": "UNIT_UNRESOLVED_ALLOWED_EXPLORATORY"})
        else:
            dropped.append({"feature": r.feature_name, "reason": r.reason, "status": r.status})
    return tuple(retained), tuple(dropped)
