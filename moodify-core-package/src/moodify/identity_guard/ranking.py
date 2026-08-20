"""Candidate ranking with Identity Guard gate (MFY-CR-P05 §16).

Order of evaluation (deterministic):

1. Technical hard gate (caller-supplied; failed candidates excluded upstream)
2. Identity hard reject          -> excluded from auto ranking
3. Reconstruction objective progress (descending)
4. Identity caution penalty      -> CAUTION ranks below PASS
5. Minimal intervention preference (tie-break by intervention magnitude)
6. Uncertainty penalty (ascending)
7. SOURCE remains eligible (always appended)

REJECT candidates can never be the automatic top pick; HUMAN_REQUIRED
candidates may stay ranked but can never be auto-approved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from moodify.identity_guard.contract import GuardState, IdentityVerdict

_GUARD_ORDER = {
    GuardState.PASS: 0,
    GuardState.CAUTION: 1,
    GuardState.HUMAN_REQUIRED: 2,
    GuardState.REJECT: 3,
}


@dataclass(frozen=True)
class CandidateRank:
    candidate_id: str
    guard_state: GuardState
    position: int
    auto_approvable: bool
    objective_progress: float
    intervention_magnitude: float
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "guard_state": self.guard_state.value,
            "position": self.position,
            "auto_approvable": self.auto_approvable,
            "objective_progress": self.objective_progress,
            "intervention_magnitude": self.intervention_magnitude,
            "reason": self.reason,
        }


def intervention_magnitude(verdict: IdentityVerdict) -> float:
    """Sum of absolute normalized deltas across measured dimensions."""
    total = 0.0
    for d in verdict.deltas:
        if d.normalized_delta is not None and d.guard_state != GuardState.NOT_MEASURABLE:
            total += abs(d.normalized_delta)
    return round(total, 3)


def rank_candidates(
    candidates: list[IdentityVerdict],
    *,
    objective_progress: dict[str, float] | None = None,
    uncertainty: dict[str, float] | None = None,
    source_id: str = "source",
) -> list[CandidateRank]:
    """Rank verdicts (guard outputs) with the Identity Gate.

    ``objective_progress`` maps candidate_id -> progress toward the
    reconstruction objective (0..1); ``uncertainty`` maps candidate_id ->
    uncertainty penalty (0..1, lower is better).
    """
    objective_progress = objective_progress or {}
    uncertainty = uncertainty or {}

    eligible: list[IdentityVerdict] = []
    rejected: list[IdentityVerdict] = []
    for verdict in candidates:
        (eligible if verdict.state != GuardState.REJECT else rejected).append(verdict)

    eligible.sort(
        key=lambda v: (
            _GUARD_ORDER[v.state],                      # 2/4: identity state first
            -objective_progress.get(v.candidate_id, 0.0),  # 3: objective progress
            uncertainty.get(v.candidate_id, 0.0),       # 6: uncertainty penalty
            intervention_magnitude(v),                  # 5: minimal intervention
            v.candidate_id,                             # deterministic tie-break
        )
    )

    ranks: list[CandidateRank] = []
    for position, verdict in enumerate(eligible, start=1):
        auto = verdict.state == GuardState.PASS
        ranks.append(CandidateRank(
            candidate_id=verdict.candidate_id,
            guard_state=verdict.state,
            position=position,
            auto_approvable=auto,
            objective_progress=objective_progress.get(verdict.candidate_id, 0.0),
            intervention_magnitude=intervention_magnitude(verdict),
            reason="identity PASS, auto-approvable" if auto
            else "identity does not allow auto-approval",
        ))

    for verdict in rejected:
        ranks.append(CandidateRank(
            candidate_id=verdict.candidate_id,
            guard_state=GuardState.REJECT,
            position=len(ranks) + 1,
            auto_approvable=False,
            objective_progress=objective_progress.get(verdict.candidate_id, 0.0),
            intervention_magnitude=intervention_magnitude(verdict),
            reason="identity hard reject — cannot be an automatic top candidate",
        ))

    # 7: SOURCE always exists as an eligible result
    ranks.append(CandidateRank(
        candidate_id=source_id,
        guard_state=GuardState.PASS,
        position=len(ranks) + 1,
        auto_approvable=True,
        objective_progress=0.0,
        intervention_magnitude=0.0,
        reason="SOURCE is always an eligible result (no intervention)",
    ))
    return ranks
