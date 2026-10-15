"""Wave Field models — Moodify Wave Field Local v0.

This is the *product object* layer of the direction recorded in
``docs/canon/WAVEFIELD_CORE_PRINCIPLE.md``: a waveform is not finished sound,
it is the condition that makes sound happen.  A :class:`FieldSpec` names a
**perceptual virtual acoustic field**; rendering places the waveform in it.

Honest language boundary (canon: *Physical truth boundary*): a single
mono/stereo file supports only a source-field / stereo-field **projection**.
``algorithmic_room_v0`` is a perceptual, algorithmic room field — NOT a
physically exact propagation simulator, NOT real room reconstruction, NOT
ray-traced acoustics.  Nothing in this package may be described as any of
those.

The schema is deliberately small: four parameters in v0, not thirty.  The most
important one is ``room_size`` — the first direct implementation of the product
idea that *the same waveform can be placed in different field sizes*.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Schema identifiers
# ---------------------------------------------------------------------------

WAVEFIELD_SCHEMA = "moodify.wavefield/0.1"
RENDER_SCHEMA = "moodify.wavefield.render/0.1"
HEAR_SCHEMA = "moodify.hear/0.1"
SEARCH_SCHEMA = "moodify.wavefield.search/0.1"
SESSION_SCHEMA = "moodify.wavefield.session/0.1"
DECISION_SCHEMA = "moodify.wavefield.decision/0.1"
EXPORT_SCHEMA = "moodify.wavefield.export/0.1"

# ---------------------------------------------------------------------------
# Fields
# ---------------------------------------------------------------------------

ENGINE_ALGORITHMIC_ROOM_V0 = "algorithmic_room_v0"
SUPPORTED_ENGINES: tuple[str, ...] = (ENGINE_ALGORITHMIC_ROOM_V0,)

#: Field ids are short, stable machine names (``field_A``), never file paths.
FIELD_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")

#: Bounds are inclusive.  ``wet`` is capped well below 1.0 on purpose: this is
#: a field, not a reverb product preset — the dry signal must remain dominant.
PARAMETER_BOUNDS: dict[str, tuple[float, float]] = {
    "room_size": (0.0, 1.0),
    "damping": (0.0, 1.0),
    "wet": (0.0, 0.40),
    "width": (0.0, 1.0),
}

#: Declaration order — it is part of the serialized record, so keep it stable.
REQUIRED_PARAMETERS: tuple[str, ...] = tuple(PARAMETER_BOUNDS)

#: The product surface is ORIGINAL + three probes.  A/B/C are *probes*, not
#: permanent marketing presets, and must never be promoted into another preset
#: product surface.
CANDIDATE_IDS: tuple[str, ...] = ("A", "B", "C")
CHOICES: tuple[str, ...] = ("ORIGINAL", "A", "B", "C")
ROLES: tuple[str, ...] = ("creator", "listener", "pro")


class FieldSpecError(ValueError):
    """A ``FieldSpec`` that cannot be trusted as a reproducible field record."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


# ---------------------------------------------------------------------------
# FieldSpec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldSpec:
    """A versioned, validated, serializable description of one virtual field.

    Validation is strict and total.  A field record that cannot be re-validated
    later cannot be reproduced, and an unreproducible field is not a field.
    """

    field_id: str
    parameters: dict[str, float]
    engine: str = ENGINE_ALGORITHMIC_ROOM_V0
    schema: str = WAVEFIELD_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != WAVEFIELD_SCHEMA:
            raise FieldSpecError(
                "UNSUPPORTED_SCHEMA",
                f"expected {WAVEFIELD_SCHEMA!r}, got {self.schema!r}",
            )
        if not isinstance(self.field_id, str) or not FIELD_ID_PATTERN.match(self.field_id):
            raise FieldSpecError(
                "MALFORMED_FIELD_ID",
                f"{self.field_id!r} must match {FIELD_ID_PATTERN.pattern}",
            )
        if self.engine not in SUPPORTED_ENGINES:
            raise FieldSpecError(
                "UNKNOWN_ENGINE",
                f"{self.engine!r} is not one of {list(SUPPORTED_ENGINES)}",
            )
        if not isinstance(self.parameters, Mapping):
            raise FieldSpecError("MALFORMED_PARAMETERS", "parameters must be a mapping")

        missing = [key for key in REQUIRED_PARAMETERS if key not in self.parameters]
        if missing:
            raise FieldSpecError("MISSING_PARAMETER", f"missing {missing}")
        unknown = [key for key in self.parameters if key not in PARAMETER_BOUNDS]
        if unknown:
            raise FieldSpecError("UNKNOWN_PARAMETER", f"unknown {sorted(unknown)}")

        normalized: dict[str, float] = {}
        for key in REQUIRED_PARAMETERS:
            raw = self.parameters[key]
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise FieldSpecError(
                    "NON_NUMERIC_PARAMETER", f"{key}={raw!r} is not a number"
                )
            value = float(raw)
            if not math.isfinite(value):
                raise FieldSpecError("NON_FINITE_PARAMETER", f"{key}={raw!r}")
            low, high = PARAMETER_BOUNDS[key]
            if value < low or value > high:
                raise FieldSpecError(
                    "PARAMETER_OUT_OF_BOUNDS",
                    f"{key}={value} outside [{low}, {high}]",
                )
            normalized[key] = round(value, 6)
        object.__setattr__(self, "parameters", normalized)

    # -- serialization ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Canonical record.  Key order follows ``REQUIRED_PARAMETERS``."""
        return {
            "schema": self.schema,
            "field_id": self.field_id,
            "engine": self.engine,
            "parameters": {key: self.parameters[key] for key in REQUIRED_PARAMETERS},
        }

    def canonical(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def field_hash(self) -> str:
        import hashlib

        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> FieldSpec:
        if not isinstance(data, Mapping):
            raise FieldSpecError("MALFORMED_FIELD", "field must be a JSON object")
        if "schema" not in data:
            raise FieldSpecError("MISSING_SCHEMA", "field record carries no schema")
        return cls(
            field_id=data.get("field_id"),  # type: ignore[arg-type]
            parameters=data.get("parameters", {}),  # type: ignore[arg-type]
            engine=data.get("engine", ENGINE_ALGORITHMIC_ROOM_V0),
            schema=data["schema"],
        )

    @classmethod
    def from_json(cls, text: str) -> FieldSpec:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise FieldSpecError("MALFORMED_FIELD", str(exc)) from exc
        return cls.from_dict(data)

    # -- evolution ----------------------------------------------------------

    def with_parameters(self, **overrides: float) -> FieldSpec:
        """Return a new spec with the given parameters replaced (still validated)."""
        merged = dict(self.parameters)
        merged.update(overrides)
        return FieldSpec(
            field_id=self.field_id, parameters=merged, engine=self.engine, schema=self.schema
        )


def field_specs_from(probes: Sequence[Mapping[str, Any]]) -> list[FieldSpec]:
    """Build validated specs from a policy probe list (order preserved)."""
    return [
        FieldSpec(
            field_id=str(probe["field_id"]),
            parameters=dict(probe["parameters"]),
            engine=str(probe.get("engine", ENGINE_ALGORITHMIC_ROOM_V0)),
        )
        for probe in probes
    ]
