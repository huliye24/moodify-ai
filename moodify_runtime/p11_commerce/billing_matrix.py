# MFY-CR-P11 — Outcome Billing Matrix
"""
Core billing principle:
  > No useful private playable result -> no reconstruction charge.

This module maps ReconstructionOutcome -> BillingDecision.
Server authoritative. Android never decides billing.
"""

from __future__ import annotations

from typing import Optional, Tuple

from .models import (
    BillingDecision,
    ReconstructionOutcome,
)


# ---------------------------------------------------------------------------
# Billing Matrix: outcome -> decision
# ---------------------------------------------------------------------------

BILLING_MATRIX: dict[ReconstructionOutcome, BillingDecision] = {
    ReconstructionOutcome.SUCCEEDED:           BillingDecision.CHARGE,
    ReconstructionOutcome.SOURCE_WINS:         BillingDecision.NO_CHARGE,
    ReconstructionOutcome.HUMAN_REQUIRED:      BillingDecision.NO_CHARGE_YET,
    ReconstructionOutcome.TECHNICAL_FAILED:    BillingDecision.NO_CHARGE,
    ReconstructionOutcome.UNSUPPORTED:         BillingDecision.NO_CHARGE,
    ReconstructionOutcome.ENCRYPTION_FAILED:   BillingDecision.NO_CHARGE,
    ReconstructionOutcome.PLAYBACK_VERIFY_FAILED: BillingDecision.NO_CHARGE,
}


def resolve_billing(outcome: ReconstructionOutcome) -> BillingDecision:
    """Determine billing decision from reconstruction outcome.

    Args:
        outcome: The final reconstruction job outcome.

    Returns:
        BillingDecision — CHARGE / NO_CHARGE / NO_CHARGE_YET
    """
    return BILLING_MATRIX.get(outcome, BillingDecision.NO_CHARGE)


def is_billable(outcome: ReconstructionOutcome) -> bool:
    """Quick check: should this outcome result in a charge?"""
    return resolve_billing(outcome) == BillingDecision.CHARGE


# ---------------------------------------------------------------------------
# Settlement Gate (v0.1)
# ---------------------------------------------------------------------------

# Billable definition v0.1:
#   BILLABLE = selected_result != SOURCE
#           AND job_success
#           AND private_object_finalized
#           AND playback_verification_pass

class SettlementGate:
    """Gate that must be passed before settlement can occur.

    All four conditions must be TRUE simultaneously:
      1. billable outcome (SUCCEEDED)
      2. PrivateAudioObject is FINALIZED
      3. Playback verification PASSED
      4. Payment state is valid (AUTHORIZED or equivalent)
    """

    @staticmethod
    def check(
        outcome: Optional[ReconstructionOutcome],
        private_object_finalized: bool,
        playback_verified: bool,
        payment_authorized: bool,
    ) -> Tuple[bool, str]:
        """Evaluate whether settlement is allowed.

        Returns:
            (allowed: bool, reason: str)
        """
        if outcome is None:
            return False, "No outcome determined yet"

        # No-charge outcomes can settle immediately without strict gates
        if outcome in (
            ReconstructionOutcome.SOURCE_WINS,
            ReconstructionOutcome.TECHNICAL_FAILED,
            ReconstructionOutcome.UNSUPPORTED,
            ReconstructionOutcome.ENCRYPTION_FAILED,
            ReconstructionOutcome.PLAYBACK_VERIFY_FAILED,
        ):
            return True, f"{outcome.value} — no charge settlement"

        if outcome == ReconstructionOutcome.HUMAN_REQUIRED:
            return False, "HUMAN_REQUIRED — pending approval, no premature settlement"

        # SUCCEEDED path — strict gate: all conditions must pass
        if not payment_authorized:
            return False, "Payment not authorized"

        if not private_object_finalized:
            return False, "PrivateAudioObject not yet finalized"

        if not playback_verified:
            return False, "Playback verification not yet passed"

        return True, "All gates passed — CHARGE settlement authorized"


def can_settle(
    outcome: Optional[ReconstructionOutcome],
    private_object_finalized: bool = False,
    playback_verified: bool = False,
    payment_authorized: bool = False,
) -> bool:
    """Convenience function: can this order be settled?"""
    allowed, _ = SettlementGate.check(
        outcome, private_object_finalized, playback_verified, payment_authorized
    )
    return allowed


def get_settlement_blockers(
    outcome: Optional[ReconstructionOutcome],
    private_object_finalized: bool = False,
    playback_verified: bool = False,
    payment_authorized: bool = False,
) -> list:
    """Return list of unmet conditions for debugging."""
    blockers = []

    if outcome is None:
        blockers.append("No outcome")
    elif outcome == ReconstructionOutcome.SUCCEEDED:
        if not private_object_finalized:
            blockers.append("PrivateAudioObject not finalized")
        if not playback_verified:
            blockers.append("Playback not verified")
        if not payment_authorized:
            blockers.append("Payment not authorized")
    elif outcome in (
        ReconstructionOutcome.SOURCE_WINS,
        ReconstructionOutcome.TECHNICAL_FAILED,
        ReconstructionOutcome.UNSUPPORTED,
        ReconstructionOutcome.ENCRYPTION_FAILED,
        ReconstructionOutcome.PLAYBACK_VERIFY_FAILED,
    ):
        # These are terminal no-charge outcomes — they "settle" as NO_CHARGE
        pass
    elif outcome == ReconstructionOutcome.HUMAN_REQUIRED:
        blockers.append("HUMAN_REQUIRED — awaiting approval")

    return blockers
