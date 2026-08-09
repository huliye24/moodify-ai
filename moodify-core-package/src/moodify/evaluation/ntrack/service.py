"""N-track ranking orchestration (DSK-MFY-NTRACK-RANKER-001).

Each track is analyzed once through the canonical auditory scan
pipeline; scan results are cached per source hash and reused when the
analysis profile matches. A quality gate isolates failed/duplicate
tracks, a staged comparison plan builds a sparse preference graph
reusing the Pairwise Judge comparison engine, and a deterministic
Elo-style estimator produces the global order with uncertainty bands.
Album mode adds an evidence-linked redundancy/diversity re-ranking.
All artifacts persist immutably under `<case_root>/05_ntrack/`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import load_scan_evidence, scan_audio
from moodify.evaluation.ntrack.album import album_rerank, candidate_feature_vector
from moodify.evaluation.ntrack.estimator import estimate_global_ranking, plan_pairs
from moodify.evaluation.ntrack.models import (
    QUALITY_ANALYSIS_FAILED,
    QUALITY_ELIGIBLE,
    QUALITY_REJECTED,
    QUALITY_REVIEW_REQUIRED,
    HumanRankingDecision,
    PairwiseRankingEdge,
    QualityGateResult,
    RankingCandidate,
)
from moodify.evaluation.ntrack.policy import RankingPolicy
from moodify.evaluation.pairwise.dimensions import compare_dimensions
from moodify.evaluation.pairwise.policy import DecisionPolicy, decide

NTRACK_DIR = "05_ntrack"
SCAN_CACHE_DIR = "scan"
DEFAULT_PROFILE = "MFY-WSE-SCAN-PROFILE-001"


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _hash_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_evidence(scan_dir: Path, profile: Any) -> Any | None:
    if not (scan_dir / "metrics.json").is_file() or not (scan_dir / "analysis_data.npz").is_file():
        return None
    return load_scan_evidence(scan_dir, profile)


def run_ntrack_ranking(
    case_id: str,
    case_root: Path,
    track_paths: list[Path],
    mode: str = "TRACK_STRENGTH",
    top_k: int | None = None,
    profile_name: str = DEFAULT_PROFILE,
    ranking_policy: RankingPolicy | None = None,
    pairwise_policy: DecisionPolicy | None = None,
) -> dict[str, Any]:
    """Register, analyze, gate, compare, estimate, and persist a ranking case."""
    if len(track_paths) < 2:
        raise ValueError("ntrack ranking requires at least 2 tracks")

    ranking_policy = ranking_policy or RankingPolicy()
    pairwise_policy = pairwise_policy or DecisionPolicy()
    profile = get_profile(profile_name)
    ntrack_dir = (case_root / NTRACK_DIR).resolve()
    scan_cache = ntrack_dir / SCAN_CACHE_DIR

    registered: list[dict[str, Any]] = []
    seen_hashes: dict[str, str] = {}
    for idx, path in enumerate(track_paths, start=1):
        p = Path(path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"track {idx} not found: {p}")
        source_hash = _hash_file(p)
        candidate_id = f"rank-cand-{uuid4().hex[:10]}"
        duplicate_of = seen_hashes.get(source_hash)
        seen_hashes[source_hash] = candidate_id
        registered.append({
            "path": str(p),
            "candidate_id": candidate_id,
            "source_hash": source_hash,
            "original_position": idx,
            "duplicate_of": duplicate_of,
        })

    # Stage 1 + cache: analyze each unique track once per version.
    analyses: dict[str, Any] = {}
    gate_results: list[QualityGateResult] = []
    for entry in registered:
        cid = entry["candidate_id"]
        if entry["duplicate_of"]:
            gate_results.append(QualityGateResult(
                candidate_id=cid,
                state=QUALITY_REJECTED,
                reasons=("DUPLICATE_SOURCE",),
                evidence_refs=(),
            ))
            analyses[cid] = None
            continue
        scan_dir = scan_cache / entry["source_hash"]
        try:
            if not (scan_dir / "metrics.json").is_file():
                scan_dir.mkdir(parents=True, exist_ok=True)
                scan_audio(case_id, f"ntrack_{cid}", Path(entry["path"]), scan_dir, profile=profile)
            evidence = _load_evidence(scan_dir, profile)
            if evidence is None:
                raise RuntimeError("scan completed without evidence.json")
            analyses[cid] = evidence
        except Exception as exc:
            analyses[cid] = None
            gate_results.append(QualityGateResult(
                candidate_id=cid,
                state=QUALITY_ANALYSIS_FAILED,
                reasons=(f"ANALYSIS_FAILED:{type(exc).__name__}",),
                evidence_refs=(),
            ))
            continue
        gate_results.append(_quality_gate(cid, evidence, ranking_policy))

    # Stage 2: separate eligible tracks from isolated failures.
    eligible = [e for e in registered if _gate_state(gate_results, e["candidate_id"]) == QUALITY_ELIGIBLE]
    failed_ids = [e["candidate_id"] for e in registered if _gate_state(gate_results, e["candidate_id"]) == QUALITY_ANALYSIS_FAILED]

    # Stage 3: coarse prior order from evidence-backed proxy features.
    initial_order = _initial_order(eligible, analyses)

    # Stage 4 + 6: selective pairwise comparison with Top-K boundary refinement.
    edges, edge_plan = _compare_pairs(
        case_id, eligible, analyses, initial_order, top_k, ranking_policy, pairwise_policy,
    )

    # Stage 5 + 7: global estimate with tie bands and Top-K confidence.
    estimate = estimate_global_ranking(case_id, edges, ranking_policy, top_k=top_k)

    album_result = None
    if mode == "ALBUM_SELECTION" and ranking_policy.album_rerank_enabled:
        feature_vectors = {
            cid: candidate_feature_vector(analyses[cid].metrics)
            for cid, entry in [(e["candidate_id"], e) for e in eligible]
            if analyses[cid] is not None
        }
        album_result = album_rerank(case_id, estimate, feature_vectors, ranking_policy, top_k=top_k)

    candidates = [
        RankingCandidate(
            ranking_candidate_id=e["candidate_id"],
            ranking_case_id=case_id,
            source_audio_id=e["path"],
            source_hash=e["source_hash"],
            original_position=e["original_position"],
            analysis_run_id=analyses[e["candidate_id"]].case_id if analyses[e["candidate_id"]] else "",
            quality_gate_state=_gate_state(gate_results, e["candidate_id"]),
        )
        for e in registered
    ]

    ntrack_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(ntrack_dir / "ranking_case.json", {
        "ranking_case_id": case_id,
        "mode": mode,
        "top_k": top_k,
        "status": "COMPLETED",
        "ranking_policy_version": ranking_policy.version,
        "pairwise_policy_version": pairwise_policy.version,
    })
    _atomic_write(ntrack_dir / "candidates.json", {"candidates": [c.to_dict() for c in candidates]})
    _atomic_write(ntrack_dir / "quality_gate.json", {"results": [g.to_dict() for g in gate_results]})
    _atomic_write(ntrack_dir / "edges.json", {"edges": [e.to_dict() for e in edges], "plan": edge_plan})
    _atomic_write(ntrack_dir / "estimate.json", estimate.to_dict())
    _atomic_write(ntrack_dir / "policy.json", {
        "ranking_policy": ranking_policy.to_dict(),
        "pairwise_policy": pairwise_policy.to_dict(),
    })
    if album_result is not None:
        _atomic_write(ntrack_dir / "album_rerank.json", album_result.to_dict())

    result: dict[str, Any] = {
        "ranking_case_id": case_id,
        "mode": mode,
        "top_k": top_k,
        "status": "COMPLETED",
        "eligible_count": len(eligible),
        "failed_count": len(failed_ids),
        "rejected_ids": [e["candidate_id"] for e in registered if _gate_state(gate_results, e["candidate_id"]) == QUALITY_REJECTED],
        "review_required_ids": [e["candidate_id"] for e in registered if _gate_state(gate_results, e["candidate_id"]) == QUALITY_REVIEW_REQUIRED],
        "pairwise_edge_count": len(edges),
        "comparison_budget": edge_plan,
        "ranking": [c.to_dict() for c in estimate.ordered_candidates],
        "tie_bands": [list(b) for b in estimate.tie_bands],
        "ranking_estimate_id": estimate.ranking_estimate_id,
        "ranking_dir": str(ntrack_dir),
    }
    if album_result is not None:
        result["album_rerank"] = album_result.to_dict()
    return result


def record_human_ranking(
    case_root: Path,
    ranking_case_id: str,
    human_order: list[str],
    top_k: int | None = None,
    must_keep: list[str] | None = None,
    rejected: list[str] | None = None,
    optional_reason: str = "",
) -> dict[str, Any]:
    """Persist a human ranking edit and derive supported preference labels.

    Only logically supported pairwise changes (adjacent inversions
    between machine and human order) become preference records; machine
    ranking is never overwritten.
    """
    ntrack_dir = case_root / NTRACK_DIR
    estimate_path = ntrack_dir / "estimate.json"
    if not estimate_path.is_file():
        raise FileNotFoundError("run ntrack ranking before recording a human ranking")

    estimate = json.loads(estimate_path.read_text(encoding="utf-8"))
    machine_order = [c["candidate_id"] for c in estimate.get("ordered_candidates", [])]
    if set(human_order) != set(machine_order):
        raise ValueError("human order must contain exactly the ranked candidate ids")

    machine_top_k = machine_order[:top_k] if top_k else []
    decision = HumanRankingDecision(
        human_ranking_decision_id=f"hum-rank-{uuid4().hex[:10]}",
        ranking_case_id=ranking_case_id,
        machine_order=tuple(machine_order),
        human_order=tuple(human_order),
        machine_top_k=tuple(machine_top_k),
        human_top_k=tuple(human_order[:top_k]) if top_k else (),
        must_keep=tuple(must_keep or ()),
        rejected=tuple(rejected or ()),
        optional_reason=optional_reason,
    )
    _atomic_write(ntrack_dir / "human_ranking.json", decision.to_dict())

    derived = _derive_pairwise_preferences(machine_order, human_order, rejected or ())
    for (winner, loser) in derived:
        _append_ranking_preference(case_root, ranking_case_id, winner, loser)

    return {
        "human_ranking_decision": decision.to_dict(),
        "derived_preference_count": len(derived),
        "derived_preferences": [{"winner": winner, "loser": loser} for (winner, loser) in derived],
    }


def _quality_gate(cid: str, evidence: Any, policy: RankingPolicy) -> QualityGateResult:
    metrics = evidence.metrics
    reasons: list[str] = []
    refs: list[str] = []
    clipping = metrics.get("clipping_sample_ratio")
    silence = metrics.get("silence_ratio")
    if isinstance(clipping, (int, float)) and clipping > policy.review_clipping_ratio_threshold:
        reasons.append("SEVERE_CLIPPING")
        refs.append("clipping_sample_ratio")
    if isinstance(silence, (int, float)) and silence > policy.review_silence_ratio_threshold:
        reasons.append("MOSTLY_SILENT")
        refs.append("silence_ratio")
    if reasons:
        state = QUALITY_REVIEW_REQUIRED if policy.severe_failure_requires_review else QUALITY_ELIGIBLE
        return QualityGateResult(candidate_id=cid, state=state, reasons=tuple(reasons), evidence_refs=tuple(refs))
    return QualityGateResult(candidate_id=cid, state=QUALITY_ELIGIBLE)


def _gate_state(gate_results: list[QualityGateResult], cid: str) -> str:
    for gate in gate_results:
        if gate.candidate_id == cid:
            return gate.state
    return QUALITY_ANALYSIS_FAILED


def _initial_order(eligible: list[dict[str, Any]], analyses: dict[str, Any]) -> list[str]:
    def proxy(cid: str) -> float:
        evidence = analyses[cid]
        if evidence is None:
            return float("-inf")
        metrics = evidence.metrics
        lufs = metrics.get("integrated_lufs")
        lufs_score = abs(float(lufs) + 14.0) if isinstance(lufs, (int, float)) else 100.0
        peak = metrics.get("true_peak_dbfs")
        peak_penalty = max(0.0, 0.0 - float(peak)) if isinstance(peak, (int, float)) else 0.0
        clipping = metrics.get("clipping_sample_ratio")
        clipping_penalty = float(clipping) * 100.0 if isinstance(clipping, (int, float)) else 0.0
        return -(lufs_score + peak_penalty + clipping_penalty)

    return sorted((e["candidate_id"] for e in eligible), key=proxy)


def _compare_pairs(
    case_id: str,
    eligible: list[dict[str, Any]],
    analyses: dict[str, Any],
    initial_order: list[str],
    top_k: int | None,
    ranking_policy: RankingPolicy,
    pairwise_policy: DecisionPolicy,
) -> tuple[list[PairwiseRankingEdge], dict[str, Any]]:
    candidate_ids = [e["candidate_id"] for e in eligible]
    plan = plan_pairs(candidate_ids, ranking_policy, initial_order=initial_order, top_k=top_k)
    plan_dict = plan.to_dict()

    edges: list[PairwiseRankingEdge] = []
    extra_pairs: list[tuple[str, str]] = []
    if top_k and len(candidate_ids) > top_k:
        radius = ranking_policy.refinement_boundary_radius
        ordered = initial_order
        boundary = ordered[max(0, top_k - 1 - radius): min(len(ordered), top_k + radius)]
        seen = set(tuple(sorted(p)) for p in plan.pair_ids)
        for i, left in enumerate(boundary):
            for right in boundary[i + 1:]:
                key = tuple(sorted((left, right)))
                if key not in seen and len(extra_pairs) < (
                    ranking_policy.top_k_refinement_pairs_per_boundary_candidate * len(boundary)
                ):
                    seen.add(key)
                    extra_pairs.append((left, right))

    for pair in list(plan.pair_ids) + extra_pairs:
        a_id, b_id = pair
        a_evidence = analyses[a_id]
        b_evidence = analyses[b_id]
        if a_evidence is None or b_evidence is None:
            continue
        dimensions = compare_dimensions(a_evidence.metrics, b_evidence.metrics)
        judgment = decide(
            dimensions,
            pairwise_policy,
            pairwise_case_id=case_id,
            analysis_failed=None,
        )
        edges.append(PairwiseRankingEdge(
            edge_id=f"edge-{uuid4().hex[:10]}",
            ranking_case_id=case_id,
            candidate_a_id=a_id,
            candidate_b_id=b_id,
            outcome=judgment.outcome,
            confidence=judgment.confidence_level,
            evidence_weight=judgment.evidence_coverage or 1.0,
        ))

    plan_dict["refinement_extra_pairs"] = len(extra_pairs)
    plan_dict["pairs_actually_compared"] = len(edges)
    return edges, plan_dict


def _derive_pairwise_preferences(
    machine_order: list[str], human_order: list[str], rejected: list[str]
) -> list[tuple[str, str]]:
    machine_pos = {cid: idx for idx, cid in enumerate(machine_order)}
    human_pos = {cid: idx for idx, cid in enumerate(human_order)}
    derived: list[tuple[str, str]] = []
    for i, winner in enumerate(human_order):
        for loser in human_order[i + 1:]:
            if winner in rejected or loser in rejected:
                continue
            if machine_pos.get(winner, -1) > machine_pos.get(loser, len(human_order)):
                derived.append((winner, loser))
    for rejected_id in rejected:
        for other in human_order:
            if rejected_id != other and human_pos[rejected_id] < human_pos[other]:
                derived.append((other, rejected_id))
    return derived


def _append_ranking_preference(case_root: Path, ranking_case_id: str, winner: str, loser: str) -> None:
    from moodify.learning.models import PairwisePreference
    from moodify.learning.store import CaseLearningStore

    store = CaseLearningStore(case_root)
    store.append_preference(
        PairwisePreference(
            case_id=ranking_case_id,
            preferred_candidate_id=winner,
            other_candidate_id=loser,
            basis="HUMAN_EDITED",
            evaluator_id="human-ntrack-ranking",
            label_source="HUMAN_EDITED",
            machine_outcome="N/A",
            machine_confidence="N/A",
            eligible_for_training=True,
        )
    )
