"""MAMSE-012 graph contracts: nodes, edges, AuditoryGraph, canonicalization.

Graph topology is part of the scientific model and is versioned via
graph_id. v0.1 supports undirected, nonnegative, homogeneous-edge graphs
for spectral operators; signed/directed/multiplex graphs are deferred.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

SCHEMA_VERSION = "mamse012-graph-v0.1"
ALGORITHM_VERSION = "mamse012-gsp-v0.1"

EPS = 1e-12


class GraphContractError(ValueError):
    pass


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    weight: float
    edge_type: str = "structural"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        a, b = sorted((self.source, self.target))
        return {
            "source": a,
            "target": b,
            "weight": float(self.weight),
            "edge_type": self.edge_type,
            "metadata": dict(self.metadata),
        }


@dataclass
class AuditoryGraph:
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    graph_family: str
    edge_semantic: str
    edge_authority: str = "EXPERIMENTAL"
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.nodes:
            raise GraphContractError("graph must have at least one node")
        ids = [n.node_id for n in self.nodes]
        if len(set(ids)) != len(ids):
            raise GraphContractError("duplicate node_id")
        node_set = set(ids)
        seen = set()
        edge_types = set()
        for e in self.edges:
            if e.source == e.target:
                raise GraphContractError("self loops are not allowed in v0.1")
            if e.source not in node_set or e.target not in node_set:
                raise GraphContractError("edge references unknown node")
            if not np.isfinite(e.weight) or e.weight <= 0:
                raise GraphContractError("edge weights must be finite and > 0")
            key = tuple(sorted((e.source, e.target)))
            if key in seen:
                raise GraphContractError("duplicate undirected edge")
            seen.add(key)
            edge_types.add(e.edge_type)
        if len(edge_types) > 1:
            raise GraphContractError("v0.1 spectral graph view requires homogeneous edge semantics")

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(n.node_id for n in self.nodes)

    @property
    def index(self) -> dict[str, int]:
        return {nid: i for i, nid in enumerate(self.node_ids)}

    @property
    def graph_id(self) -> str:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "algorithm_version": ALGORITHM_VERSION,
            "graph_family": self.graph_family,
            "edge_semantic": self.edge_semantic,
            "edge_authority": self.edge_authority,
            "nodes": [n.to_dict() for n in sorted(self.nodes, key=lambda n: n.node_id)],
            "edges": [
                e.to_dict()
                for e in sorted(self.edges, key=lambda e: tuple(sorted((e.source, e.target))) + (e.edge_type,))
            ],
            "provenance": self.provenance,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        return "agraph-" + hashlib.sha256(raw).hexdigest()[:16]

    def adjacency(self) -> np.ndarray:
        n = len(self.nodes)
        W = np.zeros((n, n), dtype=float)
        idx = self.index
        for e in self.edges:
            i, j = idx[e.source], idx[e.target]
            W[i, j] = W[j, i] = float(e.weight)
        return W

    def degree(self) -> np.ndarray:
        return self.adjacency().sum(axis=1)

    def laplacian(self, normalized: bool = False) -> np.ndarray:
        W = self.adjacency()
        d = W.sum(axis=1)
        if not normalized:
            return np.diag(d) - W
        invsqrt = np.zeros_like(d)
        nz = d > EPS
        invsqrt[nz] = 1.0 / np.sqrt(d[nz])
        D = np.diag(invsqrt)
        return np.eye(len(d)) - D @ W @ D

    def connected_components(self) -> tuple[int, np.ndarray]:
        W = self.adjacency()
        try:
            from scipy.sparse.csgraph import connected_components as scipy_cc
            from scipy import sparse
            ncomp, labels = scipy_cc(sparse.csr_matrix(W), directed=False, return_labels=True)
            return int(ncomp), labels.astype(int)
        except Exception:
            labels = np.full(len(self.nodes), -1, dtype=int)
            comp = 0
            for start in range(len(self.nodes)):
                if labels[start] >= 0:
                    continue
                stack = [start]
                labels[start] = comp
                while stack:
                    i = stack.pop()
                    for j in np.where(W[i] > 0)[0]:
                        if labels[j] < 0:
                            labels[j] = comp
                            stack.append(int(j))
                comp += 1
            return comp, labels


def _node_order_key(node: GraphNode) -> tuple[float, str]:
    order = node.metadata.get("canonical_order")
    return (float(order) if order is not None else float("inf"), node.node_id)


def canonical_graph(
    nodes: Sequence[GraphNode],
    edges: Sequence[GraphEdge],
    *,
    graph_family: str,
    edge_semantic: str,
    edge_authority: str = "EXPERIMENTAL",
    provenance: dict[str, Any] | None = None,
) -> AuditoryGraph:
    return AuditoryGraph(
        nodes=tuple(sorted(nodes, key=_node_order_key)),
        edges=tuple(sorted(edges, key=lambda e: tuple(sorted((e.source, e.target))) + (e.edge_type,))),
        graph_family=graph_family,
        edge_semantic=edge_semantic,
        edge_authority=edge_authority,
        provenance=dict(provenance or {}),
    )
