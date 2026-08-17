"""Rights / consent gate (MFY-CR-P07).

Processing data != training data != user private data. Training permission
DEFAULTS to NO and public demo DEFAULTS to NO unless explicitly granted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RightsRecord:
    rights_status: str  # OWNED / AUTHORIZED / INTERNAL_TEST_ALLOWED / OTHER
    processing_permission: bool
    training_permission: bool = False
    retention_policy: str = "internal_research_only"
    public_demo_permission: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def default_rights(rights_status: str = "INTERNAL_TEST_ALLOWED") -> RightsRecord:
    """Conservative default: processing allowed, training and public demo NO."""
    return RightsRecord(
        rights_status=rights_status,
        processing_permission=True,
        training_permission=False,
        retention_policy="internal_research_only",
        public_demo_permission=False,
    )


def validate_rights(record: RightsRecord) -> tuple[bool, str]:
    """Gate: no record may imply training/public permission without explicit grant."""
    if record.rights_status not in ("OWNED", "AUTHORIZED", "INTERNAL_TEST_ALLOWED"):
        return False, f"rights_status {record.rights_status} not allowed"
    if not record.processing_permission:
        return False, "processing_permission must be True to run reconstruction"
    if record.training_permission and record.rights_status == "INTERNAL_TEST_ALLOWED":
        return False, "INTERNAL_TEST_ALLOWED cannot grant training_permission"
    return True, "ok"
