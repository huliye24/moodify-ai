"""Statistical significance evaluator for the multi-night learning store.

Compares night groups, separates stable signal from noise, reports effect sizes.
Deterministic, fixed seed, no ML training.
Part of ECHAIN-MOODIFY-MULTI-NIGHT-STORE-016 / MHP-907.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .learning_store import load_store, NightRecord


@dataclass
class GroupStats:
    label: str
    n: int
    eds_mean: float | None
    eds_std: float | None
    elapsed_mean: float | None
    elapsed_std: float | None


@dataclass
class SignificanceResult:
    test: str
    metric: str
    group_a_label: str
    group_b_label: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    diff: float
    effect_size: float
    effect_label: str
    p_value_approx: float | None
    signal: str  # "signal" | "noise" | "insufficient_data"


@dataclass
class SignificanceReport:
    group_a: GroupStats
    group_b: GroupStats
    results: list[SignificanceResult] = field(default_factory=list)
    generated_at: str = ""
    notes: list[str] = field(default_factory=list)


def _mean_std(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    if n == 1:
        return mean, 0.0
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return mean, math.sqrt(variance)


def _cohens_d(mean_a: float, std_a: float, n_a: int, mean_b: float, std_b: float, n_b: int) -> float:
    if n_a < 2 or n_b < 2:
        return 0.0
    pooled_var = ((n_a - 1) * std_a ** 2 + (n_b - 1) * std_b ** 2) / (n_a + n_b - 2)
    if pooled_var <= 0:
        return 0.0
    return abs(mean_a - mean_b) / math.sqrt(pooled_var)


def _effect_label(d: float) -> str:
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def _approx_mann_whitney_p(a_vals: list[float], b_vals: list[float]) -> float | None:
    """Deterministic rank-based approximate p-value via U-statistic normal approximation."""
    if len(a_vals) < 3 or len(b_vals) < 3:
        return None
    combined = [(v, 0) for v in a_vals] + [(v, 1) for v in b_vals]
    combined.sort(key=lambda x: x[0])
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    r1 = sum(ranks[k] for k, (v, g) in enumerate(combined) if g == 0)
    n1, n2 = len(a_vals), len(b_vals)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2.0
    # tie correction
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma == 0:
        return None
    z = abs((u - mu) / sigma)
    # Normal approximation (one-sided → two-sided)
    p = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(z / math.sqrt(2.0))))
    return round(min(p, 1.0), 4)


def compare_groups(
    records: list[NightRecord],
    group_a_label: str = "recent",
    group_b_label: str = "baseline",
    split_index: int | None = None,
) -> SignificanceReport:
    if split_index is None:
        split_index = max(1, len(records) // 2)

    a_records = records[split_index:]
    b_records = records[:split_index]

    a_eds = [r.avg_eds for r in a_records if r.avg_eds is not None]
    b_eds = [r.avg_eds for r in b_records if r.avg_eds is not None]
    a_elapsed = [r.avg_elapsed_s for r in a_records if r.avg_elapsed_s is not None]
    b_elapsed = [r.avg_elapsed_s for r in b_records if r.avg_elapsed_s is not None]

    a_eds_mean, a_eds_std = _mean_std(a_eds)
    b_eds_mean, b_eds_std = _mean_std(b_eds)
    a_el_mean, a_el_std = _mean_std(a_elapsed)
    b_el_mean, b_el_std = _mean_std(b_elapsed)

    group_a = GroupStats(
        label=group_a_label, n=len(a_records),
        eds_mean=round(a_eds_mean, 2) if a_eds else None,
        eds_std=round(a_eds_std, 2) if a_eds else None,
        elapsed_mean=round(a_el_mean, 2) if a_elapsed else None,
        elapsed_std=round(a_el_std, 2) if a_elapsed else None,
    )
    group_b = GroupStats(
        label=group_b_label, n=len(b_records),
        eds_mean=round(b_eds_mean, 2) if b_eds else None,
        eds_std=round(b_eds_std, 2) if b_eds else None,
        elapsed_mean=round(b_el_mean, 2) if b_elapsed else None,
        elapsed_std=round(b_el_std, 2) if b_elapsed else None,
    )

    results: list[SignificanceResult] = []
    notes: list[str] = []

    for metric, a_mean, a_std, b_mean, b_std, a_vals, b_vals in [
        ("eds", a_eds_mean, a_eds_std, b_eds_mean, b_eds_std, a_eds, b_eds),
        ("elapsed_s", a_el_mean, a_el_std, b_el_mean, b_el_std, a_elapsed, b_elapsed),
    ]:
        if not a_vals or not b_vals:
            results.append(SignificanceResult(
                test="n/a", metric=metric,
                group_a_label=group_a_label, group_b_label=group_b_label,
                n_a=len(a_vals), n_b=len(b_vals),
                mean_a=a_mean, mean_b=b_mean, diff=round(a_mean - b_mean, 2),
                effect_size=0.0, effect_label="insufficient_data",
                p_value_approx=None, signal="insufficient_data",
            ))
            notes.append(f"{metric}: insufficient data for comparison")
            continue

        d = _cohens_d(a_mean, a_std, len(a_vals), b_mean, b_std, len(b_vals))
        p = _approx_mann_whitney_p(a_vals, b_vals)
        diff = round(a_mean - b_mean, 2)

        if d >= 0.5 and (p is None or p < 0.1):
            signal = "signal"
        elif d < 0.2:
            signal = "noise"
        else:
            signal = "signal" if d >= 0.5 else "noise"

        results.append(SignificanceResult(
            test="Mann-Whitney U (approx)",
            metric=metric, group_a_label=group_a_label, group_b_label=group_b_label,
            n_a=len(a_vals), n_b=len(b_vals),
            mean_a=a_mean, mean_b=b_mean, diff=diff,
            effect_size=round(d, 3), effect_label=_effect_label(d),
            p_value_approx=p, signal=signal,
        ))

    return SignificanceReport(
        group_a=group_a, group_b=group_b,
        results=results, notes=notes,
        generated_at=_utc_now_iso(),
    )


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def evaluate_store(store_path: Path, split_index: int | None = None) -> SignificanceReport:
    records = load_store(store_path)
    records.sort(key=lambda r: r.night_label)
    return compare_groups(records, split_index=split_index)


def format_significance_json(report: SignificanceReport) -> str:
    return json.dumps({
        "generated_at": report.generated_at,
        "group_a": {
            "label": report.group_a.label, "n": report.group_a.n,
            "eds_mean": report.group_a.eds_mean, "eds_std": report.group_a.eds_std,
            "elapsed_mean": report.group_a.elapsed_mean, "elapsed_std": report.group_a.elapsed_std,
        },
        "group_b": {
            "label": report.group_b.label, "n": report.group_b.n,
            "eds_mean": report.group_b.eds_mean, "eds_std": report.group_b.eds_std,
            "elapsed_mean": report.group_b.elapsed_mean, "elapsed_std": report.group_b.elapsed_std,
        },
        "results": [{
            "metric": r.metric, "test": r.test,
            "n_a": r.n_a, "n_b": r.n_b,
            "mean_a": r.mean_a, "mean_b": r.mean_b, "diff": r.diff,
            "effect_size": r.effect_size, "effect_label": r.effect_label,
            "p_value_approx": r.p_value_approx, "signal": r.signal,
        } for r in report.results],
        "notes": report.notes,
    }, ensure_ascii=False, indent=2)


def format_significance_markdown(report: SignificanceReport) -> str:
    lines = [
        "# Statistical Significance Report",
        "",
        f"**Generated**: {report.generated_at}",
        "",
        "## Groups",
        "",
        f"| Group | N | EDS Mean | EDS Std | Elapsed Mean | Elapsed Std |",
        f"|---|---|---|---|---|---|",
    ]
    for g in [report.group_a, report.group_b]:
        lines.append(
            f"| {g.label} | {g.n} | "
            f"{g.eds_mean if g.eds_mean is not None else '-'} | "
            f"{g.eds_std if g.eds_std is not None else '-'} | "
            f"{g.elapsed_mean if g.elapsed_mean is not None else '-'} | "
            f"{g.elapsed_std if g.elapsed_std is not None else '-'} |"
        )
    lines.extend(["", "## Comparisons", ""])
    for r in report.results:
        lines.extend([
            f"### {r.metric}",
            f"- **Diff**: {r.diff:.2f} ({r.group_a_label} vs {r.group_b_label})",
            f"- **Effect size**: d={r.effect_size:.3f} ({r.effect_label})",
            f"- **Signal**: **{r.signal.upper()}**",
            f"- **n**: {r.n_a} vs {r.n_b}",
        ])
        if r.p_value_approx is not None:
            lines.append(f"- **p ≈**: {r.p_value_approx}")
        lines.append("")
    if report.notes:
        lines.append("## Notes")
        for n in report.notes:
            lines.append(f"- {n}")
    return "\n".join(lines)
