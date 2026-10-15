"""FieldSpec v0 — versioning, bounds and serialization round-trip."""

from __future__ import annotations

import json
import math

import pytest

from moodify.wavefield.models import (
    CANDIDATE_IDS,
    CHOICES,
    ENGINE_ALGORITHMIC_ROOM_V0,
    REQUIRED_PARAMETERS,
    WAVEFIELD_SCHEMA,
    FieldSpec,
    FieldSpecError,
)


def spec(**overrides) -> FieldSpec:
    params = {"room_size": 0.5, "damping": 0.5, "wet": 0.16, "width": 0.86}
    params.update(overrides)
    return FieldSpec(field_id="field_A", parameters=params)


def test_round_trip_through_dict_and_json():
    original = spec()
    assert FieldSpec.from_dict(original.to_dict()) == original
    assert FieldSpec.from_json(original.to_json()) == original
    assert json.loads(original.to_json()) == original.to_dict()
    assert original.canonical() == json.dumps(
        original.to_dict(), sort_keys=True, separators=(",", ":")
    )


def test_schema_and_engine_are_recorded():
    document = spec().to_dict()
    assert document["schema"] == WAVEFIELD_SCHEMA
    assert document["engine"] == ENGINE_ALGORITHMIC_ROOM_V0
    assert set(document["parameters"]) == set(REQUIRED_PARAMETERS)


def test_room_size_is_the_declared_axis_and_is_bounded():
    for value in (0.0, 0.22, 0.5, 0.8, 1.0):
        assert spec(room_size=value).parameters["room_size"] == value
    with pytest.raises(FieldSpecError) as excinfo:
        spec(room_size=1.0001)
    assert excinfo.value.code == "PARAMETER_OUT_OF_BOUNDS"


@pytest.mark.parametrize(
    ("key", "bad"),
    [
        ("room_size", -0.01),
        ("room_size", 1.01),
        ("damping", -1.0),
        ("damping", 2.0),
        ("wet", -0.001),
        ("wet", 0.41),
        ("width", -0.5),
        ("width", 1.5),
    ],
)
def test_out_of_bounds_parameters_are_rejected(key, bad):
    with pytest.raises(FieldSpecError) as excinfo:
        spec(**{key: bad})
    assert excinfo.value.code == "PARAMETER_OUT_OF_BOUNDS"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_parameters_are_rejected(bad):
    with pytest.raises(FieldSpecError) as excinfo:
        spec(wet=bad)
    assert excinfo.value.code == "NON_FINITE_PARAMETER"


def test_missing_schema_is_rejected_on_read():
    document = spec().to_dict()
    del document["schema"]
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec.from_dict(document)
    assert excinfo.value.code == "MISSING_SCHEMA"


def test_unsupported_schema_is_rejected():
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec.from_dict({"schema": "moodify.wavefield/9.9", "field_id": "field_A",
                             "parameters": {"room_size": 0.5, "damping": 0.5,
                                            "wet": 0.1, "width": 0.8}})
    assert excinfo.value.code == "UNSUPPORTED_SCHEMA"


def test_unknown_engine_is_rejected():
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec(field_id="field_A", parameters={"room_size": 0.5, "damping": 0.5,
                                                  "wet": 0.1, "width": 0.8},
                  engine="ray_traced_room_v9")
    assert excinfo.value.code == "UNKNOWN_ENGINE"


@pytest.mark.parametrize("bad_id", ["", "1A", "field A", "field-A", "../escape", "a" * 40, None, 7])
def test_malformed_field_ids_are_rejected(bad_id):
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec(field_id=bad_id, parameters={"room_size": 0.5, "damping": 0.5,
                                               "wet": 0.1, "width": 0.8})
    assert excinfo.value.code == "MALFORMED_FIELD_ID"


def test_missing_and_unknown_parameters_are_rejected():
    with pytest.raises(FieldSpecError) as missing:
        FieldSpec(field_id="field_A", parameters={"room_size": 0.5})
    assert missing.value.code == "MISSING_PARAMETER"

    with pytest.raises(FieldSpecError) as unknown:
        FieldSpec(field_id="field_A", parameters={"room_size": 0.5, "damping": 0.5,
                                                  "wet": 0.1, "width": 0.8,
                                                  "early_reflections": 0.3})
    assert unknown.value.code == "UNKNOWN_PARAMETER"


def test_non_numeric_parameters_are_rejected():
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec(field_id="field_A", parameters={"room_size": "0.5", "damping": 0.5,
                                                  "wet": 0.1, "width": 0.8})
    assert excinfo.value.code == "NON_NUMERIC_PARAMETER"


def test_bool_is_not_accepted_as_a_parameter_value():
    """``True == 1`` in Python; a boolean is a data-entry error, not a parameter."""
    with pytest.raises(FieldSpecError) as excinfo:
        FieldSpec(field_id="field_A", parameters={"room_size": True, "damping": 0.5,
                                                  "wet": 0.1, "width": 0.8})
    assert excinfo.value.code == "NON_NUMERIC_PARAMETER"


def test_field_hash_is_stable_and_parameter_sensitive():
    a = spec(room_size=0.22)
    b = spec(room_size=0.80)
    assert a.field_hash() == spec(room_size=0.22).field_hash()
    assert a.field_hash() != b.field_hash()
    assert len(a.field_hash()) == 64


def test_with_parameters_returns_a_new_validated_spec():
    original = spec()
    changed = original.with_parameters(room_size=0.9)
    assert changed.parameters["room_size"] == 0.9
    assert original.parameters["room_size"] == 0.5, "the original must be untouched"
    assert changed is not original
    with pytest.raises(FieldSpecError):
        original.with_parameters(room_size=2.0)


def test_parameters_are_stored_in_declaration_order_for_a_stable_record():
    document = spec().to_dict()
    assert tuple(document["parameters"]) == REQUIRED_PARAMETERS


def test_values_are_finite_floats_after_construction():
    built = spec(room_size=0)
    assert isinstance(built.parameters["room_size"], float)
    assert math.isfinite(built.parameters["room_size"])


def test_the_product_surface_is_original_plus_three_probes():
    assert CHOICES == ("ORIGINAL", "A", "B", "C")
    assert CANDIDATE_IDS == ("A", "B", "C")
