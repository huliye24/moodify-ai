"""MHP-220: Listening Core Tests — blind review, pairwise, genre sensitivity, agreement."""

import tempfile
from pathlib import Path

from moodify_runtime.listening import (
    ListeningLabel,
    BlindReviewSession,
    create_blind_review_batch,
    analyze_genre_sensitivity,
    explain_mrs_score,
    compute_reviewer_agreement,
    compare_mrs_to_human,
    save_labels_jsonl,
    load_labels_jsonl,
)


# ── Label Schema ──────────────────────────────────────────────────────


def test_listening_label_creation():
    l = ListeningLabel(
        label_id="LBL_001", sample_id="SMP_001", preset="warm_vocal",
        genre="piano", review_type="pairwise", pairwise_decision="a_better",
        reviewer_id="R1", mrs_delta=5.0,
    )
    assert l.pairwise_decision == "a_better"
    assert l.mrs_delta == 5.0
    d = l.to_dict()
    assert d["label_id"] == "LBL_001"
    assert d["sample_id"] == "SMP_001"


# ── Blind Review Batch ────────────────────────────────────────────────


def test_blind_review_batch_randomization():
    before = [f"before_{i}.wav" for i in range(10)]
    after = [f"after_{i}.wav" for i in range(10)]
    sids = [f"SMP_{i:03d}" for i in range(10)]
    presets = ["warm_vocal"] * 10
    genres = ["piano"] * 10

    session = create_blind_review_batch(before, after, sids, presets, genres, pairs_per_session=10)
    assert len(session.pairs) == 10
    # Check randomization: not all pairs should have a_is_processed=True
    a_processed = [p["a_is_processed"] for p in session.pairs]
    assert not all(a_processed)  # some should be swapped
    assert not all(not p for p in a_processed)  # some should not be swapped


def test_blind_review_batch_max_pairs():
    session = create_blind_review_batch(
        ["b1.wav"], ["a1.wav"], ["S1"], ["warm_vocal"], ["piano"],
        pairs_per_session=5,
    )
    assert len(session.pairs) == 1  # only 1 pair available


# ── Genre Sensitivity ─────────────────────────────────────────────────


def test_genre_sensitivity_analysis():
    labels = [
        ListeningLabel(label_id="L1", sample_id="S1", preset="warm_vocal", genre="piano",
                       pairwise_decision="a_better", mrs_delta=5.0),
        ListeningLabel(label_id="L2", sample_id="S2", preset="warm_vocal", genre="piano",
                       pairwise_decision="b_better", mrs_delta=-3.0),
        ListeningLabel(label_id="L3", sample_id="S3", preset="clean_master", genre="electronic",
                       pairwise_decision="a_better", mrs_delta=2.0),
    ]
    result = analyze_genre_sensitivity(labels)
    assert "piano" in result
    assert "electronic" in result
    assert result["piano"]["n_labels"] == 2


# ── Score Explanation ─────────────────────────────────────────────────


def test_explain_mrs_score_improvement():
    exp = explain_mrs_score(50.0, 55.0, over_dark_level="none")
    assert "improvement" in exp.lower() or "+5" in exp
    assert "⚠️" not in exp


def test_explain_mrs_score_with_defects():
    exp = explain_mrs_score(50.0, 55.0, over_dark_level="severe", transient_damage_level="severe")
    assert "over_dark" in exp
    assert "Transient" in exp


# ── Reviewer Agreement ────────────────────────────────────────────────


def test_reviewer_agreement_perfect():
    labels = [
        ListeningLabel(label_id="L1", sample_id="S1", preset="warm_vocal", pairwise_decision="a_better", reviewer_id="R1"),
        ListeningLabel(label_id="L2", sample_id="S1", preset="warm_vocal", pairwise_decision="a_better", reviewer_id="R2"),
    ]
    result = compute_reviewer_agreement(labels)
    assert result["overall_agreement"] == 1.0


def test_reviewer_agreement_split():
    labels = [
        ListeningLabel(label_id="L1", sample_id="S1", preset="warm_vocal", pairwise_decision="a_better", reviewer_id="R1"),
        ListeningLabel(label_id="L2", sample_id="S1", preset="warm_vocal", pairwise_decision="b_better", reviewer_id="R2"),
    ]
    result = compute_reviewer_agreement(labels)
    assert result["overall_agreement"] == 0.5


# ── MRS-Human Comparison ─────────────────────────────────────────────


def test_compare_mrs_to_human():
    labels = [
        ListeningLabel(label_id="L1", sample_id="S1", preset="warm_vocal", pairwise_decision="a_better", mrs_delta=10.0),
        ListeningLabel(label_id="L2", sample_id="S2", preset="warm_vocal", pairwise_decision="b_better", mrs_delta=-5.0),
        ListeningLabel(label_id="L3", sample_id="S3", preset="clean_master", pairwise_decision="no_difference", mrs_delta=0.1),
    ]
    result = compare_mrs_to_human(labels)
    assert result["agreement_rate"] == 1.0  # all 3 match


def test_compare_mrs_to_human_insufficient():
    labels = [ListeningLabel(label_id="L1", sample_id="S1", preset="w", pairwise_decision="a_better", mrs_delta=1.0)]
    result = compare_mrs_to_human(labels)
    assert "error" in result


# ── JSONL Roundtrip ──────────────────────────────────────────────────


def test_labels_jsonl_roundtrip(tmp_path):
    labels = [
        ListeningLabel(label_id="L1", sample_id="S1", preset="warm_vocal", genre="piano",
                       pairwise_decision="a_better", mrs_delta=5.0, reviewer_id="R1"),
        ListeningLabel(label_id="L2", sample_id="S2", preset="clean_master", genre="electronic",
                       pairwise_decision="no_difference", mrs_delta=0.0, reviewer_id="R1"),
    ]
    path = tmp_path / "labels.jsonl"
    n = save_labels_jsonl(labels, path)
    assert n == 2

    loaded = load_labels_jsonl(path)
    assert len(loaded) == 2
    assert loaded[0].label_id == "L1"
    assert loaded[0].mrs_delta == 5.0
