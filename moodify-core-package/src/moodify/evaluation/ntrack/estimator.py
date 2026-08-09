"""Global rank estimation from a sparse pairwise preference graph
(DSK-MFY-NTRACK-RANKER-001).

Uses an Elo-style online update over the collected edges: deterministic
given fixed edges and policy, tolerant of missing pairs and cycles,
and explicit about uncertainty. INCONCLUSIVE edges never move scores —
they only mark a pair as tied/uncertain. Rank bands group candidates
whose latent scores are closer than the configured separation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from moodify.evaluation.ntrack.models import (
    GlobalRankingEstimate,
    PairwiseRankingEdge,
    RankedCandidateResult,
)
from moodify.evaluation.ntrack.policy import RankingPolicy

MODEL_VERSION = "ntrack_elo_v1"

_CONFIDENCE_GAP_HIGH = 30.0
_CONFIDENCE_GAP_MEDIUM = 12.0


def _expected(a: float, b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((b - a) / 400.0))


def estimate_global_ranking(
    ranking_case_id: str,
    edges: list[PairwiseRankingEdge],
    policy: RankingPolicy,
    top_k: int | None = None,
) -> GlobalRankingEstimate:
    """Estimate a global order from the preference graph."""
    candidate_ids: list[str] = []
    for edge in edges:
        for cid in (edge.candidate_a_id, edge.candidate_b_id):
            if cid not in candidate_ids:
                candidate_ids.append(cid)

    scores: dict[str, float] = {cid: policy.elo_initial_score for cid in candidate_ids}
    weights: dict[str, float] = {cid: 0.0 for cid in candidate_ids}

    decisive = [e for e in edges if e.outcome in {"A_WINS", "B_WINS"}]
    # Two update passes over deterministic edge order for convergence.
    for _ in range(2):
        for edge in decisive:
            a, b = edge.candidate_a_id, edge.candidate_b_id
            expected_a = _expected(scores[a], scores[b])
            outcome = 1.0 if edge.outcome == "A_WINS" else 0.0
            k = policy.elo_base_k * _weight(edge, policy)
            scores[a] += k * (outcome - expected_a)
            scores[b] += k * ((1.0 - outcome) - (1.0 - expected_a))

    for edge in decisive:
        winner = edge.candidate_a_id if edge.outcome == "A_WINS" else edge.candidate_b_id
        weights[winner] += _weight(edge, policy)

    ordered = sorted(scores, key=lambda cid: (-scores[cid], cid))

    tie_bands: list[tuple[str, ...]] = []
    if policy.allow_tie_bands and len(ordered) > 1:
        band: list[str] = [ordered[0]]
        for prev, cur in zip(ordered, ordered[1:]):
            if scores[prev] - scores[cur] < policy.minimum_rank_separation:
                band.append(cur)
            else:
                if len(band) > 1:
                    tie_bands.append(tuple(band))
                band = [cur]
        if len(band) > 1:
            tie_bands.append(tuple(band))

    band_of: dict[str, str] = {}
    for idx, band in enumerate(tie_bands, start=1):
        for cid in band:
            band_of[cid] = f"{idx}"

    ordered_results: list[RankedCandidateResult] = []
    for rank, cid in enumerate(ordered, start=1):
        band = band_of.get(cid, "")
        band_label = f"#{rank}" if not band else f"#{rank}-tied"
        reasons: list[str] = []
        if band:
            reasons.append("RANK_TIE_BAND")
        if weights[cid] > 0:
            reasons.append(f"PAIRWISE_WINS_WEIGHT={weights[cid]:.2f}")
        else:
            reasons.append("NO_DECISIVE_EDGES")
        ordered_results.append(
            RankedCandidateResult(
                candidate_id=cid,
                rank=rank,
                rank_band=band_label,
                score=round(scores[cid], 4),
                confidence=_rank_confidence(cid, scores, ordered, weights, top_k, policy),
                top_k_membership=rank <= top_k if top_k else None,
                reasons=tuple(reasons),
            )
        )

    return GlobalRankingEstimate(
        ranking_estimate_id=f"est-{uuid4().hex[:12]}",
        ranking_case_id=ranking_case_id,
        model_version=MODEL_VERSION,
        ordered_candidates=tuple(ordered_results),
        tie_bands=tuple(tie_bands),
        latent_scores={cid: round(s, 4) for cid, s in scores.items()},
        pairwise_edge_count=len(edges),
    )


def _weight(edge: PairwiseRankingEdge, policy: RankingPolicy) -> float:
    conf = policy.confidence_weight.get(edge.confidence, 0.6)
    return max(0.0, min(2.0, conf * edge.evidence_weight))


def _rank_confidence(
    cid: str,
    scores: dict[str, float],
    ordered: list[str],
    weights: dict[str, float],
    top_k: int | None,
    policy: RankingPolicy,
) -> str:
    """Confidence band from local score gaps and edge evidence."""
    idx = ordered.index(cid)
    if weights[cid] == 0.0:
        return "LOW"
    if top_k and idx == top_k - 1:
        # Boundary candidate: gap to the next track decides membership confidence.
        if idx + 1 < len(ordered):
            gap = scores[cid] - scores[ordered[idx + 1]]
        else:
            gap = _CONFIDENCE_GAP_HIGH
        if gap < _CONFIDENCE_GAP_MEDIUM:
            return "LOW"
        if gap < _CONFIDENCE_GAP_HIGH:
            return "MEDIUM"
        return "HIGH"
    if idx + 1 < len(ordered):
        gap = scores[cid] - scores[ordered[idx + 1]]
        if gap < _CONFIDENCE_GAP_MEDIUM:
            return "LOW"
        if gap < _CONFIDENCE_GAP_HIGH:
            return "MEDIUM"
    return "HIGH"


@dataclass(frozen=True)
class BudgetPlan:
    """Which pairs to compare, derived from the staged architecture."""

    pair_ids: tuple[tuple[str, str], ...] = ()
    budget_name: str = ""
    budget_limit: int = 0
    total_pairs_available: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_ids": [list(p) for p in self.pair_ids],
            "budget_name": self.budget_name,
            "budget_limit": self.budget_limit,
            "total_pairs_available": self.total_pairs_available,
        }


def plan_pairs(
    candidate_ids: list[str],
    policy: RankingPolicy,
    initial_order: list[str] | None = None,
    top_k: int | None = None,
) -> BudgetPlan:
    """Select high-information pairs within the comparison budget.

    Small batches compare exhaustively. Larger batches walk the coarse
    prior order, comparing adjacent candidates first, then stepping out
    one position, until the budget is spent. When a Top-K is requested,
    the boundary neighborhood is always covered first.
    """
    order = list(initial_order or candidate_ids)
    budget = policy.comparison_budget_for(len(order))
    max_pairs = budget["max_pairs"]

    selected: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def _add(pair: tuple[str, str]) -> bool:
        key = tuple(sorted(pair))
        if key in seen or len(selected) >= max_pairs:
            return False
        seen.add(key)
        selected.append(pair)
        return True

    if top_k and len(order) > top_k:
        radius = policy.refinement_boundary_radius
        boundary = order[max(0, top_k - 1 - radius): min(len(order), top_k + radius)]
        for i, left in enumerate(boundary):
            for right in boundary[i + 1:]:
                if not _add((left, right)):
                    break

    for step in range(1, len(order)):
        if len(selected) >= max_pairs:
            break
        for i in range(len(order) - step):
            _add((order[i], order[i + step]))

    return BudgetPlan(
        pair_ids=tuple(selected),
        budget_name=budget["budget_name"],
        budget_limit=max_pairs,
        total_pairs_available=budget["all_pairs"],
    )
