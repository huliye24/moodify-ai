"""Outcome taxonomy tests (MFY-CR-P07)."""

from __future__ import annotations

import pytest

from moodify.reconstruction_factory.outcome import OUTCOME_TAXONOMY, classify_outcome

pytestmark = pytest.mark.v01


def test_taxonomy_complete():
    assert set(OUTCOME_TAXONOMY) == {
        "GOLDEN", "IMPROVED", "SUBTLE_IMPROVEMENT", "SOURCE_WINS",
        "HUMAN_REQUIRED", "STEM_RECOMMENDED", "UNSUPPORTED", "FAILED",
    }


def test_source_wins_preserved():
    assert classify_outcome(improvement_noticeable=False, human_preferred=False, identity_safe=True) == "SOURCE_WINS"
    assert classify_outcome(improvement_noticeable=True, human_preferred=False, identity_safe=True) == "SOURCE_WINS"


def test_missing_human_signal_never_guessed():
    assert classify_outcome(True, human_preferred=None, identity_safe=True) == "HUMAN_REQUIRED"
    assert classify_outcome(True, human_preferred=True, identity_safe=None) == "HUMAN_REQUIRED"


def test_identity_unsafe_escalates():
    assert classify_outcome(True, human_preferred=True, identity_safe=False) == "HUMAN_REQUIRED"


def test_subtle_vs_improved():
    assert classify_outcome(False, human_preferred=True, identity_safe=True) == "SUBTLE_IMPROVEMENT"
    # single session without repetition stays IMPROVED (GOLDEN needs repeatability)
    assert classify_outcome(True, human_preferred=True, identity_safe=True) == "IMPROVED"


def test_stem_boundary_and_engineering_failure():
    assert classify_outcome(True, human_preferred=True, identity_safe=True, stem_boundary=True) == "STEM_RECOMMENDED"
    assert classify_outcome(True, human_preferred=True, identity_safe=True, engineering_ok=False) == "FAILED"
