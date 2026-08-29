"""Preregistered protocol tests (MFY_MOBILE_LISTENING_VALIDATION_001)."""

from __future__ import annotations

import pytest

from moodify.listening.protocol import (
    build_default_protocol,
    freeze_protocol,
    hash_protocol,
)

pytestmark = pytest.mark.v01


def test_default_protocol_contains_all_three_kinds():
    proto = build_default_protocol()
    kinds = {s.kind for s in proto.samples}
    assert "legitimate" in kinds
    assert "negative_control" in kinds
    assert "placebo_bypass" in kinds


def test_protocol_hash_deterministic():
    a = build_default_protocol()
    b = build_default_protocol()
    assert hash_protocol(a) == hash_protocol(b)
    assert len(hash_protocol(a)) == 64


def test_freeze_sets_hash_matching():
    proto = freeze_protocol(build_default_protocol())
    assert proto.frozen_sha256 == hash_protocol(proto)
    # hash must be stable across the frozen payload
    assert proto.frozen_sha256 == hash_protocol(build_default_protocol())


def test_endpoints_are_separate_never_merged():
    proto = build_default_protocol()
    assert proto.endpoints == ("preference", "identity_kept", "difference_audible")


def test_candidates_frozen_from_71():
    proto = build_default_protocol()
    assert proto.primitives == ("dc_offset_fix", "clip_peak_repair")
    assert proto.candidates_frozen == "mfy-intervention-v1"


def test_negative_control_expected_bypassed():
    proto = build_default_protocol()
    neg = next(s for s in proto.samples if s.kind == "negative_control")
    assert neg.expected_decision == "BYPASSED"
    placebo = next(s for s in proto.samples if s.kind == "placebo_bypass")
    assert placebo.processed_wav is None  # replayed input, no processing
