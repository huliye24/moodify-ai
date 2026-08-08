"""Moodify Capability Registry — knows what the environment can do.

Registry discovers, registers and lists production capabilities and their
providers. It records constraints, licenses, versions, health and known
failure modes (negative knowledge). It never executes processing; adapters
(018) will translate contracts into provider calls.
"""

from moodify.capability_registry.model import (
    CapabilityContract,
    CapabilityRegistry,
    ProviderRecord,
    RegistryState,
)

__all__ = [
    "CapabilityContract",
    "CapabilityRegistry",
    "ProviderRecord",
    "RegistryState",
]
