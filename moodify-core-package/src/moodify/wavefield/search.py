"""Deterministic field search policy v0.

There is no AI search in v0 and none is faked.  The policy is a fixed,
versioned list of three probes spanning one axis — **spatial scale**:

```text
A = smaller / more direct field
B = medium field
C = larger / more open field
```

This is the first direct implementation of "the same waveform can be placed in
different field sizes".

**These numbers are engineering probes, not calibrated truth.**  They were
chosen in-repo; no listening calibration was performed; the code, the search
record and the manifest all say ``UNCALIBRATED_ENGINEERING_DEFAULT``.  A future
AI search replaces this policy without changing the field record format —
that is the whole point of keeping the policy separate from ``FieldSpec``.
"""

from __future__ import annotations

from collections.abc import Mapping

from moodify.wavefield.models import (
    SEARCH_SCHEMA,
    FieldSpec,
    field_specs_from,
)

POLICY_ID = "FIELD_SEARCH_POLICY_V0"
POLICY_VERSION = 0
CALIBRATION_STATUS = "UNCALIBRATED_ENGINEERING_DEFAULT"

POLICY_NOTE = (
    "Engineering probes on the spatial-scale axis. Uncalibrated: no listening "
    "experiment has fixed these values, and they must not be consumed as "
    "calibrated limits or promoted into a preset product surface. A/B/C are "
    "probes of the search policy, not permanent presets."
)

#: Frozen starting values.  ``room_size`` is the axis; the other three are
#: coherent companions so each probe is a *whole* field rather than an
#: arbitrary point.
FIELD_SEARCH_POLICY_V0: dict = {
    "schema": SEARCH_SCHEMA,
    "policy_id": POLICY_ID,
    "policy_version": POLICY_VERSION,
    "calibration_status": CALIBRATION_STATUS,
    "axis": "spatial_scale",
    "note": POLICY_NOTE,
    "probes": (
        {
            "candidate_id": "A",
            "field_id": "field_A",
            "intent": "smaller / more direct field",
            "engine": "algorithmic_room_v0",
            "parameters": {
                "room_size": 0.22,
                "damping": 0.62,
                "wet": 0.08,
                "width": 0.72,
            },
        },
        {
            "candidate_id": "B",
            "field_id": "field_B",
            "intent": "medium field",
            "engine": "algorithmic_room_v0",
            "parameters": {
                "room_size": 0.50,
                "damping": 0.50,
                "wet": 0.16,
                "width": 0.86,
            },
        },
        {
            "candidate_id": "C",
            "field_id": "field_C",
            "intent": "larger / more open field",
            "engine": "algorithmic_room_v0",
            "parameters": {
                "room_size": 0.80,
                "damping": 0.40,
                "wet": 0.24,
                "width": 1.00,
            },
        },
    ),
}

#: Which candidate each probe is.  Kept explicit so nothing has to guess an
#: ordering from a container type.
PROBE_CANDIDATES: tuple[str, ...] = tuple(
    str(probe["candidate_id"]) for probe in FIELD_SEARCH_POLICY_V0["probes"]
)


def policy_document() -> dict:
    """JSON-ready copy of the policy (tuples become lists)."""
    return {
        **{key: value for key, value in FIELD_SEARCH_POLICY_V0.items() if key != "probes"},
        "probes": [dict(probe, parameters=dict(probe["parameters"])) for probe in FIELD_SEARCH_POLICY_V0["probes"]],
    }


def probe_fields() -> list[FieldSpec]:
    """The three probes as validated :class:`FieldSpec` objects, in A/B/C order."""
    return field_specs_from(FIELD_SEARCH_POLICY_V0["probes"])


def probe_by_candidate() -> dict[str, Mapping]:
    return {str(probe["candidate_id"]): probe for probe in FIELD_SEARCH_POLICY_V0["probes"]}


def parameters_for(candidate_id: str) -> dict[str, float]:
    try:
        return dict(probe_by_candidate()[candidate_id]["parameters"])
    except KeyError as exc:
        raise KeyError(f"no v0 probe for candidate {candidate_id!r}") from exc


# ---------------------------------------------------------------------------
# Running the search
# ---------------------------------------------------------------------------


def run_field_search(
    case_dir,
    *,
    source_path: str,
    policy: Mapping | None = None,
    hear: bool = True,
) -> dict:
    """Render every v0 probe from ``source_path`` into the case, then hear them.

    Orchestration only — rendering lives in :mod:`moodify.wavefield.renderer`
    and hearing in :mod:`moodify.wavefield.hearing`.  The source is measured
    exactly once and reused as the baseline for every candidate, so all
    candidates are compared against one and the same ORIGINAL.

    Deterministic: same source + same policy + same library versions produce
    byte-identical candidates.
    """
    from pathlib import Path

    from moodify.audio_io import load_audio
    from moodify.wavefield import record as record_mod
    from moodify.wavefield.hearing import hear_snapshot, measure_audio
    from moodify.wavefield.renderer import render_file, sha256_file

    document = dict(policy or FIELD_SEARCH_POLICY_V0)
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(str(source))

    source_samples, source_sr = load_audio(str(source), always_2d=False)
    source_metrics = measure_audio(source_samples, source_sr) if hear else None
    source_sha = sha256_file(source)

    frames = int(source_samples.shape[0])
    record_mod.write_session(
        case_dir,
        source_path=str(source),
        source_sha256=source_sha,
        sample_rate=source_sr,
        channels=1 if source_samples.ndim == 1 else int(source_samples.shape[1]),
        frames=frames,
        duration_seconds=round(frames / float(source_sr), 6),
        policy=document,
    )

    renders: dict[str, dict] = {}
    for probe, spec in zip(document["probes"], field_specs_from(document["probes"]), strict=True):
        candidate_id = str(probe["candidate_id"])
        record_mod.write_field(case_dir, candidate_id, spec)
        target = record_mod.candidate_path(case_dir, candidate_id)
        render = render_file(source, spec, target)
        record_mod.write_render(case_dir, candidate_id, render)
        renders[candidate_id] = render.to_dict()

        if hear:
            candidate_samples, _ = load_audio(str(target), always_2d=False)
            snapshot = hear_snapshot(
                candidate_id=candidate_id,
                field_id=spec.field_id,
                candidate_samples=candidate_samples,
                candidate_sample_rate=render.sample_rate,
                source_samples=source_samples,
                source_sample_rate=source_sr,
                source_sha256=source_sha,
                candidate_sha256=render.output_sha256,
                render_result=render.to_dict(),
                source_metrics=source_metrics,
            )
            record_mod.write_hearing(case_dir, candidate_id, snapshot)

    if hear:
        original = hear_snapshot(
            candidate_id="ORIGINAL",
            field_id=None,
            candidate_samples=source_samples,
            candidate_sample_rate=source_sr,
            source_samples=source_samples,
            source_sample_rate=source_sr,
            source_sha256=source_sha,
            candidate_sha256=source_sha,
            is_reference=True,
        )
        record_mod.write_hearing(case_dir, "ORIGINAL", original)

    state = record_mod.inspect(case_dir)
    state["renders"] = renders
    return state
