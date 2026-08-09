"""Deterministic execution DAG models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    CACHE_HIT = "CACHE_HIT"
    CACHE_MISS = "CACHE_MISS"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ExecutionNode:
    node_id: str
    node_version: str
    dependencies: tuple[str, ...]
    compute: Callable[[dict[str, Any]], Any]
    cache_policy: str = "PERSISTENT"
    resource_class: str = "SMALL"
    parameters: dict[str, Any] = field(default_factory=dict)


def topological_order(nodes: list[ExecutionNode]) -> list[ExecutionNode]:
    by_id = {node.node_id: node for node in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate execution node ID")
    ordered: list[ExecutionNode] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            raise ValueError("execution graph contains a cycle")
        if node_id not in by_id:
            raise ValueError(f"missing dependency node: {node_id}")
        visiting.add(node_id)
        for dependency in by_id[node_id].dependencies:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)
        ordered.append(by_id[node_id])

    for item in nodes:
        visit(item.node_id)
    return ordered
