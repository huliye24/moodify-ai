"""Quarterly freeze guards (core/Ear) — MFY_QUARTERLY_RELEASE_FREEZE_001.

Machine checks that Ear authority surfaces did not drift: job status enum,
case authority enum, the approved decision scope contract, and the public
product version string.
"""

from __future__ import annotations

from moodify.contracts.production_case import AuthorityState, LifecycleState
from moodify.node.models import JobStatus
from moodify.authority.scope_contract import ALGORITHMIC_REVIEW_SCOPE, REGISTRY


def test_job_status_enumeration_is_frozen():
    assert {s.value for s in JobStatus} == {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED"}


def test_case_authority_enumeration_is_frozen():
    assert {s.value for s in AuthorityState} == {
        "SYSTEM", "ALGORITHM", "HUMAN_REQUIRED", "HUMAN_APPROVED", "HUMAN_REJECTED",
    }
    assert {s.value for s in LifecycleState} == {
        "CREATED", "ACTIVE", "AWAITING_HUMAN", "COMPLETED", "FAILED", "CANCELLED",
    }


def test_approved_decision_scope_is_frozen():
    contract = ALGORITHMIC_REVIEW_SCOPE
    assert contract.reviewer_id == "MFY-ALGORITHMIC-REVIEW-001"
    assert contract.reviewer_version == "v1.0"
    assert contract.input_profile == "MFY-WSE-SCAN-PROFILE-001"
    assert contract.is_active()
    assert REGISTRY["MFY-ALGORITHMIC-REVIEW-001"] is contract
    assert contract.allowed_judgment_outputs == ("MACHINE_DECIDED",)


def test_product_version_string_is_stable():
    from moodify.release import PRODUCT_VERSION

    assert PRODUCT_VERSION == "1.0.0-rc.1"
