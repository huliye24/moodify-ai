"""Human ranking capture for SOURCE/A/B/C."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import HumanReview

ALLOWED_ITEMS = ("SOURCE", "A", "B", "C")


def write_review_template(case_id: str, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "case_id": case_id,
        "instructions": "Listen without relying on machine scores. Rank SOURCE/A/B/C best to worst.",
        "allowed_items": list(ALLOWED_ITEMS),
        "ranking": [],
        "rejected": [],
        "reviewer_id": "",
        "notes": "",
        "completed_at": None,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_review(path: Path) -> HumanReview:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return HumanReview(
        case_id=str(data["case_id"]),
        ranking=list(data.get("ranking", [])),
        rejected=list(data.get("rejected", [])),
        reviewer_id=str(data.get("reviewer_id", "")),
        notes=str(data.get("notes", "")),
        completed_at=data.get("completed_at"),
    )


def validate_completed_review(review: HumanReview) -> None:
    if len(review.ranking) != len(ALLOWED_ITEMS):
        raise ValueError("completed review must rank SOURCE/A/B/C exactly once")
    if set(review.ranking) != set(ALLOWED_ITEMS):
        raise ValueError("ranking must contain exactly SOURCE/A/B/C")
    if len(set(review.ranking)) != len(review.ranking):
        raise ValueError("ranking contains duplicate items")
    if any(item not in ALLOWED_ITEMS for item in review.rejected):
        raise ValueError("rejected contains unknown item")
    if not review.reviewer_id.strip():
        raise ValueError("reviewer_id is required")
    if not review.completed_at:
        raise ValueError("completed_at is required")


def stamp_review_complete(path: Path, reviewer_id: str) -> None:
    """Small helper for operator tooling; ranking must already be filled manually."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["reviewer_id"] = reviewer_id
    data["completed_at"] = datetime.now(timezone.utc).isoformat()
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pairwise_preferences(review: HumanReview) -> list[dict]:
    validate_completed_review(review)
    rows: list[dict] = []
    for winner_index, winner in enumerate(review.ranking):
        for loser in review.ranking[winner_index + 1 :]:
            rows.append(
                {
                    "case_id": review.case_id,
                    "winner": winner,
                    "loser": loser,
                    "preference": 1,
                    "reviewer_id": review.reviewer_id,
                    "completed_at": review.completed_at,
                }
            )
    if len(rows) != 6:
        raise RuntimeError("four-item ranking must produce six pairwise rows")
    return rows
