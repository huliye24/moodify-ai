"""base.py — Provider interface for mix_graph nodes.

Every node type in a mix graph is rendered by exactly one provider.
Providers are pure functions of (audio, sr, parameters) -> audio and must be
deterministic: same version + same input + same parameters -> same output.
"""

from __future__ import annotations

import numpy as np


class ProviderError(ValueError):
    """Raised when node parameters are invalid for a provider."""


class NodeProvider:
    """Base class for mix_graph node providers."""

    node_type: str = ""
    summary: str = ""

    def validate_parameters(self, parameters: dict) -> dict:
        """Validate and canonicalize parameters; raise ProviderError on any violation."""
        raise NotImplementedError

    def render(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        """Apply the node to audio (shape (n,) or (n, ch), float32) and return processed audio."""
        raise NotImplementedError

    def describe(self, parameters: dict) -> dict:
        """Deterministic provenance description of what will be applied."""
        return {"node_type": self.node_type, "parameters": dict(parameters)}
