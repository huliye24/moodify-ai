"""Loudness matching validation tests (MFY_MOBILE_LISTENING_VALIDATION_001)."""

from __future__ import annotations

import numpy as np
import pytest

from moodify.listening.loudness_match import verify_level_match
from moodify.listening.protocol import LEVEL_MATCH_DB_MAX, SWITCH_LATENCY_MS_MAX

pytestmark = pytest.mark.v01

SR = 44100


def test_matched_pair_passes():
    t = np.arange(SR) / SR
    a = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    b = (0.3 * np.sin(2 * np.pi * 440 * t) + 1e-4).astype(np.float32)  # near identical
    r = verify_level_match(a, b, SR)
    assert r.passed
    assert abs(r.loudness_diff_db) <= LEVEL_MATCH_DB_MAX


def test_mismatched_pair_fails():
    t = np.arange(SR) / SR
    a = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    b = (0.15 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)  # -6 dB
    r = verify_level_match(a, b, SR)
    assert not r.passed
    assert abs(r.loudness_diff_db) > LEVEL_MATCH_DB_MAX


def test_shape_mismatch_fails():
    a = np.zeros((1000,), dtype=np.float32)
    b = np.zeros((999,), dtype=np.float32)
    r = verify_level_match(a, b, SR)
    assert not r.passed
    assert r.reason == "shape mismatch"


def test_switch_latency_threshold():
    t = np.arange(SR) / SR
    a = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    ok = verify_level_match(a, a.copy(), SR, switch_latency_ms=SWITCH_LATENCY_MS_MAX)
    assert ok.passed
    bad = verify_level_match(a, a.copy(), SR, switch_latency_ms=SWITCH_LATENCY_MS_MAX + 1)
    assert not bad.passed
