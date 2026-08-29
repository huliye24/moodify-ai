"""Machine-Human agreement analysis tests (MFY-CR-P07)."""

from __future__ import annotations

import pytest

from moodify.reconstruction_factory.agreement import analyze_agreement

pytestmark = pytest.mark.v01


def test_agreement_counts_matching_ranks():
    records = [
        {"technical_rank": "B", "human_rank": "B", "identity_preservation_rank": "B"},
        {"technical_rank": "A", "human_rank": "C", "identity_preservation_rank": "A"},
    ]
    a = analyze_agreement(records)
    assert a.n == 2
    assert a.technical_top_matches_human_top == 1
    assert a.technical_top_matches_identity_top == 2


def test_disagreement_patterns_reported():
    records = [
        {"technical_rank": "A", "human_rank": "C", "identity_preservation_rank": "A"},
        {"technical_rank": "B", "human_rank": "B", "identity_guard_results": {"verdict": "CAUTION"}},
        {"source_vs_winner_result": "SOURCE_WINS"},
    ]
    a = analyze_agreement(records)
    assert "TECH_RANKING_OK_BUT_HUMAN_DISAGREES" in a.patterns
    assert "HUMAN_LIKES_BUT_IDENTITY_CAUTION" in a.patterns
    assert "SOURCE_WINS" in a.patterns


def test_missing_signals_not_guessed():
    a = analyze_agreement([{"technical_rank": "B"}])
    assert a.technical_top_matches_human_top == 0
    assert "MACHINE_CONFIDENT_HUMAN_MISSING" in a.patterns
