"""graph.py — MixGraph model: load/save, digest, and preset derivation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from moodify.mix_graph.schema import (
    AUDIO_EXTENSIONS,
    MixGraphError,
    SCHEMA_ID,
    canonical_json,
    validate_graph,
)


@dataclass
class MixGraph:
    """A validated serial mix graph bound to a resolved source path."""

    source: Path
    nodes: list[dict[str, Any]]
    intent: str | None = None
    verification: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    notes: str | None = None
    graph_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema": SCHEMA_ID,
            "status": "EXPERIMENTAL",
            "source": str(self.source),
            "nodes": self.nodes,
        }
        if self.intent is not None:
            data["intent"] = self.intent
        if self.verification is not None:
            data["verification"] = self.verification
        if self.provenance is not None:
            data["provenance"] = self.provenance
        if self.notes is not None:
            data["notes"] = self.notes
        return data

    def canonical_json(self) -> str:
        return canonical_json(self.to_dict())

    def digest(self) -> str:
        """sha256 over the render-relevant part of the graph (schema + nodes).

        provenance/intent/notes never affect audio and are excluded, so the
        digest names the render identity of the graph.
        """
        render_identity = {"schema": SCHEMA_ID, "nodes": self.nodes}
        payload = json.dumps(render_identity, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def graph_from_dict(data: dict[str, Any], base_dir: Path) -> MixGraph:
    """Validate a raw graph document and bind relative paths to base_dir."""
    canonical = validate_graph(data)
    source = (base_dir / canonical["source"]).resolve()
    if source.suffix.lower() not in AUDIO_EXTENSIONS:
        raise MixGraphError(f"unsupported audio extension: {source.suffix or '(none)'}")
    return MixGraph(
        source=source,
        nodes=canonical["nodes"],
        intent=canonical.get("intent"),
        verification=canonical.get("verification"),
        provenance=canonical.get("provenance"),
        notes=canonical.get("notes"),
    )


def load_graph(path: Path) -> MixGraph:
    """Load a graph JSON file; relative source paths resolve beside the file."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MixGraphError(f"cannot read graph: {exc}") from exc
    graph = graph_from_dict(data, path.resolve().parent)
    graph.graph_path = path.resolve()
    return graph


def save_graph(graph: MixGraph, path: Path) -> Path:
    """Write the graph in canonical JSON form; refuse to overwrite."""
    path = Path(path)
    if path.exists():
        raise MixGraphError(f"refusing to overwrite existing graph: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph.canonical_json(), encoding="utf-8")
    return path


def graph_from_preset(preset_key: str, source: str) -> MixGraph:
    """Derive a starter mix graph from a v0.1 preset.

    Only the four v0.1 node types are representable: preset reverb
    (P10-P12) and harmonic drive (P13) are dropped and listed in notes —
    never silently translated into another node.
    """
    from moodify.v01_presets import get_preset

    preset = get_preset(preset_key)
    if preset is None:
        raise MixGraphError(f"unknown preset '{preset_key}'")
    params = preset["params"]

    eq_bands: list[dict[str, Any]] = []
    if abs(params["P02_vocal_presence_gain"]) > 0.01:
        eq_bands.append({"type": "peak", "freq_hz": params["P01_vocal_presence_freq"],
                         "gain_db": params["P02_vocal_presence_gain"],
                         "q": params["P03_vocal_presence_q"]})
    if abs(params["P05_proximity_low_gain"]) > 0.01:
        eq_bands.append({"type": "lowshelf", "freq_hz": params["P04_proximity_low_freq"],
                         "gain_db": params["P05_proximity_low_gain"]})
    if abs(params["P15_high_shelf_gain"]) > 0.01:
        eq_bands.append({"type": "highshelf", "freq_hz": params["P14_high_shelf_freq"],
                         "gain_db": params["P15_high_shelf_gain"]})

    nodes: list[dict[str, Any]] = []
    if eq_bands:
        nodes.append({
            "id": "eq_1",
            "type": "eq",
            "enabled": True,
            "parameters": {"bands": eq_bands},
            "reason": f"eq bands derived from preset '{preset_key}'",
        })
    nodes.append({
        "id": "comp_1",
        "type": "compressor",
        "enabled": True,
        "parameters": {
            "threshold_db": params["P09_compression_threshold"],
            "ratio": params["P06_compression_ratio"],
            "attack_ms": params["P07_compression_attack"],
            "release_ms": params["P08_compression_release"],
        },
        "reason": f"compression derived from preset '{preset_key}'",
    })
    if abs(params["P12_reverb_width"] - 1.0) > 0.01:
        nodes.append({
            "id": "stereo_1",
            "type": "stereo",
            "enabled": True,
            "parameters": {"width": params["P12_reverb_width"]},
            "reason": "width heuristic from preset reverb-width parameter",
        })
    nodes.append({
        "id": "limiter_1",
        "type": "limiter",
        "enabled": True,
        "parameters": {"ceiling_db": -1.0},
        "reason": "hard ceiling at -1 dBFS (repo-standard ceiling semantics)",
    })

    dropped = []
    if params["P11_reverb_dry_wet"] > 0.005:
        dropped.append("reverb")
    if params["P13_harmonic_drive"] > 0.002:
        dropped.append("harmonic_drive")
    notes = "derived from preset '{key}'; not representable in v0.1: {dropped}".format(
        key=preset_key, dropped=", ".join(dropped) if dropped else "none")

    # MixGraph always holds canonical nodes: digests must be identical whether
    # a graph came from a file (validate_graph) or from a preset derivation.
    from moodify.mix_graph.providers import get_provider

    for node in nodes:
        node["parameters"] = get_provider(node["type"]).validate_parameters(node["parameters"])

    return MixGraph(
        source=Path(source),
        nodes=nodes,
        intent=preset["description"],
        provenance={"created_by": "moodify.mix_graph.graph_from_preset",
                    "notes": f"preset={preset_key}"},
        notes=notes,
    )
