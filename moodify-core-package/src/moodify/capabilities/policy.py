"""Provider selection policy.

A policy expresses **what the caller will accept**, not what it wants most.
That distinction is the whole design:

* **hard constraints** eliminate providers — they can never be outvoted;
* **soft preferences** only order whatever survives.

The default policy is deliberately conservative: it accepts only providers
declared ``ACTIVE``, and every relaxation must be asked for by name. A default
that silently accepts unverified connectivity turns "we have never run this"
into "available", which is the failure mode this layer exists to prevent.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from moodify.compat import StrEnum

from .models import validate_provider_id


class PrivacyPolicy(StrEnum):
    """Hard constraint on where work may run."""

    ANY = "ANY"
    """No constraint."""

    NO_CLOUD = "NO_CLOUD"
    """Work must not be sent to a remote service. Local applications are fine —
    a DAW on this machine is not "the cloud"."""

    LOCAL_ONLY = "LOCAL_ONLY"
    """Work must run on this machine. Rejects both cloud services and external
    applications. The strongest data-locality constraint."""


class LocalityPreference(StrEnum):
    """Soft preference over where work runs. Never eliminates a provider."""

    ANY = "ANY"
    PREFER_LOCAL = "PREFER_LOCAL"
    PREFER_CLOUD = "PREFER_CLOUD"


class DeterminismPolicy(StrEnum):
    ANY = "ANY"

    PREFER_DETERMINISTIC = "PREFER_DETERMINISTIC"
    """Rank deterministic providers first among the eligible."""

    REQUIRE_DETERMINISTIC = "REQUIRE_DETERMINISTIC"
    """Eliminate any provider not declared ``DETERMINISTIC``.

    ``UNKNOWN`` does not satisfy this. An unestablished claim is not a claim,
    and treating unknown as deterministic is exactly the false confidence this
    layer exists to prevent.
    """


class ProviderPolicy(BaseModel):
    """Selection policy. Immutable; ``extra="forbid"``.

    Constructing the default (``ProviderPolicy()``) is the conservative
    choice: ``ACTIVE`` providers only, no locality constraint, no licence
    requirement, no preferences.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # ── hard constraints ──────────────────────────────────────────────────
    privacy: PrivacyPolicy = PrivacyPolicy.ANY
    determinism: DeterminismPolicy = DeterminismPolicy.ANY
    commercial_use_required: bool = False
    redistribution_required: bool = False

    # ── explicit opt-ins for non-default provider statuses ────────────────
    allow_experimental: bool = False
    allow_connected_untested: bool = False
    allow_declared_only: bool = False

    # ── soft preferences ──────────────────────────────────────────────────
    locality_preference: LocalityPreference = LocalityPreference.ANY
    preferred_provider_ids: tuple[str, ...] = ()

    # ── exclusion (outranks every preference) ─────────────────────────────
    excluded_provider_ids: tuple[str, ...] = ()

    @field_validator("preferred_provider_ids", "excluded_provider_ids")
    @classmethod
    def require_provider_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        checked = tuple(validate_provider_id(item) for item in value)
        if len(set(checked)) != len(checked):
            raise ValueError("provider ID list contains duplicates")
        return checked
