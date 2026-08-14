"""Authority scope contracts — the explicit authorization boundary for
deterministic machine judgment.

Every rule/reviewer that may *decide* (not merely report) must be covered by a
ScopeContract. "The algorithm runs" never substitutes for "the algorithm is
authorized to decide" (MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date

SCOPE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ScopeContract:
    """Approved decision scope for one rule/reviewer.

    All fields must be filled; an empty or partial contract is not an
    authorization.
    """

    reviewer_id: str
    reviewer_version: str
    input_profile: str
    metric_versions: tuple[str, ...]
    allowed_audio: tuple[str, ...] = ("wav", "flac")  # format conditions
    min_duration_s: float = 1.0
    max_duration_s: float = 1800.0
    max_channels: int = 2
    min_evidence_completeness: float = 1.0  # 1.0 = all required artifacts present
    thresholds_calibrated_from: str = "2026-08 calibration run (locked)"
    allowed_judgment_outputs: tuple[str, ...] = ("MACHINE_DECIDED",)
    forbidden_conditions: tuple[str, ...] = (
        "perceptual preference", "artistic quality", "copyright conclusion",
    )
    known_limits: str = "single-profile; dense AI mixes may reduce cepstral reliability"
    expires_on: date | None = None
    revoked_on: date | None = None

    @property
    def contract_id(self) -> str:
        digest = hashlib.sha256(
            "|".join([
                self.reviewer_id, self.reviewer_version, self.input_profile,
                ",".join(self.metric_versions),
            ]).encode("utf-8"),
        ).hexdigest()[:16]
        return f"SCOPE-{self.reviewer_id}-{digest}"

    def is_active(self, today: date | None = None) -> bool:
        today = today or date.today()
        if self.revoked_on is not None and today >= self.revoked_on:
            return False
        if self.expires_on is not None and today >= self.expires_on:
            return False
        return True


# The single approved algorithmic decision scope (D-002 boundary). Any change
# to profile/metric versions/thresholds requires a new version + human review.
ALGORITHMIC_REVIEW_SCOPE = ScopeContract(
    reviewer_id="MFY-ALGORITHMIC-REVIEW-001",
    reviewer_version="v1.0",
    input_profile="MFY-WSE-SCAN-PROFILE-001",
    metric_versions=("WSE-PROFILE-001",),
    allowed_audio=("wav", "flac"),
    min_duration_s=1.0,
    max_duration_s=1800.0,
    max_channels=2,
    min_evidence_completeness=1.0,
    thresholds_calibrated_from="2026-08 pilot calibration (MFY-ALGORITHMIC-REVIEW-001)",
    allowed_judgment_outputs=("MACHINE_DECIDED",),
    forbidden_conditions=("perceptual preference", "artistic quality", "copyright conclusion"),
    known_limits=("dense AI mixes reduce cepstral reliability; threshold drift "
                  "not recalibrated before September 2026"),
    expires_on=None,
    revoked_on=None,
)

REGISTRY: dict[str, ScopeContract] = {
    ALGORITHMIC_REVIEW_SCOPE.reviewer_id: ALGORITHMIC_REVIEW_SCOPE,
}


def get_contract(reviewer_id: str) -> ScopeContract | None:
    return REGISTRY.get(reviewer_id)
