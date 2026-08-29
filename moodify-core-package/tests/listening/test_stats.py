"""Statistics engine tests (MFY_MOBILE_LISTENING_VALIDATION_001).

Engine self-test uses SYNTHETIC data only — human judgments are never
fabricated; real sessions stay PENDING per user instruction.
"""

from __future__ import annotations

import pytest

from moodify.listening.stats import analyze_three_endpoints, binomial_ci, preference_test

pytestmark = pytest.mark.v01


def test_binomial_ci_reasonable():
    lo, hi = binomial_ci(100, 80)
    assert lo < 0.8 < hi
    assert 0.0 <= lo <= hi <= 1.0
    lo2, hi2 = binomial_ci(0, 0)
    assert lo2 == 0.0 and hi2 == 0.0


def test_clear_preference_passes():
    r = preference_test(favorable=80, n=100, threshold=0.55)
    assert r.passed
    assert r.proportion == 0.8
    assert r.p_value < 0.05
    assert r.effect_size > 0.5


def test_no_preference_fails():
    r = preference_test(favorable=52, n=100, threshold=0.55)
    assert not r.passed
    assert r.p_value > 0.05


def test_no_data_is_data_pending():
    report = analyze_three_endpoints(0, 0, 0, 0, preference_threshold=0.55)
    assert report.verdict == "DATA_PENDING"
    for r in report.results:
        assert r.n == 0


def test_three_endpoints_reported_separately():
    report = analyze_three_endpoints(
        n=60, prefer_moodify=45, identity_kept=55, difference_audible=40,
        preference_threshold=0.55,
    )
    assert report.verdict == "PASS"
    names = [r.endpoint for r in report.results]
    assert names == ["preference", "identity_kept", "difference_audible"]
    # identity kept reported on its own proportion (55/60 = 0.92)
    identity = report.results[1]
    assert identity.proportion == pytest.approx(55 / 60)
    assert identity.passed


def test_insufficient_reverts_to_71_not_lower_threshold():
    report = analyze_three_endpoints(
        n=60, prefer_moodify=30, identity_kept=50, difference_audible=20,
        preference_threshold=0.55,
    )
    assert report.verdict == "INSUFFICIENT"
