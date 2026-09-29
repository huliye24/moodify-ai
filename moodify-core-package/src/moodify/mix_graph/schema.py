"""schema.py — moodify.mix_graph/0.1 schema and validation.

The graph JSON is designed as the future MSP protocol payload (adjudicated
2026-09-29): `nodes` carries the full render-relevant state; `intent`,
`provenance` and `verification` are session metadata that never affect audio
output. v0.1 status is EXPERIMENTAL; freeze gate = golden case + deterministic
replay evidence (see docs/plan/2026-09-20_MIX_GRAPH_V01_PROPOSAL.md §5.1).
"""

from __future__ import annotations

import json
import re
from typing import Any

from moodify.mix_graph.providers import ProviderError, get_provider

SCHEMA_ID = "moodify.mix_graph/0.1"
STATUS = "EXPERIMENTAL"

NODE_TYPES = ("eq", "compressor", "stereo", "limiter")

AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".aiff", ".aif", ".m4a"}

_TOP_REQUIRED = {"schema", "source", "nodes"}
_TOP_OPTIONAL = {"intent", "verification", "provenance", "notes", "status"}
_NODE_REQUIRED = {"id", "type", "parameters"}
_NODE_OPTIONAL = {"enabled", "reason", "evidence_refs"}
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class MixGraphError(ValueError):
    """Raised for any invalid mix graph document or session input."""


def validate_graph(data: Any) -> dict[str, Any]:
    """Validate a graph document and return a canonicalized copy.

    Raises MixGraphError with a precise message on the first violation.
    Parameter-range validation is delegated to the node providers.
    """
    if not isinstance(data, dict):
        raise MixGraphError("graph must be a JSON object")
    unknown = set(data) - _TOP_REQUIRED - _TOP_OPTIONAL
    if unknown:
        raise MixGraphError(f"graph has unknown keys: {sorted(unknown)}")
    missing = _TOP_REQUIRED - set(data)
    if missing:
        raise MixGraphError(f"graph is missing required keys: {sorted(missing)}")
    if data["schema"] != SCHEMA_ID:
        raise MixGraphError(f"unsupported schema; expected {SCHEMA_ID}")
    status = data.get("status", STATUS)
    if status != STATUS:
        raise MixGraphError(f"unsupported status '{status}'; expected {STATUS}")
    if not isinstance(data["source"], str) or not data["source"].strip():
        raise MixGraphError("source must be a non-empty string")

    nodes = data["nodes"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 32:
        raise MixGraphError("nodes must be a list of 1..32 entries")

    canonical_nodes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for i, node in enumerate(nodes):
        canonical_nodes.append(_validate_node(i, node, seen_ids))

    verification = data.get("verification")
    if verification is not None:
        if not isinstance(verification, dict):
            raise MixGraphError("verification must be an object")
        unknown = set(verification) - {"max_peak_dbfs"}
        if unknown:
            raise MixGraphError(f"verification has unknown keys: {sorted(unknown)}")
        canonical_verification: dict[str, Any] | None = None
        if "max_peak_dbfs" in verification:
            limit = verification["max_peak_dbfs"]
            if isinstance(limit, bool) or not isinstance(limit, (int, float)) \
                    or not -60.0 <= float(limit) <= 0.0:
                raise MixGraphError("verification.max_peak_dbfs must be a number in [-60, 0]")
            canonical_verification = {"max_peak_dbfs": float(limit)}
    else:
        canonical_verification = None

    for key in ("intent", "notes"):
        value = data.get(key)
        if value is not None and not isinstance(value, str):
            raise MixGraphError(f"{key} must be a string")
    provenance = data.get("provenance")
    if provenance is not None:
        if not isinstance(provenance, dict):
            raise MixGraphError("provenance must be an object")
        unknown = set(provenance) - {"created_by", "created_at", "notes"}
        if unknown:
            raise MixGraphError(f"provenance has unknown keys: {sorted(unknown)}")

    canonical: dict[str, Any] = {
        "schema": SCHEMA_ID,
        "status": STATUS,
        "source": data["source"],
        "nodes": canonical_nodes,
    }
    if data.get("intent") is not None:
        canonical["intent"] = data["intent"]
    if canonical_verification is not None:
        canonical["verification"] = canonical_verification
    if provenance is not None:
        canonical["provenance"] = provenance
    if data.get("notes") is not None:
        canonical["notes"] = data["notes"]
    return canonical


def _validate_node(index: int, node: Any, seen_ids: set[str]) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise MixGraphError(f"node {index} must be an object")
    unknown = set(node) - _NODE_REQUIRED - _NODE_OPTIONAL
    if unknown:
        raise MixGraphError(f"node {index} has unknown keys: {sorted(unknown)}")
    missing = _NODE_REQUIRED - set(node)
    if missing:
        raise MixGraphError(f"node {index} is missing required keys: {sorted(missing)}")

    node_id = node["id"]
    if not isinstance(node_id, str) or not _ID_PATTERN.match(node_id):
        raise MixGraphError(f"node {index} id must match {_ID_PATTERN.pattern}")
    if node_id in seen_ids:
        raise MixGraphError(f"duplicate node id '{node_id}'")
    seen_ids.add(node_id)

    node_type = node["type"]
    if not isinstance(node_type, str) or node_type not in NODE_TYPES:
        raise MixGraphError(
            f"node '{node_id}' type must be one of: {', '.join(NODE_TYPES)}"
        )

    enabled = node.get("enabled", True)
    if not isinstance(enabled, bool):
        raise MixGraphError(f"node '{node_id}' enabled must be a boolean")
    reason = node.get("reason")
    if reason is not None and not isinstance(reason, str):
        raise MixGraphError(f"node '{node_id}' reason must be a string")
    evidence_refs = node.get("evidence_refs", [])
    if not isinstance(evidence_refs, list) \
            or not all(isinstance(ref, str) for ref in evidence_refs):
        raise MixGraphError(f"node '{node_id}' evidence_refs must be a list of strings")

    try:
        parameters = get_provider(node_type).validate_parameters(node["parameters"])
    except ProviderError as exc:
        raise MixGraphError(f"node '{node_id}' parameters invalid: {exc}") from exc

    canonical: dict[str, Any] = {
        "id": node_id,
        "type": node_type,
        "enabled": enabled,
        "parameters": parameters,
    }
    if reason is not None:
        canonical["reason"] = reason
    if evidence_refs:
        canonical["evidence_refs"] = evidence_refs
    return canonical


def canonical_json(data: dict[str, Any]) -> str:
    """Deterministic JSON serialization used for digests and file output."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
