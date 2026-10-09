"""Runtime capability probe records (``moodify.runtime_probe/0.1``).

These models describe **what this machine can run right now** — the third
question, distinct from the two layers that already exist:

    DECLARATION  what the project says a provider requires   (capabilities.models)
    ROUTING      which declared provider is eligible          (capabilities.router)
    PROBING      whether the provider can actually run here   (this package)

A probe result is a *record of something that happened* — a measurement taken
at a moment — so it carries a timezone-aware ``checked_at``. It inherits the
canonical conventions (frozen, ``extra="forbid"``, enum-typed vocabularies,
JSON-safe values) without pretending to be a canonical v1 contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from moodify.compat import StrEnum

from ..capabilities.policy import ProviderPolicy
from ..contracts.base import ensure_json_safe, freeze_json_value

#: Schema identifier for a probe report. Distinct from the canonical contract
#: ``schema_version`` ("1.0") — they version different things.
RUNTIME_PROBE_SCHEMA = "moodify.runtime_probe/0.1"


class ProbeStatus(StrEnum):
    """What the probe can honestly say about one provider on this machine.

    ``AVAILABLE`` is never produced by a check that only confirmed a file
    exists: every requirement must have been *verified* (an interpreter ran,
    a module imported, a binary executed). ``UNKNOWN`` is a legitimate,
    expected answer — it names a question this probe refused to guess at.
    """

    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class RequirementStatus(StrEnum):
    """The outcome of verifying one declared requirement."""

    SATISFIED = "SATISFIED"
    """Verified present and usable (imported, executed, version checked)."""

    MISSING = "MISSING"
    """Verified absent or broken — a definitive negative."""

    MISMATCH = "MISMATCH"
    """Present, but not the version the declaration pins."""

    UNKNOWN = "UNKNOWN"
    """Could not be verified — no adapter, refused probe, or a timeout.

    Never folded into SATISFIED: an unverified requirement is not a met one.
    """


class RequirementCheck(BaseModel):
    """One declared requirement and what the probe learned about it.

    ``requirement`` is the declaration's own string, verbatim, so the report
    can always be traced back to the claim it verifies.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    requirement: str
    kind: str
    """Which probe adapter produced this check (``python_version``,
    ``python_import``, ``executable``, ``external_venv``, ``unsupported``)."""

    status: RequirementStatus
    detail: str
    remedy: str | None = None
    """What would make this requirement met, when one is known."""


class ProviderProbe(BaseModel):
    """The runtime truth about one provider on this machine, right now."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str
    capability_ids: tuple[str, ...]
    probe_status: ProbeStatus
    checked_at: datetime
    runtime_kind: str
    """How the provider runs here: ``python_in_process`` (the interpreter
    running the probe), ``external_venv``, ``system_binary``, or
    ``remote_service`` (deliberately not probed)."""

    executable_or_environment: str | None = None
    version: str | None = None
    requirements_checked: tuple[RequirementCheck, ...]
    missing_requirements: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    evidence: dict[str, Any] = {}

    @field_validator("checked_at")
    @classmethod
    def require_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("checked_at must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("evidence")
    @classmethod
    def require_json_safe_evidence(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value) if value else value


def probe_status_for(checks: tuple[RequirementCheck, ...]) -> ProbeStatus:
    """Derive the provider status from its requirement checks.

    The rules, in order (the loudest fact wins):

    * any ``MISSING``            → ``UNAVAILABLE`` (a definitive negative)
    * every check ``UNKNOWN``    → ``UNKNOWN`` (nothing was verified)
    * any ``UNKNOWN``/``MISMATCH`` → ``DEGRADED`` (partly verified only)
    * otherwise                  → ``AVAILABLE`` (every requirement verified)

    No checks at all is ``UNKNOWN``: nothing was verified, so nothing may be
    claimed.
    """
    if not checks:
        return ProbeStatus.UNKNOWN
    if any(check.status is RequirementStatus.MISSING for check in checks):
        return ProbeStatus.UNAVAILABLE
    if any(check.status is RequirementStatus.UNKNOWN for check in checks):
        if all(check.status is RequirementStatus.UNKNOWN for check in checks):
            return ProbeStatus.UNKNOWN
        return ProbeStatus.DEGRADED
    if any(check.status is RequirementStatus.MISMATCH for check in checks):
        return ProbeStatus.DEGRADED
    return ProbeStatus.AVAILABLE


class ProviderRuntimeReport(BaseModel):
    """The join of two independent layers for one provider.

    ``probe`` is runtime truth (policy-free); ``eligible_capabilities`` comes
    from the pure router under the report's policy. Keeping them as separate
    fields is the point: "eligible but unavailable" and "ineligible but
    installed" are both readable from this record without collapsing the
    layers that produced them.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    probe: ProviderProbe
    eligible_capabilities: tuple[str, ...] = ()


class RuntimeReport(BaseModel):
    """A whole-machine runtime answer: every provider, probed and joined."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    protocol: str = RUNTIME_PROBE_SCHEMA
    generated_at: datetime
    duration_s: float
    policy: ProviderPolicy
    """The policy eligibility was decided under. Carried in the report so a
    reader can always tell *under which rules* a provider counted as
    eligible."""

    providers: tuple[ProviderRuntimeReport, ...]
    summary: dict[str, Any] = {}

    @field_validator("generated_at")
    @classmethod
    def require_aware_generated_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("summary")
    @classmethod
    def require_json_safe_summary(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value) if value else value
