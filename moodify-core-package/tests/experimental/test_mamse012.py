"""MAMSE-012 synthetic gates (23 prototype + repo-specific extras).

Band path graph, canonical order, graph_id order-independence, contract
rejections (self-loop/negative/heterogeneous), Laplacian PSD, components,
GFT round-trip, Dirichlet energy, graph spectral energy, heat/polynomial
filters, local variation localization, event graph semantics, positive
correlation graph (no abs), dense guard, evidence boundaries, save/reopen;
plus: manifest roundtrip, blocked-feature policy (negative correlation
never abs'd), sparse path guard.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from moodify_experimental.mamse012 import (
    GraphContractError,
    GraphEdge,
    GraphNode,
    build_band_adjacency_graph,
    build_positive_correlation_graph,
    build_temporal_event_graph,
    canonical_graph,
    dirichlet_energy,
    graph_evidence,
    graph_fourier_transform,
    graph_spectral_energy,
    heat_kernel_filter,
    inverse_graph_fourier,
    local_variation,
    polynomial_graph_filter,
    save_graph_evidence,
    spectral_decomposition,
)

BANDS = [
    ("sub", 20, 60), ("bass", 60, 120), ("low_mid", 120, 250), ("mid", 250, 500),
    ("core_mid", 500, 2000), ("presence", 2000, 5000), ("brilliance", 5000, 10000),
    ("air", 10000, 16000),
]


def test_band_graph_is_path():
    g = build_band_adjacency_graph(BANDS)
    assert len(g.nodes) == 8 and len(g.edges) == 7
    assert np.allclose(g.degree(), [1, 2, 2, 2, 2, 2, 2, 1])


def test_band_node_axis_preserves_frequency_order():
    g = build_band_adjacency_graph(list(reversed(BANDS)))
    assert g.node_ids == tuple(f"band:{b[0]}" for b in BANDS)


def test_graph_id_independent_of_input_order():
    nodes = [GraphNode("b", "x"), GraphNode("a", "x"), GraphNode("c", "x")]
    edges = [GraphEdge("b", "c", 1.0), GraphEdge("a", "b", 2.0)]
    g1 = canonical_graph(nodes, edges, graph_family="t", edge_semantic="x")
    g2 = canonical_graph(nodes[::-1], edges[::-1], graph_family="t", edge_semantic="x")
    assert g1.graph_id == g2.graph_id
    assert g1.node_ids == ("a", "b", "c")


def test_self_loop_rejected():
    with pytest.raises(GraphContractError):
        canonical_graph([GraphNode("a", "x")], [GraphEdge("a", "a", 1)],
                        graph_family="t", edge_semantic="x")


def test_negative_weight_rejected():
    with pytest.raises(GraphContractError):
        canonical_graph([GraphNode("a", "x"), GraphNode("b", "x")],
                        [GraphEdge("a", "b", -1)],
                        graph_family="t", edge_semantic="x")


def test_heterogeneous_edge_types_rejected():
    with pytest.raises(GraphContractError):
        canonical_graph(
            [GraphNode("a", "x"), GraphNode("b", "x"), GraphNode("c", "x")],
            [GraphEdge("a", "b", 1, "e1"), GraphEdge("b", "c", 1, "e2")],
            graph_family="t", edge_semantic="mixed"
        )


def test_laplacian_symmetric_psd():
    L = build_band_adjacency_graph(BANDS).laplacian()
    assert np.allclose(L, L.T)
    assert np.min(np.linalg.eigvalsh(L)) > -1e-10


def test_zero_eigenvalues_equal_components():
    g = canonical_graph(
        [GraphNode(str(i), "x") for i in range(4)],
        [GraphEdge("0", "1", 1), GraphEdge("2", "3", 1)],
        graph_family="t", edge_semantic="x"
    )
    vals, _ = spectral_decomposition(g)
    ncomp, _ = g.connected_components()
    assert np.sum(vals < 1e-9) == ncomp == 2


def test_constant_signal_zero_dirichlet_energy():
    assert dirichlet_energy(build_band_adjacency_graph(BANDS), np.ones(8)) < 1e-12


def test_graph_fourier_roundtrip():
    g = build_band_adjacency_graph(BANDS)
    x = np.array([1, 2, 1, 3, 2, 4, 3, 5], dtype=float)
    vals, c, U = graph_fourier_transform(g, x)
    assert np.allclose(x, inverse_graph_fourier(c, U), atol=1e-10)


def test_smooth_signal_has_lower_dirichlet_than_spike():
    g = build_band_adjacency_graph(BANDS)
    smooth = np.linspace(0, 1, 8)
    spike = smooth.copy()
    spike[5] += 3
    assert dirichlet_energy(g, spike) > dirichlet_energy(g, smooth) * 10


def test_spike_has_more_high_graph_frequency_energy():
    g = build_band_adjacency_graph(BANDS)
    smooth = np.linspace(0, 1, 8)
    spike = smooth.copy()
    spike[5] += 3
    a = graph_spectral_energy(g, smooth)["high_graph_frequency_ratio"]
    b = graph_spectral_energy(g, spike)["high_graph_frequency_ratio"]
    assert b > a * 2


def test_heat_filter_identity_at_zero():
    g = build_band_adjacency_graph(BANDS)
    x = np.arange(8, dtype=float)
    assert np.allclose(heat_kernel_filter(g, x, 0), x)


def test_heat_filter_reduces_dirichlet_energy():
    g = build_band_adjacency_graph(BANDS)
    x = np.array([0, 0, 0, 0, 0, 4, 0, 0], dtype=float)
    y = heat_kernel_filter(g, x, .8)
    assert dirichlet_energy(g, y) < dirichlet_energy(g, x)


def test_polynomial_identity():
    g = build_band_adjacency_graph(BANDS)
    x = np.arange(8, dtype=float)
    assert np.allclose(polynomial_graph_filter(g, x, [1]), x)


def test_local_variation_localizes_spike():
    g = build_band_adjacency_graph(BANDS)
    x = np.zeros(8)
    x[4] = 5
    assert int(np.argmax(local_variation(g, x))) == 4


def test_event_graph_overlap_weight_one():
    events = [
        {"event_id": "e1", "event_type": "A", "start_ms": 0, "end_ms": 1000, "domain": "x"},
        {"event_id": "e2", "event_type": "B", "start_ms": 500, "end_ms": 1500, "domain": "y"},
    ]
    g = build_temporal_event_graph(events)
    assert len(g.edges) == 1 and np.isclose(g.edges[0].weight, 1)


def test_event_graph_gap_decay():
    events = [
        {"event_id": "e1", "event_type": "A", "start_ms": 0, "end_ms": 1000, "domain": "x"},
        {"event_id": "e2", "event_type": "B", "start_ms": 2000, "end_ms": 2500, "domain": "y"},
    ]
    g = build_temporal_event_graph(events, tau_ms=1000, max_gap_ms=2000)
    assert np.isclose(g.edges[0].weight, np.exp(-1), atol=1e-12)


def test_event_graph_does_not_invent_musical_label():
    events = [{
        "event_id": "e1", "event_type": "PHASE_RISK_REGION", "start_ms": 0, "end_ms": 1000,
        "domain": "stereo", "profile_id": "v1", "localization_precision_ms": 100,
    }]
    g = build_temporal_event_graph(events)
    payload = json.dumps(g.nodes[0].to_dict()).lower()
    assert g.nodes[0].label == "PHASE_RISK_REGION"
    assert "bad_chorus" not in payload and "vocal_problem" not in payload


def test_positive_correlation_graph_omits_negative_edge():
    C = np.array([[1, .8, -.9], [.8, 1, .2], [-.9, .2, 1.]])
    g = build_positive_correlation_graph(C, ["a", "b", "c"], threshold=.5)
    assert len(g.edges) == 1
    assert {g.edges[0].source, g.edges[0].target} == {"feature:a", "feature:b"}


def test_dense_guard():
    nodes = [GraphNode(f"n{i}", "x") for i in range(6)]
    edges = [GraphEdge(f"n{i}", f"n{i + 1}", 1) for i in range(5)]
    g = canonical_graph(nodes, edges, graph_family="p", edge_semantic="path")
    with pytest.raises(GraphContractError):
        spectral_decomposition(g, max_dense_nodes=5, k=None)


def test_graph_evidence_semantic_boundaries():
    e = graph_evidence(build_band_adjacency_graph(BANDS), np.linspace(0, 1, 8))
    assert e["zero_eigenvalue_count"] == 1
    assert any("not acoustic Hz" in s for s in e["semantic_boundaries"])


def test_save_graph_evidence_roundtrip(tmp_path):
    g = build_band_adjacency_graph(BANDS)
    save_graph_evidence(g, tmp_path, signal=np.linspace(0, 1, 8))
    js = json.loads((tmp_path / "graph_summary.json").read_text(encoding="utf-8"))
    z = np.load(tmp_path / "graph_arrays.npz")
    assert js["graph_id"] == g.graph_id
    assert z["adjacency"].shape == (8, 8)
    assert (tmp_path / "mamse012_manifest.json").exists()


def test_large_graph_sparse_path_guard():
    # Above max_dense_nodes, k=None must be blocked; k=2 via sparse is allowed
    nodes = [GraphNode(f"n{i}", "x") for i in range(600)]
    edges = [GraphEdge(f"n{i}", f"n{i + 1}", 1) for i in range(599)]
    g = canonical_graph(nodes, edges, graph_family="p", edge_semantic="path")
    with pytest.raises(GraphContractError):
        spectral_decomposition(g, max_dense_nodes=512, k=None)
    vals, vecs = spectral_decomposition(g, max_dense_nodes=512, k=2)
    assert vals.shape == (2,) and vecs.shape == (600, 2)
