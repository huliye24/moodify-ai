"""MAMSE-012 graph builders: band path, temporal event, positive correlation."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .contracts import AuditoryGraph, GraphContractError, GraphEdge, GraphNode, canonical_graph


def build_band_adjacency_graph(bands: Sequence[tuple[str, float, float]]) -> AuditoryGraph:
    """Canonical 8-band path graph (ordered acoustic-band adjacency)."""
    if len(bands) < 2:
        raise GraphContractError("need at least two bands")
    ordered = sorted(bands, key=lambda b: float(b[1]))
    nodes = []
    for name, lo, hi in ordered:
        if not (0 <= lo < hi):
            raise GraphContractError("invalid band bounds")
        nodes.append(GraphNode(
            node_id=f"band:{name}",
            node_type="frequency_band",
            label=name,
            metadata={"lo_hz": float(lo), "hi_hz": float(hi), "canonical_order": len(nodes)},
        ))
    edges = [
        GraphEdge(a.node_id, b.node_id, 1.0, "frequency_adjacency",
                  {"semantic": "ordered adjacency only"})
        for a, b in zip(nodes[:-1], nodes[1:])
    ]
    return canonical_graph(
        nodes, edges,
        graph_family="canonical_band_path",
        edge_semantic="ordered acoustic-band adjacency",
        edge_authority="DETERMINISTIC_TOPOLOGY",
        provenance={"weight_semantics": "unit adjacency; not calibrated psychoacoustic similarity"},
    )


def _interval_gap_ms(a0: int, a1: int, b0: int, b1: int) -> int:
    if a1 < b0:
        return b0 - a1
    if b1 < a0:
        return a0 - b1
    return 0


def build_temporal_event_graph(
    events: Sequence[dict | object],
    *,
    tau_ms: float = 1000.0,
    max_gap_ms: int = 2500,
) -> AuditoryGraph:
    """Temporal event graph: interval-proximity edges with exp(-gap/tau) weights.

    Original TemporalEvent semantics are preserved; no musical label is
    invented.
    """
    if tau_ms <= 0 or max_gap_ms < 0:
        raise ValueError("invalid temporal graph parameters")
    rows = []
    for event in events:
        d = event if isinstance(event, dict) else event.to_dict()
        start, end = int(d["start_ms"]), int(d["end_ms"])
        if end <= start:
            raise GraphContractError("event end must exceed start")
        rows.append({
            "event_id": str(d["event_id"]),
            "event_type": str(d.get("event_type", "")),
            "domain": str(d.get("domain", "")),
            "start_ms": start,
            "end_ms": end,
            "profile_id": str(d.get("profile_id", "")),
            "localization_precision_ms": int(d.get("localization_precision_ms", 0)),
        })
    rows.sort(key=lambda r: (r["start_ms"], r["end_ms"], r["event_id"]))
    nodes = [
        GraphNode(node_id=f"event:{r['event_id']}", node_type="temporal_event",
                  label=r["event_type"], metadata={**r, "canonical_order": i})
        for i, r in enumerate(rows)
    ]
    edges = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            gap = _interval_gap_ms(a["start_ms"], a["end_ms"], b["start_ms"], b["end_ms"])
            if gap > max_gap_ms:
                if b["start_ms"] > a["end_ms"] + max_gap_ms:
                    break
                continue
            edges.append(GraphEdge(
                f"event:{a['event_id']}", f"event:{b['event_id']}",
                float(math.exp(-gap / tau_ms)), "temporal_proximity", {"gap_ms": int(gap)},
            ))
    return canonical_graph(
        nodes, edges,
        graph_family="temporal_event_graph",
        edge_semantic="time-interval proximity",
        edge_authority="DETERMINISTIC_DERIVED",
        provenance={"tau_ms": tau_ms, "max_gap_ms": max_gap_ms},
    )


def build_positive_correlation_graph(
    correlation: np.ndarray,
    feature_names: Sequence[str],
    *,
    threshold: float = 0.5,
) -> AuditoryGraph:
    """Positive-correlation graph from a symmetric correlation matrix.

    Negative correlations are omitted (never abs()'d); signed graphs are
    deferred.
    """
    C = np.asarray(correlation, dtype=float)
    names = tuple(feature_names)
    if C.shape != (len(names), len(names)):
        raise GraphContractError("correlation shape mismatch")
    if not np.allclose(C, C.T, atol=1e-8):
        raise GraphContractError("correlation must be symmetric")
    if threshold <= 0 or threshold >= 1:
        raise ValueError("threshold must be in (0,1)")
    nodes = [
        GraphNode(f"feature:{name}", "auditory_feature", label=name,
                  metadata={"canonical_order": i})
        for i, name in enumerate(names)
    ]
    edges = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = float(C[i, j])
            if np.isfinite(r) and r >= threshold:
                edges.append(GraphEdge(
                    f"feature:{names[i]}", f"feature:{names[j]}", r,
                    "positive_correlation", {"correlation": r},
                ))
    return canonical_graph(
        nodes, edges,
        graph_family="positive_correlation_graph",
        edge_semantic="positive empirical correlation",
        edge_authority="DATA_DERIVED",
        provenance={"threshold": threshold, "negative_edges_policy": "omitted; signed graph deferred"},
    )
