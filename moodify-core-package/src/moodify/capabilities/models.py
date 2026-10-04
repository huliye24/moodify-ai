"""Canonical capability and provider declarations (``moodify.capabilities/0.1``).

These models describe **what Moodify can do** and **who can do it**. They
describe nothing about how anything runs: there is no execute method, no
registry of callables, no import of an engine.

On the base class
-----------------
These declarations deliberately do *not* inherit
:class:`moodify.contracts.base.CanonicalModel`. That base models **records of
things that happened** — it requires a timezone-aware ``created_at`` because a
measurement, an artifact or a case is an event. A capability declaration is not
an event: it is a static catalog entry that describes no moment in time.
Stamping every declaration with an import timestamp would be a fabricated fact
in a system whose whole point is not fabricating facts.

The conventions that *do* apply are inherited in full: frozen instances,
``extra="forbid"``, enum-typed vocabularies, and canonical JSON via
``moodify.contracts.serialization``.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from moodify.compat import StrEnum

from .failures import FailureCode

#: Schema identifier for the registry snapshot. Distinct from the canonical
#: contract ``schema_version`` ("1.0") — they version different things.
CAPABILITY_SCHEMA = "moodify.capabilities/0.1"

#: One ID segment: lowercase ASCII, no leading digit or underscore.
_SEGMENT = re.compile(r"^[a-z][a-z0-9_]*$")

#: Rejects version-like segments (``v1``, ``2``) so that versions never leak
#: into a capability ID. ``stem.separate.v1`` is a contract revision, not a
#: new capability; it belongs in the contract, not the name.
_VERSION_LIKE = re.compile(r"^v?\d+$")


def _validate_segments(value: str, *, kind: str, exact_parts: int | None) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{kind} must be a non-empty string")
    if value != value.strip() or not value.isascii():
        raise ValueError(f"{kind} must be trimmed ASCII")
    parts = value.split(".")
    if exact_parts is not None and len(parts) != exact_parts:
        raise ValueError(f"{kind} must be '<domain>.<operation>' ({exact_parts} dot-separated segments)")
    if len(parts) < 2:
        raise ValueError(f"{kind} must have at least two dot-separated segments")
    for part in parts:
        if not _SEGMENT.match(part):
            raise ValueError(f"{kind} segment {part!r} must match [a-z][a-z0-9_]*")
        if _VERSION_LIKE.match(part):
            raise ValueError(f"{kind} must not encode a version: {part!r}")
    return value


def validate_capability_id(value: str) -> str:
    """Validate a ``domain.operation`` capability ID.

    Capability IDs are provider-independent and stable: ``stem.separate``
    survives Demucs being replaced. ``demucs.separate`` does not.
    """
    return _validate_segments(value, kind="capability_id", exact_parts=2)


def validate_provider_id(value: str) -> str:
    """Validate a provider ID (``moodify.auditory``, ``lalal.cloud``)."""
    return _validate_segments(value, kind="provider_id", exact_parts=None)


class CapabilityStatus(StrEnum):
    """How real a capability is in *this* branch, from repository evidence."""

    CANONICAL = "CANONICAL"
    IMPLEMENTED_NOT_CANONICAL = "IMPLEMENTED_NOT_CANONICAL"
    PARTIAL = "PARTIAL"
    EXPERIMENTAL = "EXPERIMENTAL"
    ABSENT = "ABSENT"
    LEGACY = "LEGACY"
    DEFERRED = "DEFERRED"


class StrategicPosture(StrEnum):
    """What Moodify intends to do about the capability. Architecture
    metadata, **not** runtime availability — an ``ABSENT`` capability may
    legitimately be ``INTEGRATE``."""

    BUILD = "BUILD"
    INTEGRATE = "INTEGRATE"
    DELEGATE = "DELEGATE"
    DEFER = "DEFER"


class IOType(StrEnum):
    """A small controlled vocabulary for discovery. Not a wire schema —
    Sound Protocol owns that."""

    AUDIO = "audio"
    PROJECT = "project"
    STEM = "stem"
    MIDI = "midi"
    MUSICXML = "musicxml"
    SCORE = "score"
    LYRICS = "lyrics"
    MIX_SESSION = "mix_session"
    MASTER = "master"
    REPORT = "report"
    EVIDENCE = "evidence"
    METADATA = "metadata"


class Locality(StrEnum):
    """Where a capability naturally runs. Not provider availability."""

    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    HYBRID = "HYBRID"
    EXTERNAL_APP = "EXTERNAL_APP"
    ABSTRACT = "ABSTRACT"


class Determinism(StrEnum):
    DETERMINISTIC = "DETERMINISTIC"
    CONDITIONALLY_DETERMINISTIC = "CONDITIONALLY_DETERMINISTIC"
    NONDETERMINISTIC = "NONDETERMINISTIC"
    UNKNOWN = "UNKNOWN"


class ProviderType(StrEnum):
    LIBRARY = "library"
    CLI = "cli"
    MODEL = "model"
    API = "api"
    BINARY = "binary"
    STANDARD = "standard"


class ExecutionMode(StrEnum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    EXTERNAL_APP = "EXTERNAL_APP"


class ProviderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CONNECTED_UNTESTED = "CONNECTED_UNTESTED"
    EXPERIMENTAL = "EXPERIMENTAL"
    DECLARED_ONLY = "DECLARED_ONLY"
    UNAVAILABLE = "UNAVAILABLE"
    DEPRECATED = "DEPRECATED"


class CommercialUse(StrEnum):
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class Redistribution(StrEnum):
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


def _require_unique(values: tuple, field: str) -> tuple:
    """Reject duplicates rather than de-duplicating them.

    Silently collapsing a repeated entry is a repair, and a repaired
    declaration is one nobody can audit: the author's intent is lost and the
    omission is invisible downstream.
    """
    if len(set(values)) != len(values):
        raise ValueError(f"{field} contains duplicates")
    return values


class Capability(BaseModel):
    """A declared capability: what Moodify can conceptually do."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    capability_id: str
    title: str
    description: str
    domain: str
    status: CapabilityStatus
    strategic_posture: StrategicPosture
    input_types: tuple[IOType, ...]
    output_types: tuple[IOType, ...]
    failure_codes: tuple[FailureCode, ...]
    provider_ids: tuple[str, ...] = ()
    locality: Locality
    determinism: Determinism
    requires_human_review: bool = False
    notes: str | None = None

    @field_validator("capability_id")
    @classmethod
    def require_capability_id(cls, value: str) -> str:
        return validate_capability_id(value)

    @field_validator("title", "description")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("input_types", "output_types")
    @classmethod
    def require_io_types(cls, value: tuple[IOType, ...]) -> tuple[IOType, ...]:
        if not value:
            raise ValueError("capability must declare at least one input/output type")
        return _require_unique(value, "input_types/output_types")

    @field_validator("failure_codes")
    @classmethod
    def require_failure_codes(cls, value: tuple[FailureCode, ...]) -> tuple[FailureCode, ...]:
        if not value:
            raise ValueError("capability must declare at least one failure code")
        return _require_unique(value, "failure_codes")

    @field_validator("provider_ids")
    @classmethod
    def require_provider_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        checked = tuple(validate_provider_id(item) for item in value)
        return _require_unique(checked, "provider_ids")

    @model_validator(mode="after")
    def require_domain_matches_id(self) -> "Capability":
        if self.domain != self.capability_id.split(".", 1)[0]:
            raise ValueError(
                f"domain {self.domain!r} must equal the capability_id prefix "
                f"{self.capability_id.split('.', 1)[0]!r}"
            )
        return self


class Provider(BaseModel):
    """A declared provider: an implementation that can satisfy capabilities.

    Identity is deliberately separate from capability identity. A provider may
    implement several capabilities; a capability may have several providers.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str
    name: str
    provider_type: ProviderType
    capability_ids: tuple[str, ...]
    execution_mode: ExecutionMode
    status: ProviderStatus
    code_license: str
    weights_license: str | None = None
    """``None`` means the provider involves no model weights at all (a system
    binary, a cloud API, a pure algorithm). It is **not** the same as
    ``"UNKNOWN"``: unknown means weights exist and their terms are unverified,
    which is the domain's most common licensing trap."""

    commercial_use: CommercialUse = CommercialUse.UNKNOWN
    redistribution: Redistribution = Redistribution.UNKNOWN
    runtime_requirements: tuple[str, ...] = ()
    notes: str | None = None

    @field_validator("provider_id")
    @classmethod
    def require_provider_id(cls, value: str) -> str:
        return validate_provider_id(value)

    @field_validator("name", "code_license")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("weights_license")
    @classmethod
    def normalize_weights_license(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("capability_ids")
    @classmethod
    def require_capability_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("provider must declare at least one capability")
        checked = tuple(validate_capability_id(item) for item in value)
        return _require_unique(checked, "capability_ids")

    @field_validator("runtime_requirements")
    @classmethod
    def require_unique_requirements(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_unique(value, "runtime_requirements")
