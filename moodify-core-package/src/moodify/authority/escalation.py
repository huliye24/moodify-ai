"""Escalation judgment — decides MACHINE_DECIDED / HUMAN_REQUIRED /
INCONCLUSIVE / FAILED for a case before any machine verdict may stand.

Covers the mandatory escalation reasons (MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001 §2):
- input outside the validated distribution or profile mismatch
- missing metrics / unknown implementation version / incomplete manifest
- conflicting rules
- confidence/uncertainty beyond the approved threshold
- verification invariant failure
- artistic/contextual/uncalibrated perceptual conclusion
- user-requested human review
- suspended or revoked rule

Unified machine-parseable outcomes; free text never substitutes for the state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from moodify.authority.scope_contract import get_contract

MACHINE_DECIDED = "MACHINE_DECIDED"
HUMAN_REQUIRED = "HUMAN_REQUIRED"
INCONCLUSIVE = "INCONCLUSIVE"
FAILED = "FAILED"

_OUTCOMES = (MACHINE_DECIDED, HUMAN_REQUIRED, INCONCLUSIVE, FAILED)


@dataclass(frozen=True)
class EscalationRecord:
    outcome: str
    reasons: tuple[str, ...] = ()
    details: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "schema_version": "1.0",
            "outcome": self.outcome,
            "reasons": list(self.reasons),
            "details": self.details,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_scope(manifest: dict | None) -> EscalationRecord | None:
    """Check the authority scope contract against the case manifest.

    Returns None when the machine may decide; otherwise an escalation record
    whose outcome is one of HUMAN_REQUIRED / INCONCLUSIVE / FAILED.
    """
    if not manifest:
        return EscalationRecord(FAILED, ("EVIDENCE_MANIFEST_MISSING",), {"detail": "no case manifest to verify scope"})
    contract = get_contract(manifest.get("reviewer_id", "MFY-ALGORITHMIC-REVIEW-001"))
    if contract is None:
        return EscalationRecord(HUMAN_REQUIRED, ("SCOPE_CONTRACT_UNKNOWN",), {"reviewer_id": manifest.get("reviewer_id")})
    if not contract.is_active():
        return EscalationRecord(HUMAN_REQUIRED, ("SCOPE_CONTRACT_SUSPENDED_OR_EXPIRED",), {"contract_id": contract.contract_id})

    reasons: list[str] = []
    details: dict = {}

    profile = manifest.get("scan_profile") or manifest.get("profile")
    if profile != contract.input_profile:
        reasons.append("PROFILE_MISMATCH")
        details["profile"] = profile
        details["expected_profile"] = contract.input_profile

    versions = manifest.get("metric_versions") or ()
    if contract.metric_versions and not versions:
        reasons.append("METRIC_VERSION_UNKNOWN")
        details["metric_versions"] = versions

    source = manifest.get("source") or {}
    fmt = (source.get("format") or manifest.get("source_format") or "").lower()
    if fmt and fmt not in contract.allowed_audio:
        reasons.append("AUDIO_FORMAT_OUT_OF_SCOPE")
        details["format"] = fmt

    if "duration_s" in manifest:
        duration = float(manifest["duration_s"])
        if duration < contract.min_duration_s or duration > contract.max_duration_s:
            reasons.append("DURATION_OUT_OF_SCOPE")
            details["duration_s"] = duration

    if "channels" in manifest:
        channels = int(manifest["channels"])
        if channels > contract.max_channels:
            reasons.append("CHANNELS_OUT_OF_SCOPE")
            details["channels"] = channels

    evidence_ids = manifest.get("evidence_ids") or ()
    required = getattr(manifest, "required_evidence", None)
    if required and len(evidence_ids) < contract.min_evidence_completeness * len(required):
        reasons.append("EVIDENCE_INCOMPLETE")
        details["evidence_count"] = len(evidence_ids)

    if reasons:
        return EscalationRecord(HUMAN_REQUIRED, tuple(reasons), details)
    return None


def evaluate_verification(case_dir: "object | None" = None, comparison_ok: bool | None = None, invariant_failures: list[str] | None = None) -> EscalationRecord | None:
    """Verification invariant failures block machine success (fail closed)."""
    if invariant_failures:
        return EscalationRecord(FAILED, ("VERIFICATION_INVARIANT_FAILED",), {"invariant_failures": invariant_failures})
    if comparison_ok is False:
        return EscalationRecord(INCONCLUSIVE, ("VERIFICATION_NOT_ESTABLISHED",), {})
    return None


def user_requested_review(case_id: str, reason: str) -> EscalationRecord:
    return EscalationRecord(HUMAN_REQUIRED, ("USER_REQUESTED_REVIEW",), {"case_id": case_id, "reason": reason[:500]})


def perceptual_or_copyright_conclusion(conclusion: str) -> EscalationRecord:
    return EscalationRecord(HUMAN_REQUIRED, ("PERCEPTUAL_OR_COPYRIGHT_CONCLUSION",), {"conclusion": conclusion[:300]})


def conflicting_rules(rule_ids: list[str]) -> EscalationRecord:
    return EscalationRecord(INCONCLUSIVE, ("RULES_CONFLICT",), {"rule_ids": rule_ids})


def confidence_beyond_threshold(confidence: float, threshold: float) -> EscalationRecord:
    return EscalationRecord(HUMAN_REQUIRED, ("CONFIDENCE_OUTSIDE_APPROVED_THRESHOLD",), {"confidence": confidence, "threshold": threshold})
