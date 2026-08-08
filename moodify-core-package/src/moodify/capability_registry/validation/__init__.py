"""Capability validation — execution success is not production success.

Each ValidationRule carries a historical_source: the failure that made the
rule a necessary boundary (geological record, POSC-003). Rules cannot be
disabled by providers; error-level failures reject the candidate. Rejected
candidates and reasons are first-class negative knowledge.
"""

from moodify.capability_registry.validation.rules import (
    RuleResult,
    ValidationReport,
    ValidationRule,
    common_rules,
    rules_for_capability,
)
from moodify.capability_registry.validation.candidates import (
    Candidate,
    CandidateRanker,
    CandidateSpec,
    RejectionReason,
)

__all__ = [
    "Candidate",
    "CandidateRanker",
    "CandidateSpec",
    "RejectionReason",
    "RuleResult",
    "ValidationReport",
    "ValidationRule",
    "common_rules",
    "rules_for_capability",
]
