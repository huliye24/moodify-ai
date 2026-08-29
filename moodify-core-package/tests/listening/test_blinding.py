"""Blinding engine tests (MFY_MOBILE_LISTENING_VALIDATION_001)."""

from __future__ import annotations

import pytest

from moodify.listening.blinding import build_sessions, randomize_assignment
from moodify.listening.protocol import build_default_protocol

pytestmark = pytest.mark.v01


def test_assignment_deterministic_per_seed():
    a = randomize_assignment("t1", "s1", "in.wav", "out.wav", seed=42)
    b = randomize_assignment("t1", "s1", "in.wav", "out.wav", seed=42)
    assert a == b
    assert a.play_a in ("in.wav", "out.wav")
    assert a.play_b in ("in.wav", "out.wav")
    assert a.play_a != a.play_b
    # labels are hidden from the reviewer until reveal
    assert a.label_a in ("ORIGINAL", "PROCESSED")
    assert a.label_b in ("ORIGINAL", "PROCESSED")


def test_different_seed_changes_assignment():
    # 50/50 swap; may occasionally collide, so verify the label mapping differs
    # for at least one of several seeds
    seeds = [randomize_assignment("t1", "s1", "in.wav", "out.wav", s) for s in range(1, 9)]
    assert len({x.label_a for x in seeds}) > 1  # both orders occur across seeds


def test_sessions_cover_all_samples_deduped():
    proto = build_default_protocol()
    plans = build_sessions(proto, seed=7, sessions_per_sample=2)
    sample_ids = {a.sample_id for p in plans for a in p.assignments}
    assert sample_ids == {s.sample_id for s in proto.samples}
    # dedup: same sample+seed never repeats within a plan set
    keys = [f"{a.sample_id}:{p.seed}" for p in plans for a in p.assignments]
    assert len(keys) == len(set(keys))


def test_build_sessions_deterministic():
    proto = build_default_protocol()
    assert build_sessions(proto, seed=3) == build_sessions(proto, seed=3)
