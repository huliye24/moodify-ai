"""Capability Registry — the canonical answer to "what can Moodify do?"

Registry 0.1 establishes stable, provider-independent capability IDs and the
provider declarations behind them::

    moodify.capabilities/0.1

The rule it exists to enforce::

    Models change. Capabilities persist.

``stem.separate`` survives Demucs being replaced. ``demucs.separate`` does not.

This package is metadata and discovery only. It executes nothing, imports no
engine, and reaches no network. Declarations are static and explicit — nothing
is discovered by scanning the filesystem, because a module with a promising
name is not a capability.
"""

from .builtin import builtin_registry
from .failures import (
    RETRYABLE_FAILURE_CODES,
    Failure,
    FailureCode,
    is_retryable,
)
from .models import (
    CAPABILITY_SCHEMA,
    Capability,
    CapabilityStatus,
    CommercialUse,
    Determinism,
    ExecutionMode,
    IOType,
    Locality,
    Provider,
    ProviderStatus,
    ProviderType,
    Redistribution,
    StrategicPosture,
    validate_capability_id,
    validate_provider_id,
)
from .registry import (
    CapabilityNotFound,
    CapabilityRegistry,
    ProviderNotFound,
    RegistryError,
    RegistryValidationError,
)

__all__ = [
    "CAPABILITY_SCHEMA",
    "RETRYABLE_FAILURE_CODES",
    "Capability",
    "CapabilityNotFound",
    "CapabilityRegistry",
    "CapabilityStatus",
    "CommercialUse",
    "Determinism",
    "ExecutionMode",
    "Failure",
    "FailureCode",
    "IOType",
    "Locality",
    "Provider",
    "ProviderNotFound",
    "ProviderStatus",
    "ProviderType",
    "Redistribution",
    "RegistryError",
    "RegistryValidationError",
    "StrategicPosture",
    "builtin_registry",
    "get_capability",
    "get_provider",
    "has_capability",
    "is_retryable",
    "list_capabilities",
    "list_providers",
    "providers_for",
    "registry_snapshot",
    "registry_snapshot_json",
    "validate_capability_id",
    "validate_provider_id",
]


# ── module-level queries against the canonical built-in registry ──────────


def list_capabilities(*, status=None, domain=None):
    """Declared capabilities, sorted by ID, optionally filtered."""
    return builtin_registry().list_capabilities(status=status, domain=domain)


def get_capability(capability_id: str) -> Capability:
    """One capability by ID. Raises :class:`CapabilityNotFound`."""
    return builtin_registry().get_capability(capability_id)


def has_capability(capability_id: object) -> bool:
    """Whether *capability_id* is declared. Never raises."""
    return builtin_registry().has_capability(capability_id)


def list_providers(*, status=None):
    """Declared providers, sorted by ID, optionally filtered."""
    return builtin_registry().list_providers(status=status)


def get_provider(provider_id: str) -> Provider:
    """One provider by ID. Raises :class:`ProviderNotFound`."""
    return builtin_registry().get_provider(provider_id)


def providers_for(capability_id: str) -> tuple[Provider, ...]:
    """Providers declaring *capability_id*.

    Raises :class:`CapabilityNotFound` if the capability itself is undeclared,
    which is a different answer from a declared capability with no provider.
    """
    return builtin_registry().providers_for(capability_id)


def registry_snapshot() -> dict:
    """Deterministic, JSON-serializable view of the whole registry."""
    return builtin_registry().snapshot()


def registry_snapshot_json() -> str:
    """Canonical JSON form of :func:`registry_snapshot`."""
    return builtin_registry().snapshot_json()
