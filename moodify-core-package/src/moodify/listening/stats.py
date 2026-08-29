"""Statistics engine (MFY_MOBILE_LISTENING_VALIDATION_001).

Reports the three endpoints SEPARATELY (preference / identity kept /
difference audible) — never a merged mystery score. Effect size, confidence
interval and a binomial test are reported with uncertainty. If the threshold
is not reached, the verdict says so: return to 71, never lower the threshold.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from moodify.listening.protocol import ALPHA


@dataclass(frozen=True)
class EndpointResult:
    endpoint: str
    n: int
    favorable: int
    proportion: float
    ci_low: float
    ci_high: float
    p_value: float
    effect_size: float  # Cohen's h for proportions
    passed: bool


@dataclass(frozen=True)
class StatisticalReport:
    results: tuple[EndpointResult, ...]
    verdict: str  # PASS / INSUFFICIENT / DATA_PENDING


def binomial_ci(n: int, k: int, alpha: float = ALPHA) -> tuple[float, float]:
    """Wilson score interval for a proportion."""
    if n == 0:
        return 0.0, 0.0
    z = 1.959963984540054 if alpha == 0.05 else 2.5758293035489004  # 95% / 99%
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size between two proportions (0.5 baseline for binary)."""
    def _asin(p: float) -> float:
        return 2.0 * math.asin(math.sqrt(max(0.0, min(1.0, p))))

    return _asin(p1) - _asin(p2)


def _binomial_p(n: int, k: int, p0: float = 0.5) -> float:
    """Two-sided exact binomial test p-value."""
    if n == 0:
        return 1.0
    from scipy import stats

    return float(stats.binomtest(k, n, p0, alternative="two-sided").pvalue)


def preference_test(favorable: int, n: int, threshold: float, alpha: float = ALPHA) -> EndpointResult:
    """Main endpoint: proportion of 'prefer Moodify' judgments against threshold.

    threshold (e.g. 0.55) is frozen in the protocol; missing it is a fail —
    the threshold is never lowered.
    """
    p = favorable / n if n > 0 else 0.0
    lo, hi = binomial_ci(n, favorable, alpha)
    p_value = _binomial_p(n, favorable)
    h = cohens_h(p, 0.5)
    passed = n > 0 and p >= threshold and p_value < alpha
    return EndpointResult("preference", n, favorable, p, lo, hi, p_value, h, passed)


def analyze_three_endpoints(
    n: int,
    prefer_moodify: int,
    identity_kept: int,
    difference_audible: int,
    preference_threshold: float,
    alpha: float = ALPHA,
) -> StatisticalReport:
    """Separate analysis of the three endpoints — never merged."""
    results = (
        preference_test(prefer_moodify, n, preference_threshold, alpha),
        EndpointResult(
            "identity_kept", n, identity_kept, identity_kept / n if n else 0.0,
            *binomial_ci(n, identity_kept, alpha),
            _binomial_p(n, identity_kept), cohens_h(identity_kept / n if n else 0.0, 0.5),
            n > 0 and identity_kept / n >= 0.8,
        ),
        EndpointResult(
            "difference_audible", n, difference_audible, difference_audible / n if n else 0.0,
            *binomial_ci(n, difference_audible, alpha),
            _binomial_p(n, difference_audible), cohens_h(difference_audible / n if n else 0.0, 0.5),
            n > 0,  # audibility is descriptive, not a pass/fail gate
        ),
    )
    if n == 0:
        verdict = "DATA_PENDING"
    elif not results[0].passed:
        verdict = "INSUFFICIENT"
    else:
        verdict = "PASS"
    return StatisticalReport(results, verdict)
