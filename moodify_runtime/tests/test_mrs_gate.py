"""MHP-074: Gate Threshold Unit Tests — genre dispatch, over-dark, boundaries.

Tests for decide_candidate_gate() with:
- Genre-specific threshold dispatch
- Graduated over-dark levels (none/mild/severe)
- Threshold boundary conditions
- Combined gate scenarios
"""

import pytest

from moodify_runtime.operator_console import decide_candidate_gate


# ── Genre threshold dispatch ─────────────────────────────────────────


def test_default_thresholds_no_genre():
    """Without genre, defaults apply: mrs_delta=0.0, transient=1.0, loudness=1.0."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=0.5)
    assert r["decision"] == "approve"

    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=-0.1)
    assert r["decision"] == "reprocess"


def test_electronic_genre_threshold():
    """Electronic: required_mrs_delta=2.0. Delta=1.5 should reprocess."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=1.5, genre="electronic")
    assert r["decision"] == "reprocess"
    assert "mrs_delta_below_threshold" in r["reasons"]

    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=2.5, genre="electronic")
    assert r["decision"] == "approve"


def test_piano_genre_threshold():
    """Piano: required_mrs_delta=1.0. Delta=0.5 should reprocess."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=0.5, genre="piano")
    assert r["decision"] == "reprocess"

    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=1.5, genre="piano")
    assert r["decision"] == "approve"


def test_vocal_loudness_penalty():
    """Vocal: loudness_penalty_threshold=0.7 (strict)."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=3.0,
                              loudness_penalty=0.8, genre="vocal")
    assert r["decision"] == "reject"
    assert "loudness_penalty_above_threshold" in r["reasons"]


def test_rock_transient_threshold():
    """Rock: transient_threshold=0.6 (strict)."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=3.0,
                              transient_damage=0.7, genre="rock")
    assert r["decision"] == "reject"
    assert "transient_damage_above_threshold" in r["reasons"]


def test_ambient_mrs_delta():
    """Ambient: required_mrs_delta=3.0 (hardest to satisfy)."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=2.0, genre="ambient")
    assert r["decision"] == "reprocess"


# ── Graduated over-dark levels ───────────────────────────────────────


def test_over_dark_none_passes():
    """over_dark_level=none should not affect gate."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=1.0,
                              over_dark_level="none")
    assert r["decision"] == "approve"
    assert "all_gates_passed" in r["reasons"]


def test_over_dark_mild_reprocesses():
    """over_dark_level=mild + good MRS → reprocess."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=2.0,
                              over_dark_level="mild")
    assert r["decision"] == "reprocess"
    assert "over_dark_mild" in r["reasons"]


def test_over_dark_severe_rejects():
    """over_dark_level=severe + any MRS → reject."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=10.0,
                              over_dark_level="severe")
    assert r["decision"] == "reject"
    assert "over_dark_severe" in r["reasons"]


def test_over_dark_level_overrides_binary_flag():
    """Explicit level overrides legacy boolean."""
    # Legacy flag would reprocess, but severe level rejects
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=5.0,
                              over_dark_triggered=True, over_dark_level="severe")
    assert r["decision"] == "reject"


# ── Backward compatibility: binary flag ──────────────────────────────


def test_binary_over_dark_triggered_reprocesses():
    """Legacy over_dark_triggered=True → reprocess (not reject)."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=2.0,
                              over_dark_triggered=True)
    assert r["decision"] == "reprocess"
    assert "over_dark_triggered" in r["reasons"]


# ── Runtime failure always rejects ───────────────────────────────────


def test_runtime_failure_rejects():
    """Runtime failure is always reject, regardless of MRS."""
    r = decide_candidate_gate("C1", "J1", False, mrs_score_delta=100.0)
    assert r["decision"] == "reject"
    assert "runtime_failed" in r["reasons"]


# ── Combined scenarios ───────────────────────────────────────────────


def test_good_mrs_mild_overdark_reprocess():
    """Good MRS + mild over_dark → reprocess (not reject)."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=5.0,
                              over_dark_level="mild")
    assert r["decision"] == "reprocess"


def test_bad_mrs_no_overdark_reprocess():
    """Bad MRS + no over_dark → reprocess."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=-1.0,
                              over_dark_level="none")
    assert r["decision"] == "reprocess"
    assert "mrs_delta_below_threshold" in r["reasons"]


def test_transient_damage_rejects_over_good_mrs():
    """Transient damage above threshold rejects even with good MRS."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=10.0,
                              transient_damage=1.5, transient_threshold=1.0)
    assert r["decision"] == "reject"


def test_mrs_delta_missing_reprocess():
    """Missing MRS delta should trigger reprocess, not crash."""
    r = decide_candidate_gate("C1", "J1", True, mrs_score_delta=None)
    assert r["decision"] == "reprocess"
    assert "mrs_delta_missing" in r["reasons"]
