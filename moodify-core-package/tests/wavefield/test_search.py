"""FIELD_SEARCH_POLICY_V0 — deterministic, sealed, and honest about calibration."""

from __future__ import annotations

import numpy as np
import soundfile as sf

from moodify.wavefield.models import PARAMETER_BOUNDS
from moodify.wavefield.renderer import render_array
from moodify.wavefield.search import (
    CALIBRATION_STATUS,
    FIELD_SEARCH_POLICY_V0,
    POLICY_ID,
    POLICY_VERSION,
    parameters_for,
    policy_document,
    probe_by_candidate,
    probe_fields,
    run_field_search,
)


def test_policy_is_named_and_versioned():
    assert POLICY_ID == "FIELD_SEARCH_POLICY_V0"
    assert POLICY_VERSION == 0
    assert FIELD_SEARCH_POLICY_V0["policy_id"] == POLICY_ID
    assert FIELD_SEARCH_POLICY_V0["axis"] == "spatial_scale"


def test_policy_is_explicitly_uncalibrated():
    assert CALIBRATION_STATUS == "UNCALIBRATED_ENGINEERING_DEFAULT"
    assert FIELD_SEARCH_POLICY_V0["calibration_status"] == CALIBRATION_STATUS
    note = FIELD_SEARCH_POLICY_V0["note"].lower()
    assert "uncalibrated" in note
    assert "preset" in note, "A/B/C must be declared probes, not presets"


def test_probes_are_exactly_a_b_c():
    assert [p["candidate_id"] for p in FIELD_SEARCH_POLICY_V0["probes"]] == ["A", "B", "C"]
    assert [f.field_id for f in probe_fields()] == ["field_A", "field_B", "field_C"]


def test_room_size_increases_monotonically_with_field_size():
    sizes = [probe_by_candidate()[c]["parameters"]["room_size"] for c in "ABC"]
    assert sizes == sorted(sizes)
    assert sizes[0] < sizes[1] < sizes[2]


def test_probes_are_meaningfully_different():
    """Not decorative: the axis must actually move."""
    a, b, c = (p["parameters"] for p in FIELD_SEARCH_POLICY_V0["probes"])
    assert abs(c["room_size"] - a["room_size"]) >= 0.4
    assert abs(c["wet"] - a["wet"]) >= 0.10
    assert abs(c["width"] - a["width"]) >= 0.20
    assert a != b != c


def test_probes_stay_inside_the_declared_parameter_bounds():
    for probe in FIELD_SEARCH_POLICY_V0["probes"]:
        for key, value in probe["parameters"].items():
            low, high = PARAMETER_BOUNDS[key]
            assert low <= value <= high, f"{probe['candidate_id']}.{key}={value}"


def test_probe_fields_are_validated_specs():
    for field, probe in zip(probe_fields(), FIELD_SEARCH_POLICY_V0["probes"], strict=True):
        assert field.parameters == probe["parameters"]
        assert field.engine == probe["engine"]


def test_policy_is_sealed_against_accidental_mutation():
    """The tuple container makes the frozen policy structurally read-only."""
    assert isinstance(FIELD_SEARCH_POLICY_V0["probes"], tuple)
    document = policy_document()
    assert isinstance(document["probes"], list), "the JSON document must be serializable"
    document["probes"][0]["parameters"]["room_size"] = 0.99
    assert probe_by_candidate()["A"]["parameters"]["room_size"] == 0.22


def test_parameters_for_is_deterministic_and_rejects_unknown_candidates():
    assert parameters_for("B") == parameters_for("B")
    try:
        parameters_for("D")
    except KeyError:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown candidate must raise")


def test_the_same_source_renders_into_three_measurably_different_fields():
    """The central product claim, checked on one waveform."""
    sr = 48000
    t = np.arange(sr * 3) / sr
    source = np.stack(
        [0.34 * np.sin(2 * np.pi * 220 * t), 0.30 * np.sin(2 * np.pi * 330 * t)], axis=1
    ).astype(np.float32)

    outputs = [render_array(source, sr, field)[0] for field in probe_fields()]
    hashes = {out.tobytes() for out in outputs}
    assert len(hashes) == 3, "the three probes must not produce the same render"

    widths = []
    for out in outputs:
        left = out[:, 0].astype(np.float64)
        right = out[:, 1].astype(np.float64)
        correlation = float(np.corrcoef(left, right)[0, 1])
        widths.append(round(1.0 - abs(correlation), 6))
    assert len(set(widths)) == 3, f"stereo field width must differ per probe: {widths}"
    assert widths[0] > widths[2], "the larger field must decorrelate more"


def test_run_field_search_is_deterministic(source_wav, case_dir):
    from moodify.wavefield.record import inspect

    first = run_field_search(case_dir, source_path=str(source_wav))
    first_hashes = {cid: row["sha256"] for cid, row in first["candidates"].items()}

    second = run_field_search(case_dir, source_path=str(source_wav))
    second_hashes = {cid: row["sha256"] for cid, row in second["candidates"].items()}

    assert first_hashes == second_hashes
    assert inspect(case_dir)["blockers"] == ["NOT_CHOSEN"]


def test_run_field_search_writes_one_candidate_per_probe(source_wav, case_dir):
    state = run_field_search(case_dir, source_path=str(source_wav), hear=False)
    assert set(state["candidates"]) == {"A", "B", "C"}
    for candidate_id, row in state["candidates"].items():
        assert row["exists"], candidate_id
        rendered, _ = sf.read(row["path"], always_2d=False)
        assert np.all(np.isfinite(rendered))
    assert state["session"]["policy_id"] == POLICY_ID
