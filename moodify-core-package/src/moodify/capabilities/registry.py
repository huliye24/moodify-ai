"""Read-only capability registry: validation, queries, deterministic snapshot.

The registry answers *what Moodify can do* and *who can do it*. It executes
nothing, imports no engine, and reaches no network.

Layer boundary (see also ``docs/ecosystem/MOODIFY_CAPABILITY_REGISTRY_0_1.md``)::

    Capability Registry = what Moodify can conceptually do
    Sound Protocol      = how a capability request is expressed
    Provider Router     = which implementation performs it  (not implemented)
    Production Graph    = how capabilities are composed     (not implemented)
    Project Model       = persistent production state       (not merged)
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

from ..contracts.serialization import to_canonical_dict
from .models import (
    CAPABILITY_SCHEMA,
    Capability,
    CapabilityStatus,
    Provider,
    ProviderStatus,
)


class RegistryError(Exception):
    """Base class for registry failures."""


class RegistryValidationError(RegistryError):
    """A set of declarations is internally inconsistent.

    Raised at construction. Declarations are never silently repaired: a
    registry that quietly drops a bad entry is worse than one that refuses to
    build, because the omission is invisible to every downstream consumer.
    """


class CapabilityNotFound(RegistryError, KeyError):
    """No capability with that ID is declared."""


class ProviderNotFound(RegistryError, KeyError):
    """No provider with that ID is declared."""


def _index_capabilities(items: Iterable[Capability]) -> dict[str, Capability]:
    index: dict[str, Capability] = {}
    for item in items:
        if item.capability_id in index:
            raise RegistryValidationError(f"duplicate capability ID: {item.capability_id}")
        index[item.capability_id] = item
    return index


def _index_providers(items: Iterable[Provider]) -> dict[str, Provider]:
    index: dict[str, Provider] = {}
    for item in items:
        if item.provider_id in index:
            raise RegistryValidationError(f"duplicate provider ID: {item.provider_id}")
        index[item.provider_id] = item
    return index


class CapabilityRegistry:
    """An immutable, validated set of capability and provider declarations."""

    def __init__(
        self,
        capabilities: Sequence[Capability],
        providers: Sequence[Provider],
    ) -> None:
        self._capabilities = _index_capabilities(capabilities)
        self._providers = _index_providers(providers)
        self._validate_references()

    # ── validation ────────────────────────────────────────────────────────

    def _validate_references(self) -> None:
        """Reject dangling and asymmetric references in both directions."""
        for capability in self._capabilities.values():
            for provider_id in capability.provider_ids:
                if provider_id not in self._providers:
                    raise RegistryValidationError(
                        f"capability {capability.capability_id} references unknown provider "
                        f"{provider_id}"
                    )
                if capability.capability_id not in self._providers[provider_id].capability_ids:
                    raise RegistryValidationError(
                        f"{provider_id} does not declare {capability.capability_id}; "
                        "capability/provider references must agree in both directions"
                    )
        for provider in self._providers.values():
            for capability_id in provider.capability_ids:
                if capability_id not in self._capabilities:
                    raise RegistryValidationError(
                        f"provider {provider.provider_id} references unknown capability "
                        f"{capability_id}"
                    )
                if provider.provider_id not in self._capabilities[capability_id].provider_ids:
                    raise RegistryValidationError(
                        f"{capability_id} does not declare {provider.provider_id}; "
                        "capability/provider references must agree in both directions"
                    )

    # ── capability queries ────────────────────────────────────────────────

    def list_capabilities(
        self,
        *,
        status: CapabilityStatus | None = None,
        domain: str | None = None,
    ) -> tuple[Capability, ...]:
        """All capabilities, sorted by ID, optionally filtered."""
        items = sorted(self._capabilities.values(), key=lambda c: c.capability_id)
        if status is not None:
            items = [c for c in items if c.status is status]
        if domain is not None:
            items = [c for c in items if c.domain == domain]
        return tuple(items)

    def get_capability(self, capability_id: str) -> Capability:
        try:
            return self._capabilities[capability_id]
        except KeyError:
            raise CapabilityNotFound(capability_id) from None

    def has_capability(self, capability_id: object) -> bool:
        """Membership test.

        A malformed or non-string ID is simply not a member and returns
        ``False`` rather than raising — this is a discovery predicate, and a
        typo should read as "not available", not as a crash.
        """
        return isinstance(capability_id, str) and capability_id in self._capabilities

    # ── provider queries ──────────────────────────────────────────────────

    def list_providers(self, *, status: ProviderStatus | None = None) -> tuple[Provider, ...]:
        items = sorted(self._providers.values(), key=lambda p: p.provider_id)
        if status is not None:
            items = [p for p in items if p.status is status]
        return tuple(items)

    def get_provider(self, provider_id: str) -> Provider:
        try:
            return self._providers[provider_id]
        except KeyError:
            raise ProviderNotFound(provider_id) from None

    def providers_for(self, capability_id: str) -> tuple[Provider, ...]:
        """Providers declaring *capability_id*.

        Raises :class:`CapabilityNotFound` if no such capability is declared —
        "not a capability" is a different answer from "a capability with no
        provider yet", and conflating them would hide real gaps.
        """
        capability = self.get_capability(capability_id)
        return tuple(self._providers[pid] for pid in sorted(capability.provider_ids))

    # ── export ────────────────────────────────────────────────────────────

    @property
    def schema(self) -> str:
        return CAPABILITY_SCHEMA

    def snapshot(self) -> dict[str, Any]:
        """A deterministic, JSON-serializable view of the whole registry.

        Deterministic in the strong sense: the same declarations always produce
        the same bytes, so the snapshot can be hashed and compared across
        builds. This is what Agent and CLI discovery will read.
        """
        return {
            "schema": CAPABILITY_SCHEMA,
            "capabilities": [to_canonical_dict(c) for c in self.list_capabilities()],
            "providers": [to_canonical_dict(p) for p in self.list_providers()],
        }

    def snapshot_json(self) -> str:
        """Canonical JSON form of :meth:`snapshot` (sorted keys, no NaN)."""
        return json.dumps(
            self.snapshot(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
