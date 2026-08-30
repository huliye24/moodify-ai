"""Deterministic state machine for contribution lifecycle management."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from .validate import ValidationError


class ContributionStatus(Enum):
    """Contribution lifecycle states."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"
    REJECTED = "rejected"
    VERIFIED = "verified"
    SCORED = "scored"
    FINALIZED = "finalized"


class TransitionNotAllowedError(Exception):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, from_status: str, to_status: str, reason: str):
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason
        super().__init__(
            f"Cannot transition from '{from_status}' to '{to_status}': {reason}"
        )


class StateMachine:
    """Deterministic state machine for contribution records."""

    # Define allowed transitions
    ALLOWED_TRANSITIONS = {
        ContributionStatus.DRAFT: [ContributionStatus.SUBMITTED],
        ContributionStatus.SUBMITTED: [ContributionStatus.UNDER_REVIEW],
        ContributionStatus.UNDER_REVIEW: [
            ContributionStatus.REJECTED,
            ContributionStatus.NEEDS_MORE_EVIDENCE,
            ContributionStatus.VERIFIED
        ],
        ContributionStatus.NEEDS_MORE_EVIDENCE: [ContributionStatus.UNDER_REVIEW],
        ContributionStatus.REJECTED: [],  # Immutable once rejected
        ContributionStatus.VERIFIED: [ContributionStatus.SCORED],
        ContributionStatus.SCORED: [ContributionStatus.FINALIZED],
        ContributionStatus.FINALIZED: []  # Immutable once finalized
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Check if a state transition is allowed.

        Args:
            from_status: Current status (string)
            to_status: Target status (string)

        Returns:
            True if transition is allowed
        """
        try:
            from_enum = ContributionStatus(from_status)
            to_enum = ContributionStatus(to_status)
            return to_enum in cls.ALLOWED_TRANSITIONS[from_enum]
        except ValueError:
            return False

    @classmethod
    def validate_transition(cls, from_status: str, to_status: str, record_data: Dict[str, Any] = None) -> None:
        """Validate a state transition with business rules.

        Args:
            from_status: Current status
            to_status: Target status
            record_data: Full contribution record for additional validation

        Raises:
            TransitionNotAllowedError: If transition is invalid
        """
        if not cls.can_transition(from_status, to_status):
            raise TransitionNotAllowedError(
                from_status, to_status, "Transition not in allowed transitions"
            )

        # Additional business rule validations
        if from_status == ContributionStatus.DRAFT.value and to_status != ContributionStatus.SUBMITTED.value:
            raise TransitionNotAllowedError(
                from_status, to_status, "Draft can only transition to submitted"
            )

        if from_status == ContributionStatus.UNDER_REVIEW.value:
            # Check if review reason is provided for certain transitions
            if to_status in [ContributionStatus.REJECTED, ContributionStatus.NEEDS_MORE_EVIDENCE]:
                if record_data and not record_data.get('review'):
                    raise TransitionNotAllowedError(
                        from_status, to_status, "Review field required for rejection or evidence request"
                    )

        if to_status == ContributionStatus.SCORED.value:
            # Can only score verified records
            if from_status != ContributionStatus.VERIFIED.value:
                raise TransitionNotAllowedError(
                    from_status, to_status, "Only verified records can be scored"
                )

            # Check if scores field exists
            if record_data and not record_data.get('scores'):
                raise TransitionNotAllowedError(
                    from_status, to_status, "Scores field required for scored status"
                )

        if to_status == ContributionStatus.FINALIZED.value:
            # Check if scores exist and are complete
            if record_data and not record_data.get('scores'):
                raise TransitionNotAllowedError(
                    from_status, to_status, "Scores required before finalization"
                )

    def apply_transition(self, record: Dict[str, Any], target_status: str, review_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Apply a state transition to a contribution record.

        Args:
            record: The contribution record
            target_status: Target status
            review_data: Optional review data (for transitions that require it)

        Returns:
            Updated contribution record
        """
        current_status = record.get('status', 'draft')

        # Validate the transition
        self.validate_transition(current_status, target_status, record)

        # Create a copy to avoid modifying the original
        updated_record = record.copy()

        # Apply the transition
        updated_record['status'] = target_status
        updated_record['policyVersion'] = record.get('policyVersion', 'unknown')

        # Handle review data for certain transitions
        if review_data is not None:
            if 'metadata' not in updated_record:
                updated_record['metadata'] = {}
            if 'review' not in updated_record['metadata']:
                updated_record['metadata']['review'] = {}

            # Handle both regular review and final review
            if 'finalReviewer' in review_data:
                # This is a final review
                final_review = {
                    'finalReviewer': review_data['finalReviewer'],
                    'finalDate': review_data['finalDate'],
                    'finalDecision': review_data['finalDecision']
                }
                if 'appliedAt' in review_data:
                    final_review['appliedAt'] = review_data['appliedAt']
                updated_record['metadata']['review'] = final_review
            else:
                # This is a regular review
                regular_review = {
                    'reviewer': review_data['reviewer'],
                    'reviewDate': review_data['reviewDate']
                }
                if 'score' in review_data:
                    regular_review['score'] = review_data['score']
                if 'feedback' in review_data:
                    regular_review['feedback'] = review_data['feedback']
                if 'recommendation' in review_data:
                    regular_review['recommendation'] = review_data['recommendation']
                if 'appliedAt' in review_data:
                    regular_review['appliedAt'] = review_data['appliedAt']
                updated_record['metadata']['review'] = regular_review

        # Handle immutable fields after certain transitions
        if target_status in ['rejected', 'finalized']:
            # Mark as immutable
            if 'metadata' not in updated_record:
                updated_record['metadata'] = {}
            updated_record['metadata']['immutable'] = True
            updated_record['metadata']['finalizedAt'] = datetime.utcnow().isoformat()

        return updated_record

    def get_allowed_transitions(self, from_status: str) -> List[str]:
        """Get all allowed target states from a given state.

        Args:
            from_status: Current status

        Returns:
            List of allowed target statuses
        """
        try:
            from_enum = ContributionStatus(from_status)
            return [status.value for status in self.ALLOWED_TRANSITIONS[from_enum]]
        except ValueError:
            return []

    def is_terminal_state(self, status: str) -> bool:
        """Check if a status is a terminal (immutable) state.

        Args:
            status: Status to check

        Returns:
            True if terminal state
        """
        return status in [ContributionStatus.REJECTED.value, ContributionStatus.FINALIZED.value]