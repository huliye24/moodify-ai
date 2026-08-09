"""N-track ranking domain models (DSK-MFY-NTRACK-RANKER-001).

A ranking case accepts a group of tracks, analyzes each through the
canonical auditory pipeline once, gates quality, builds a preference
graph via selective pairwise comparison, estimates a global order with
uncertainty bands, and optionally applies album-aware re-ranking.
Human edits are stored as first-class preference data and never
silently overwrite the machine ranking.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

RANKING_MODE_TRACK = "TRACK_STRENGTH"
RANKING_MODE_ALBUM = "ALBUM_SELECTION"

QUALITY_ELIGIBLE = "ELIGIBLE"
QUALITY_REVIEW_REQUIRED = "REVIEW_REQUIRED"
QUALITY_REJECTED = "REJECTED"
QUALITY_ANALYSIS_FAILED = "ANALYSIS_FAILED"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RankingCandidate:
    ranking_candidate_id: str
    ranking_case_id: str
    source_audio_id: str
    source_hash: str
    original_position: int
    analysis_run_id: str = ""
    quality_gate_state: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RankingCandidate":
        return cls(**data)


@dataclass(frozen=True)
class QualityGateResult:
    candidate_id: str
    state: str
    reasons: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QualityGateResult":
        data = dict(data)
        data["reasons"] = tuple(data.get("reasons", ()))
        data["evidence_refs"] = tuple(data.get("evidence_refs", ()))
        return cls(**data)


@dataclass(frozen=True)
class PairwiseRankingEdge:
    edge_id: str
    ranking_case_id: str
    candidate_a_id: str
    candidate_b_id: str
    outcome: str  # A_WINS | B_WINS | INCONCLUSIVE
    confidence: str  # LOW | MEDIUM | HIGH
    evidence_weight: float = 1.0
    pairwise_case_id: str = ""
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PairwiseRankingEdge":
        return cls(**data)


@dataclass(frozen=True)
class RankedCandidateResult:
    candidate_id: str
    rank: int
    rank_band: str = ""
    score: float | None = None
    confidence: str = "LOW"
    top_k_membership: bool | None = None
    reasons: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RankedCandidateResult":
        data = dict(data)
        data["reasons"] = tuple(data.get("reasons", ()))
        data["evidence_refs"] = tuple(data.get("evidence_refs", ()))
        return cls(**data)


@dataclass(frozen=True)
class GlobalRankingEstimate:
    ranking_estimate_id: str
    ranking_case_id: str
    model_version: str
    ordered_candidates: tuple[RankedCandidateResult, ...] = ()
    tie_bands: tuple[tuple[str, ...], ...] = ()
    latent_scores: dict[str, float] = field(default_factory=dict)
    pairwise_edge_count: int = 0
    comparison_budget: dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["ordered_candidates"] = [c.to_dict() for c in self.ordered_candidates]
        payload["tie_bands"] = [list(b) for b in self.tie_bands]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GlobalRankingEstimate":
        data = dict(data)
        data["ordered_candidates"] = tuple(
            RankedCandidateResult.from_dict(c) for c in data.get("ordered_candidates", [])
        )
        data["tie_bands"] = tuple(tuple(b) for b in data.get("tie_bands", []))
        return cls(**data)


@dataclass(frozen=True)
class AlbumAwareRanking:
    album_ranking_id: str
    ranking_case_id: str
    base_ranking_estimate_id: str
    policy_version: str
    selected_candidate_ids: tuple[str, ...] = ()
    reranked_candidates: tuple[RankedCandidateResult, ...] = ()
    redundancy_penalties: dict[str, float] = field(default_factory=dict)
    diversity_contributions: dict[str, float] = field(default_factory=dict)
    explanations: tuple[str, ...] = ()
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reranked_candidates"] = [c.to_dict() for c in self.reranked_candidates]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlbumAwareRanking":
        data = dict(data)
        data["reranked_candidates"] = tuple(
            RankedCandidateResult.from_dict(c) for c in data.get("reranked_candidates", [])
        )
        return cls(**data)


@dataclass(frozen=True)
class HumanRankingDecision:
    human_ranking_decision_id: str
    ranking_case_id: str
    machine_order: tuple[str, ...] = ()
    human_order: tuple[str, ...] = ()
    machine_top_k: tuple[str, ...] = ()
    human_top_k: tuple[str, ...] = ()
    must_keep: tuple[str, ...] = ()
    rejected: tuple[str, ...] = ()
    optional_reason: str = ""
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HumanRankingDecision":
        data = dict(data)
        for key in ("machine_order", "human_order", "machine_top_k", "human_top_k",
                    "must_keep", "rejected"):
            data[key] = tuple(data.get(key, ()))
        return cls(**data)
