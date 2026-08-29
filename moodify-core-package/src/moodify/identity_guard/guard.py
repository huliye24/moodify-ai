"""Identity Guard engine v0.1 (MFY-CR-P05).

Per-candidate source-vs-candidate comparison across six dimensions with veto
semantics:

    Any REJECT                     -> REJECT
    Any HUMAN_REQUIRED or
      critical-unmeasured + change -> HUMAN_REQUIRED
    Any CAUTION (all measured)     -> PASS_WITH_CAUTION
    otherwise                      -> PASS

No averaging; a critical identity failure can never be averaged away.
"""

from __future__ import annotations

from moodify.identity_guard.contract import (
    GuardState,
    IdentityDelta,
    IdentityDimension,
    IdentityVerdict,
)
from moodify.identity_guard.thresholds import IDENTITY_GUARD_POLICY_V1

_POLICY = IDENTITY_GUARD_POLICY_V1["dimensions"]


def _value(metrics: dict, name: str) -> float | None:
    entry = metrics.get(name)
    if not isinstance(entry, dict):
        return None
    value = entry.get("value")
    return value if isinstance(value, (int, float)) else None


def _delta(source: dict, candidate: dict, name: str) -> tuple[float | None, float | None, float | None]:
    s, c = _value(source, name), _value(candidate, name)
    if s is None or c is None:
        return None, None, None
    return c - s, s, c


# ---------------------------------------------------------------------------
# Per-dimension guards
# ---------------------------------------------------------------------------

def _guard_vocal_mid(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-01 — PROXY only. Drift beyond budget needs human ears; never REJECT."""
    refs: list[str] = []
    worst = 0.0
    for budget_key, budget in dim_cfg["budgets"].items():
        metric = budget_key[:-4] if budget_key.endswith("_abs") else budget_key
        d, s, c = _delta(source, candidate, metric)
        if d is None:
            continue
        refs.append(metric)
        worst = max(worst, abs(d) / budget["value"])
    if not refs:
        return _delta_not_measurable(IdentityDimension.IG_01_VOCAL_MID, ctx,
                                     "mid-band proxy metrics missing")
    if worst > 1.0:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_01_VOCAL_MID,
            guard_state=GuardState.HUMAN_REQUIRED,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="LOW",
            human_review_required=True,
            notes="mid-band proxies drifted beyond budget; PROXY only — cannot "
                  "distinguish artistic change from identity drift without human ears",
        )
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_01_VOCAL_MID,
        guard_state=GuardState.PASS,
        measurement_refs=tuple(refs),
        normalized_delta=round(worst, 3),
        confidence="LOW",
        notes="mid-band character within proxy budget",
    )


def _guard_dynamics(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-02 — MEASURABLE. Severe dynamic flattening is a hard reject."""
    refs: list[str] = []
    worst_ratio = 0.0
    worst_metric = ""
    for metric, budget in dim_cfg["budgets"].items():
        d, s, c = _delta(source, candidate, metric)
        if d is None or budget["value"] == 0:
            continue
        refs.append(metric)
        ratio = d / budget["value"]  # negative delta / negative budget -> positive ratio
        if ratio > worst_ratio:
            worst_ratio, worst_metric = ratio, metric
    if not refs:
        return _delta_not_measurable(IdentityDimension.IG_02_DYNAMICS, ctx,
                                     "dynamic metrics missing")
    if worst_ratio > 1.0:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_02_DYNAMICS,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst_ratio, 3),
            confidence="MEDIUM",
            notes=f"severe dynamic flattening ({worst_metric} beyond budget)",
        )
    if worst_ratio > dim_cfg["caution_factor"]:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_02_DYNAMICS,
            guard_state=GuardState.CAUTION,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst_ratio, 3),
            confidence="MEDIUM",
            notes="dynamic change approaching budget",
        )
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_02_DYNAMICS,
        guard_state=GuardState.PASS,
        measurement_refs=tuple(refs),
        normalized_delta=round(worst_ratio, 3),
        confidence="MEDIUM",
        notes="dynamic character within budget",
    )


def _guard_reverb(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-03 — NOT_MEASURABLE in v0.1 (no validated decay/late-energy detector)."""
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_03_REVERB_SPACE,
        guard_state=GuardState.NOT_MEASURABLE,
        measurement_refs=(),
        confidence="LOW",
        human_review_required=False,
        notes="NOT_MEASURABLE_V0_1 — no validated reverb/space detector; "
              "critical-unmeasured dimension forces human ear check when any "
              "other dimension shows change",
    )


def _guard_stereo(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-04 — MEASURABLE. Artificial widening and mono-identity break are hard rejects."""
    refs: list[str] = []
    worst = 0.0
    for metric, budget in dim_cfg["budgets"].items():
        d, s, c = _delta(source, candidate, metric)
        if d is None:
            continue
        refs.append(metric)
        worst = max(worst, d / budget["value"])
    mono_guard = dim_cfg["mono_guard"]
    s_corr = _value(source, "stereo_correlation")
    c_corr = _value(candidate, "stereo_correlation")
    mono_break = (
        s_corr is not None and c_corr is not None
        and s_corr >= mono_guard["source_correlation_min"]
        and c_corr <= mono_guard["candidate_correlation_max"]
    )
    if mono_break:
        refs.append("stereo_correlation")
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_04_STEREO,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            source_value=round(s_corr, 4), candidate_value=round(c_corr, 4),
            normalized_delta=1.0,
            confidence="MEDIUM",
            notes="mono/narrow source widened beyond mono guard; mono identity "
                  "must stay legal, widening it is not a default improvement",
        )
    if worst > 1.0:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_04_STEREO,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="stereo width beyond tested boundary",
        )
    if worst > 0.6:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_04_STEREO,
            guard_state=GuardState.CAUTION,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="stereo change approaching budget",
        )
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_04_STEREO,
        guard_state=GuardState.PASS,
        measurement_refs=tuple(refs),
        normalized_delta=round(worst, 3),
        confidence="MEDIUM",
        notes="stereo character within budget",
    )


def _guard_low_end(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-05 — MEASURABLE. Modern bass inflation is a hard reject."""
    refs: list[str] = []
    worst = 0.0
    for metric, budget in dim_cfg["budgets"].items():
        d, s, c = _delta(source, candidate, metric)
        if d is None:
            continue
        refs.append(metric)
        worst = max(worst, d / budget["value"])
    if not refs:
        return _delta_not_measurable(IdentityDimension.IG_05_LOW_END, ctx,
                                     "low-end band metrics missing")
    if worst > 1.0:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_05_LOW_END,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="low-end boosted beyond budget (modern bass inflation guard)",
        )
    if worst > 0.6:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_05_LOW_END,
            guard_state=GuardState.CAUTION,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="low-end change approaching budget",
        )
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_05_LOW_END,
        guard_state=GuardState.PASS,
        measurement_refs=tuple(refs),
        normalized_delta=round(worst, 3),
        confidence="MEDIUM",
        notes="low-end character within budget",
    )


def _guard_loudness(source: dict, candidate: dict, dim_cfg: dict, ctx: dict) -> IdentityDelta:
    """IG-06 — MEASURABLE. Loudness war and new clipping are hard rejects."""
    refs: list[str] = []
    d, s, c = _delta(source, candidate, "integrated_lufs")
    worst = 0.0
    if d is not None:
        refs.append("integrated_lufs")
        worst = abs(d) / dim_cfg["budgets"]["integrated_lufs"]["value"]
    s_clip, c_clip = _value(source, "clipping_sample_ratio"), _value(candidate, "clipping_sample_ratio")
    new_clip = (
        c_clip is not None and s_clip is not None
        and c_clip - s_clip >= dim_cfg["clipping_guard"]["new_clipping_min_ratio"]
    )
    if new_clip:
        refs.append("clipping_sample_ratio")
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_06_LOUDNESS_DENSITY,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            source_value=round(s_clip, 6), candidate_value=round(c_clip, 6),
            normalized_delta=1.0,
            confidence="HIGH",
            notes="new clipping introduced in candidate (hard reject)",
        )
    if worst > 1.0:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_06_LOUDNESS_DENSITY,
            guard_state=GuardState.REJECT,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="extreme loudness jump beyond budget",
        )
    if worst > dim_cfg["budgets"]["caution_lufs"]["value"] / dim_cfg["budgets"]["integrated_lufs"]["value"]:
        return IdentityDelta(
            candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
            dimension=IdentityDimension.IG_06_LOUDNESS_DENSITY,
            guard_state=GuardState.CAUTION,
            measurement_refs=tuple(refs),
            normalized_delta=round(worst, 3),
            confidence="MEDIUM",
            notes="loudness change approaching budget",
        )
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=IdentityDimension.IG_06_LOUDNESS_DENSITY,
        guard_state=GuardState.PASS,
        measurement_refs=tuple(refs),
        normalized_delta=round(worst, 3),
        confidence="MEDIUM",
        notes="loudness/density within budget",
    )


def _delta_not_measurable(dimension: IdentityDimension, ctx: dict, note: str) -> IdentityDelta:
    return IdentityDelta(
        candidate_id=ctx["candidate_id"], source_id=ctx["source_id"],
        dimension=dimension, guard_state=GuardState.NOT_MEASURABLE,
        measurement_refs=(), confidence="LOW", notes=note,
    )


_DIMENSION_GUARDS = {
    IdentityDimension.IG_01_VOCAL_MID: _guard_vocal_mid,
    IdentityDimension.IG_02_DYNAMICS: _guard_dynamics,
    IdentityDimension.IG_03_REVERB_SPACE: _guard_reverb,
    IdentityDimension.IG_04_STEREO: _guard_stereo,
    IdentityDimension.IG_05_LOW_END: _guard_low_end,
    IdentityDimension.IG_06_LOUDNESS_DENSITY: _guard_loudness,
}


def guard_candidate(
    source_metrics: dict,
    candidate_metrics: dict,
    *,
    candidate_id: str = "candidate",
    source_id: str = "source",
) -> IdentityVerdict:
    """Run the Identity Guard on one source/candidate metric pair.

    Inputs are standard metric records (the dict shape produced by
    ``moodify.auditory.metrics.compute_metrics``). Returns the overall verdict
    with per-dimension deltas. No verdict grants processing authority by
    itself; SOURCE always remains an eligible result.
    """
    ctx = {"candidate_id": candidate_id, "source_id": source_id}
    deltas: list[IdentityDelta] = []
    for dimension in IdentityDimension:
        cfg = _POLICY[dimension.value]
        if cfg["capability"] == "NOT_MEASURABLE":
            deltas.append(_guard_reverb(source_metrics, candidate_metrics, cfg, ctx))
        else:
            deltas.append(_DIMENSION_GUARDS[dimension](source_metrics, candidate_metrics, cfg, ctx))

    states = [d.guard_state for d in deltas]
    any_change = any(
        d.guard_state in {GuardState.CAUTION, GuardState.HUMAN_REQUIRED, GuardState.REJECT}
        for d in deltas
    )
    unmeasured_critical = any(
        d.dimension == IdentityDimension.IG_03_REVERB_SPACE
        for d in deltas
    )

    if GuardState.REJECT in states:
        state = GuardState.REJECT
    elif GuardState.HUMAN_REQUIRED in states or (unmeasured_critical and any_change):
        state = GuardState.HUMAN_REQUIRED
        question = (
            "Q1. Does this still sound like the same recording? "
            "Q2. Did any core character disappear? "
            "Q3. Does anything sound artificially modernized? "
            "Q4. Is the improvement worth the change? "
            "Q5. SOURCE / A / B / C preference?"
        )
    elif GuardState.CAUTION in states:
        state = GuardState.CAUTION
    else:
        state = GuardState.PASS

    return IdentityVerdict(
        candidate_id=candidate_id,
        source_id=source_id,
        state=state,
        deltas=tuple(deltas),
        human_review_question=question if state == GuardState.HUMAN_REQUIRED else "",
    )
