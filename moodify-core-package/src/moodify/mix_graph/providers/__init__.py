"""providers — registry of mix_graph node providers (one provider per node type)."""

from __future__ import annotations

from moodify.mix_graph.providers.base import NodeProvider, ProviderError
from moodify.mix_graph.providers.pedalboard_providers import (
    CompressorProvider,
    EQProvider,
    LimiterProvider,
    StereoProvider,
)

_PROVIDERS: dict[str, NodeProvider] = {
    provider.node_type: provider
    for provider in (EQProvider(), CompressorProvider(), StereoProvider(), LimiterProvider())
}


def get_provider(node_type: str) -> NodeProvider:
    """Return the provider for a node type; raise ProviderError if unknown."""
    provider = _PROVIDERS.get(node_type)
    if provider is None:
        raise ProviderError(
            f"unknown node type '{node_type}'; known types: {', '.join(sorted(_PROVIDERS))}"
        )
    return provider


__all__ = ["NodeProvider", "ProviderError", "get_provider"]
