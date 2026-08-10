"""MFY-DATA-FACTORY-001 human review validation tests."""

from __future__ import annotations

import pytest

from moodify.data_factory.human_review import pairwise_preferences, validate_completed_review
from moodify.data_factory.models import HumanReview

CASE_ID = "case_" + "a" * 32


def _review(ranking: list[str], **changes) -> HumanReview:
    values = {
        "case_id": CASE_ID,
        "ranking": ranking,
        "rejected": [],
        "reviewer_id": "human-001",
        "notes": "",
        "completed_at": "2026-08-10T00:00:00+00:00",
    }
    values.update(changes)
    return HumanReview(**values)


def test_four_item_ranking_yields_six_pairwise_preferences():
    review = _review(["B", "A", "SOURCE", "C"])
    rows = pairwise_preferences(review)
    assert len(rows) == 6
    assert rows[0]["winner"] == "B"
    assert rows[0]["loser"] == "A"
    pairs = {(row["winner"], row["loser"]) for row in rows}
    assert pairs == {
        ("B", "A"), ("B", "SOURCE"), ("B", "C"),
        ("A", "SOURCE"), ("A", "C"), ("SOURCE", "C"),
    }


def test_review_rejects_duplicate_items():
    with pytest.raises(ValueError):
        validate_completed_review(_review(["A", "A", "B", "C"]))


def test_review_rejects_missing_items():
    with pytest.raises(ValueError):
        validate_completed_review(_review(["A", "B", "C"]))


def test_review_rejects_unknown_item():
    with pytest.raises(ValueError):
        validate_completed_review(_review(["B", "A", "SOURCE", "D"]))


def test_review_rejects_unknown_rejected_item():
    with pytest.raises(ValueError):
        validate_completed_review(_review(["B", "A", "SOURCE", "C"], rejected=["X"]))


def test_review_requires_reviewer_and_completed_at():
    with pytest.raises(ValueError):
        validate_completed_review(_review(["B", "A", "SOURCE", "C"], reviewer_id=""))
    with pytest.raises(ValueError):
        validate_completed_review(_review(["B", "A", "SOURCE", "C"], completed_at=None))


def test_rejected_candidate_is_allowed_alongside_ranking():
    review = _review(["B", "A", "SOURCE", "C"], rejected=["C"])
    assert len(pairwise_preferences(review)) == 6
