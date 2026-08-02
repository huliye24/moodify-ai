"""Training eligibility and rights governance (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Eligibility defaults safely: UNKNOWN / PENDING_REVIEW, never ELIGIBLE.
A technically complete case may still be ineligible for model training.
"""

from __future__ import annotations

from moodify.learning.errors import TrainingEligibilityUnknown
from moodify.learning.models import RightsMetadata

# A rights field counts as an explicit grant only for these values.
_GRANT = {"YES", "TRUE", "AUTHORIZED", "GRANTED", "CONSENTED"}
_DENY = {"NO", "FALSE", "DENIED", "REVOKED"}


def compute_eligibility(rights: RightsMetadata) -> tuple[str, list[str]]:
    """Derive training eligibility from rights metadata.

    Returns (eligibility, exclusion_reasons). Never returns ELIGIBLE unless
    every training-relevant authorization is explicitly granted.
    """
    reasons: list[str] = []

    if rights.model_training_authorized.strip().upper() in _DENY:
        return "INELIGIBLE", ["model_training_authorized denied"]
    if rights.commercial_training_authorized.strip().upper() in _DENY:
        return "INELIGIBLE", ["commercial_training_authorized denied"]
    if rights.derivative_data_authorized.strip().upper() in _DENY:
        return "INELIGIBLE", ["derivative_data_authorized denied"]
    if rights.rights_holder == "UNKNOWN" or not rights.rights_holder.strip():
        return "PENDING_REVIEW", ["rights_holder unknown"]

    required = {
        "model_training_authorized": rights.model_training_authorized,
        "derivative_data_authorized": rights.derivative_data_authorized,
        "research_use_authorized": rights.research_use_authorized,
        "processing_authorization": rights.processing_authorization,
    }
    for field, value in required.items():
        if value.strip().upper() not in _GRANT:
            reasons.append(f"{field} not explicitly granted ({value or 'UNKNOWN'})")
    if reasons:
        return "PENDING_REVIEW", reasons

    if not rights.reviewed_by.strip():
        reasons.append("no rights review recorded")
        return "PENDING_REVIEW", reasons

    return "ELIGIBLE", []


def assert_eligibility_granted(eligibility: str, reasons: list[str] | None = None) -> None:
    if eligibility != "ELIGIBLE":
        raise TrainingEligibilityUnknown(
            f"training eligibility is {eligibility}; reasons: {reasons or []}",
            operation="dataset_export",
            recoverable=True,
        )
