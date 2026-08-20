"""MAMSE-012 — graph signal processing & auditory topology (experimental).

Explicit topology over auditory objects: band path graph, temporal event
graph, positive-correlation graph; Laplacian spectrum, GFT, Dirichlet
energy, local variation, graph filters. Graph frequency is topology
frequency, not acoustic Hz; edges express chosen relations, not causality.
"""

from .builders import (
    build_band_adjacency_graph,
    build_positive_correlation_graph,
    build_temporal_event_graph,
)
from .contracts import (
    ALGORITHM_VERSION,
    EPS,
    SCHEMA_VERSION,
    AuditoryGraph,
    GraphContractError,
    GraphEdge,
    GraphNode,
    canonical_graph,
)
from .evidence import MANIFEST_SCHEMA_VERSION, graph_evidence, save_graph_evidence
from .gsp import (
    dirichlet_energy,
    graph_fourier_transform,
    graph_spectral_energy,
    heat_kernel_filter,
    inverse_graph_fourier,
    local_variation,
    polynomial_graph_filter,
    spectral_decomposition,
)

__all__ = [
    "SCHEMA_VERSION",
    "ALGORITHM_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "EPS",
    "GraphNode",
    "GraphEdge",
    "AuditoryGraph",
    "GraphContractError",
    "canonical_graph",
    "build_band_adjacency_graph",
    "build_temporal_event_graph",
    "build_positive_correlation_graph",
    "spectral_decomposition",
    "graph_fourier_transform",
    "inverse_graph_fourier",
    "dirichlet_energy",
    "local_variation",
    "graph_spectral_energy",
    "heat_kernel_filter",
    "polynomial_graph_filter",
    "graph_evidence",
    "save_graph_evidence",
]
