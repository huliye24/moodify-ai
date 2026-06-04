"""MHP-203→207: Human Listening Evaluation — blind review, pairwise preference,
genre sensitivity, score explanation, reviewer agreement.

Provides the infrastructure for human-aligned MRS calibration.
Real labels come from human reviewers; this module provides the protocol,
data structures, and analysis tools.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════
# MHP-215: Label Dataset Schema
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ListeningLabel:
    """A single human listening judgment for a before/after audio pair."""
    label_id: str
    sample_id: str
    preset: str
    genre: str = ""

    # Review type
    review_type: str = "pairwise"  # "pairwise" | "absolute" | "gate_agreement" | "defect_tag"

    # Pairwise: "a_better" | "b_better" | "no_difference" | "both_bad"
    pairwise_decision: str = ""

    # Absolute scores (1-5)
    clarity_before: int = 0
    clarity_after: int = 0
    warmth_before: int = 0
    warmth_after: int = 0
    naturalness_before: int = 0
    naturalness_after: int = 0
    overall_before: int = 0
    overall_after: int = 0

    # Gate agreement
    gate_decision: str = ""        # "approve" | "reprocess" | "reject"
    agrees_with_automated_gate: Optional[bool] = None

    # Defect tags
    defect_tags: List[str] = field(default_factory=list)

    # Metadata
    reviewer_id: str = ""
    session_id: str = ""
    review_duration_s: float = 0.0
    notes: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    # MRS scores (for comparison)
    mrs_delta: Optional[float] = None
    mrs_open_delta: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════
# MHP-203/204: Blind Review + Pairwise Preference
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class BlindReviewSession:
    """A blind listening review session with randomized A/B order."""
    session_id: str
    reviewer_id: str = ""
    pairs: List[Dict[str, Any]] = field(default_factory=list)  # [{a_path, b_path, sample_id, preset, genre, randomized_order}]
    labels: List[ListeningLabel] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_blind_review_batch(
    before_paths: List[str],
    after_paths: List[str],
    sample_ids: List[str],
    presets: List[str],
    genres: List[str],
    reviewer_id: str = "",
    pairs_per_session: int = 20,
) -> BlindReviewSession:
    """Create a blind A/B review batch with randomized order.

    Each pair: before vs after, with A/B randomly assigned.
    Reviewer doesn't know which is processed.
    """
    import random

    session = BlindReviewSession(
        session_id=f"BRS_{uuid.uuid4().hex[:8].upper()}",
        reviewer_id=reviewer_id,
    )

    n = min(len(before_paths), len(after_paths), pairs_per_session)
    indices = list(range(n))
    random.shuffle(indices)

    for i in indices[:pairs_per_session]:
        swap = random.choice([True, False])
        pair = {
            "pair_index": i,
            "a_path": after_paths[i] if swap else before_paths[i],
            "b_path": before_paths[i] if swap else after_paths[i],
            "a_is_processed": swap,
            "sample_id": sample_ids[i] if i < len(sample_ids) else "",
            "preset": presets[i] if i < len(presets) else "",
            "genre": genres[i] if i < len(genres) else "",
        }
        session.pairs.append(pair)

    return session


# ═══════════════════════════════════════════════════════════════════════
# MHP-205: Genre Sensitivity Analysis
# ═══════════════════════════════════════════════════════════════════════


def analyze_genre_sensitivity(
    labels: List[ListeningLabel],
) -> Dict[str, Any]:
    """Compute per-genre agreement rates between human labels and MRS deltas.

    Returns: per-genre breakdown of: agreement rate, mean delta, reviewer preference distribution.
    """
    by_genre: Dict[str, List[ListeningLabel]] = {}
    for l in labels:
        by_genre.setdefault(l.genre or "unknown", []).append(l)

    result = {}
    for genre, g_labels in by_genre.items():
        # Agreement: human says "better" AND mrs_delta > 0, or "worse" AND mrs_delta < 0
        agree = 0
        total = 0
        for l in g_labels:
            if l.pairwise_decision and l.mrs_delta is not None:
                total += 1
                if (l.pairwise_decision == "a_better" and l.mrs_delta > 0) or \
                   (l.pairwise_decision == "b_better" and l.mrs_delta < 0):
                    agree += 1

        deltas = [l.mrs_delta for l in g_labels if l.mrs_delta is not None]
        result[genre] = {
            "n_labels": len(g_labels),
            "agreement_rate": round(agree / max(total, 1), 4),
            "mean_mrs_delta": round(np.mean(deltas), 2) if deltas else 0,
            "decisions": {
                "a_better": sum(1 for l in g_labels if l.pairwise_decision == "a_better"),
                "b_better": sum(1 for l in g_labels if l.pairwise_decision == "b_better"),
                "no_difference": sum(1 for l in g_labels if l.pairwise_decision == "no_difference"),
            },
        }

    return result


# ═══════════════════════════════════════════════════════════════════════
# MHP-206: Score Explanation
# ═══════════════════════════════════════════════════════════════════════


def explain_mrs_score(
    pseudo_mrs_before: float,
    pseudo_mrs_after: float,
    over_dark_level: str = "none",
    over_bright_level: str = "none",
    transient_damage_level: str = "none",
    vocal_thinning_level: str = "none",
    genre: str = "",
) -> str:
    """Generate a human-readable explanation of why MRS changed.

    This bridges the gap between numeric scores and human-understandable
    quality assessment.
    """
    delta = pseudo_mrs_after - pseudo_mrs_before
    parts = []

    if delta > 5:
        parts.append(f"Significant improvement (+{delta:.1f} MRS)")
    elif delta > 0:
        parts.append(f"Slight improvement (+{delta:.1f} MRS)")
    elif delta > -5:
        parts.append(f"Minimal change ({delta:.1f} MRS)")
    else:
        parts.append(f"Quality degradation ({delta:.1f} MRS)")

    if over_dark_level == "severe":
        parts.append("⚠️ Bass frequencies are excessive — over_dark detected")
    elif over_dark_level == "mild":
        parts.append("⚠️ Slight bass buildup — review recommended")

    if over_bright_level == "severe":
        parts.append("⚠️ High frequencies are harsh — over_bright detected")

    if transient_damage_level == "severe":
        parts.append("⚠️ Transient attacks have been softened too much")

    if vocal_thinning_level == "severe":
        parts.append("⚠️ Vocal body has been thinned — warmth lost")

    if not parts:
        parts.append("No quality issues detected")

    return " | ".join(parts)


# ═══════════════════════════════════════════════════════════════════════
# MHP-207: Reviewer Agreement Metrics
# ═══════════════════════════════════════════════════════════════════════


def compute_reviewer_agreement(
    labels: List[ListeningLabel],
) -> Dict[str, Any]:
    """Compute inter-reviewer agreement metrics.

    For the same sample+preset pair, what % of reviewers agree?
    """
    # Group by sample+preset
    by_pair: Dict[Tuple[str, str], List[ListeningLabel]] = {}
    for l in labels:
        key = (l.sample_id, l.preset)
        by_pair.setdefault(key, []).append(l)

    agreement_scores = []
    agreement_details = []

    for (sid, preset), group in by_pair.items():
        if len(group) < 2:
            continue
        decisions = [l.pairwise_decision for l in group if l.pairwise_decision]
        if len(decisions) < 2:
            continue

        # Majority agreement: most common decision / total reviewers
        from collections import Counter
        counts = Counter(decisions)
        majority = counts.most_common(1)[0][1]
        agree = majority / len(decisions)

        agreement_scores.append(agree)
        agreement_details.append({
            "sample_id": sid,
            "preset": preset,
            "n_reviewers": len(decisions),
            "decisions": dict(counts),
            "agreement": round(agree, 2),
        })

    return {
        "overall_agreement": round(np.mean(agreement_scores), 4) if agreement_scores else 0,
        "pairs_with_multiple_reviewers": len(agreement_scores),
        "details": agreement_details,
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-217: MRS-Human Comparison Pipeline
# ═══════════════════════════════════════════════════════════════════════


def compare_mrs_to_human(
    labels: List[ListeningLabel],
) -> Dict[str, Any]:
    """Compare MRS deltas against human pairwise decisions.

    Returns: Spearman correlation, agreement rate, confusion matrix.
    """
    human_map = {"a_better": 1, "b_better": -1, "no_difference": 0}
    mrs_deltas = []
    human_scores = []

    for l in labels:
        h = human_map.get(l.pairwise_decision)
        if h is None or l.mrs_delta is None:
            continue
        mrs_deltas.append(l.mrs_delta)
        human_scores.append(h)

    if len(mrs_deltas) < 3:
        return {"error": "insufficient_data", "n": len(mrs_deltas)}

    # Spearman r (uses local _spearman_r defined below)
    r = _spearman_r(mrs_deltas, human_scores)

    # Agreement: MRS sign matches human
    agree = 0
    for d, h in zip(mrs_deltas, human_scores):
        if (d > 0 and h == 1) or (d < 0 and h == -1) or (abs(d) < 0.5 and h == 0):
            agree += 1

    return {
        "n": len(mrs_deltas),
        "spearman_r": round(r, 4),
        "agreement_rate": round(agree / len(mrs_deltas), 4),
        "mrs_deltas": mrs_deltas,
        "human_scores": human_scores,
    }


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def _spearman_r(xs: List[float], ys: List[float]) -> float:
    """Spearman rank correlation — no scipy dependency."""
    if len(xs) < 3:
        return 0.0
    n = len(xs)
    rx = _rank(xs)
    ry = _rank(ys)
    mean_r = (n + 1) / 2.0
    num = sum((rx[i] - mean_r) * (ry[i] - mean_r) for i in range(n))
    den = np.sqrt(sum((rx[i] - mean_r) ** 2 for i in range(n)) *
                  sum((ry[i] - mean_r) ** 2 for i in range(n)))
    return float(num / den) if den > 0 else 0.0


def _rank(vals: List[float]) -> List[float]:
    indexed = sorted(enumerate(vals), key=lambda x: x[1])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg
        i = j
    return ranks


def save_labels_jsonl(labels: List[ListeningLabel], path: Path) -> int:
    """Save labels to JSONL file. Returns count written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for l in labels:
            f.write(json.dumps(l.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    return count


def load_labels_jsonl(path: Path) -> List[ListeningLabel]:
    """Load labels from JSONL. Returns list of ListeningLabel."""
    if not path.exists():
        return []
    labels = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                labels.append(ListeningLabel(**{k: v for k, v in d.items() if k in ListeningLabel.__dataclass_fields__}))
    return labels
