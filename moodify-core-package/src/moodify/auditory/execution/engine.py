"""Deterministic local DAG executor with cache verification and resume."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

from moodify.auditory.execution.cache import CacheCorruptionError, LocalCache
from moodify.auditory.execution.checkpoints import RunManifest
from moodify.auditory.execution.diagnostics import ExecutionDiagnostics
from moodify.auditory.execution.graph import ExecutionNode, topological_order
from moodify.auditory.execution.identity import AnalysisIdentity
from moodify.auditory.identity import logical_id


class ExecutionInterrupted(RuntimeError):
    """Controlled interruption used to verify checkpoint/resume behavior."""


class ExecutionEngine:
    PLAN_VERSION = "phase1-local-plan-v1"

    def __init__(self, identity: AnalysisIdentity, cache: LocalCache,
                 manifest_path: Path | None = None):
        self.identity = identity
        self.cache = cache
        self.diagnostics = ExecutionDiagnostics()
        self.manifest = RunManifest(
            manifest_path,
            run_id=logical_id("run", {"analysis": identity.logical_id, "plan": self.PLAN_VERSION}),
            source_sha256=identity.source_sha256,
            plan_version=self.PLAN_VERSION,
        ) if manifest_path else None

    def dry_run(self, nodes: list[ExecutionNode]) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        hashes: dict[str, str] = {}
        for node in topological_order(nodes):
            dependencies = {dep: hashes.get(dep, "unknown") for dep in node.dependencies}
            key = self.identity.node_key(node.node_id, node.node_version,
                                         node.parameters, dependencies)
            state = "CACHE_MISS"
            if all(value != "unknown" for value in dependencies.values()):
                try:
                    hit = self.cache.get(self.identity.source_sha256, key, dependencies)
                    if hit:
                        state = "CACHE_HIT"
                        hashes[node.node_id] = hit[1]
                except CacheCorruptionError:
                    state = "CACHE_CORRUPT"
            result.append({"node_id": node.node_id, "state": state, "cache_key": key})
        return result

    def run(self, nodes: list[ExecutionNode], stop_after: str | None = None) -> dict[str, Any]:
        outputs: dict[str, Any] = {}
        hashes: dict[str, str] = {}
        for node in topological_order(nodes):
            dependency_hashes = {dep: hashes[dep] for dep in node.dependencies}
            key = self.identity.node_key(node.node_id, node.node_version,
                                         node.parameters, dependency_hashes)
            cached = None
            if node.cache_policy == "PERSISTENT":
                try:
                    cached = self.cache.get(
                        self.identity.source_sha256, key, dependency_hashes,
                    )
                except CacheCorruptionError:
                    self.diagnostics.cache_corruptions += 1
                    self.diagnostics.cache_invalidations += 1
                    self.cache.remove_entry(self.identity.source_sha256, key)
            if cached:
                outputs[node.node_id], hashes[node.node_id], byte_size = cached
                self.diagnostics.cache_hits += 1
                self.diagnostics.nodes_reused += 1
                self.diagnostics.bytes_read += byte_size
            else:
                self.diagnostics.cache_misses += int(node.cache_policy == "PERSISTENT")
                try:
                    value = node.compute({dep: outputs[dep] for dep in node.dependencies})
                except Exception:
                    if self.manifest:
                        self.manifest.failed(node.node_id)
                    raise
                self.diagnostics.nodes_executed += 1
                if node.node_id in {"auditory_representation", "temporal_events"}:
                    self.diagnostics.transform_computed(node.node_id)
                outputs[node.node_id] = value
                if node.cache_policy == "PERSISTENT":
                    content_hash, byte_size = self.cache.put(
                        self.identity.source_sha256, key, value,
                        node.node_id, node.node_version, dependency_hashes,
                    )
                    self.diagnostics.bytes_written += byte_size
                else:
                    content_hash = _logical_hash(value)
                hashes[node.node_id] = content_hash
            if node.node_id == "decoded_audio" and not cached:
                self.diagnostics.decoded_source_count += 1
            if self.manifest:
                self.manifest.completed(node.node_id, key)
            if stop_after == node.node_id:
                raise ExecutionInterrupted(f"controlled stop after {node.node_id}")
        if self.manifest:
            self.manifest.finish()
        return outputs


def _logical_hash(value: Any) -> str:
    if isinstance(value, np.ndarray):
        digest = hashlib.sha256()
        digest.update(str(value.dtype).encode())
        digest.update(str(value.shape).encode())
        digest.update(value.tobytes())
        return digest.hexdigest()
    return logical_id("content", value, 64).split("-", 1)[1]
