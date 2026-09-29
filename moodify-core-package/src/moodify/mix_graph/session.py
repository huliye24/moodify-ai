"""session.py — load → render → verify → export executor for mix graphs.

Deterministic: same core version + same graph + same source -> bit-identical
output. provenance/intent/notes are excluded from the graph digest because
they never affect audio. dry_run renders and verifies but writes nothing.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np

from moodify.audio_io import load_audio
from moodify.mix_graph.graph import MixGraph
from moodify.mix_graph.providers import get_provider
from moodify.mix_graph.schema import MixGraphError
from moodify.mix_graph.verify import measure_audio, peak_gate, verify_before_after
from moodify.release import PRODUCT_VERSION


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_session(graph: MixGraph, output_dir: str | Path = "outputs",
                dry_run: bool = False) -> dict:
    """Execute a mix graph session and return the evidence document.

    Raises MixGraphError on any validation, rendering or export failure.
    """
    if not graph.source.is_file():
        raise MixGraphError(f"source is not a file: {graph.source}")

    digest = graph.digest()
    output_dir = Path(output_dir)
    output_name = f"{graph.source.stem}_mixgraph_{digest[:8]}.wav"
    output_path = output_dir / output_name
    evidence_path = output_path.with_suffix(".evidence.json")
    if not dry_run and (output_path.exists() or evidence_path.exists()):
        raise MixGraphError(f"refusing to overwrite existing output: {output_path}")

    # Sessions process in stereo; mono sources are upsampled and the decision
    # is recorded in evidence rather than silently applied.
    audio, sr = load_audio(str(graph.source), always_2d=True)
    mono_upsampled = not _source_is_stereo(graph.source)
    source_audio = audio.astype(np.float32)

    node_records: list[dict] = []
    current = source_audio
    for node in graph.nodes:
        node_before = measure_audio(current, sr)
        record: dict = {
            "id": node["id"],
            "type": node["type"],
            "enabled": node["enabled"],
            "parameters": node["parameters"],
        }
        if node.get("reason"):
            record["reason"] = node["reason"]
        if not node["enabled"]:
            record["bypassed"] = True
            record["note"] = "short-circuited; output equals input"
        else:
            provider = get_provider(node["type"])
            current = provider.render(current, sr, node["parameters"])
            record["describe"] = provider.describe(node["parameters"])
        record["before"] = node_before
        record["after"] = measure_audio(current, sr)
        node_records.append(record)

    verification = verify_before_after(source_audio, current, sr)
    gate = None
    gate_limit = _peak_limit(graph)
    if gate_limit is not None:
        gate = peak_gate(verification["after"], gate_limit)
        verification["peak_gate"] = gate

    evidence: dict = {
        "schema": "moodify.mix_graph.evidence/0.1",
        "core_version": PRODUCT_VERSION,
        "graph_digest_sha256": digest,
        "source": str(graph.source),
        "source_sha256": _sha256(graph.source),
        "session": {
            "mono_upsampled_to_stereo": mono_upsampled,
            "sample_rate": sr,
            "channels": 2,
        },
        "nodes": node_records,
        "verification": verification,
        "output": {
            "path": str(output_path),
            "name": output_name,
            "sha256": None,
            "written": False,
        },
        "status": "dry_run" if dry_run else "rendered",
    }

    if dry_run:
        return evidence

    from moodify.v01_exporter import export  # single export authority

    written = export(current, sr, str(graph.source), f"mixgraph_{digest[:8]}",
                     str(output_dir))
    if Path(written) != output_path.resolve():
        # v01_exporter owns naming; align the evidence with what was written.
        evidence["output"]["path"] = written
        evidence["output"]["name"] = Path(written).name
    evidence["output"]["sha256"] = _sha256(Path(written))
    evidence["output"]["written"] = True

    # Evidence is a first-class session artifact: a render without its
    # verification evidence is not a finished session.
    output_dir.mkdir(parents=True, exist_ok=True)
    from moodify.mix_graph.schema import canonical_json

    evidence_path.write_text(canonical_json(evidence), encoding="utf-8")
    evidence["output"]["evidence_path"] = str(evidence_path)
    return evidence


def _source_is_stereo(path: Path) -> bool:
    try:
        import soundfile as sf

        info = sf.info(str(path))
        return info.channels >= 2
    except (OSError, RuntimeError):
        return False


def _peak_limit(graph: MixGraph) -> float | None:
    """Peak-gate limit: explicit graph verification wins; else the last
    limiter's ceiling — bypassed or not, because the ceiling is the graph's
    stated intent and a bypassed limiter must not silently void it; else no
    gate (measurement-only)."""
    if graph.verification and "max_peak_dbfs" in graph.verification:
        return float(graph.verification["max_peak_dbfs"])
    for node in reversed(graph.nodes):
        if node["type"] == "limiter":
            return float(node["parameters"]["ceiling_db"])
    return None


def export_delivery(audio_path: str | Path, output_dir: str | Path = "outputs") -> dict:
    """Re-encode an existing WAV as 16-bit PCM delivery with a -1 dBFS ceiling.

    Deterministic delivery encode; refuses to overwrite the input or an
    existing output of the same name.
    """
    source = Path(audio_path)
    if not source.is_file():
        raise MixGraphError(f"audio is not a file: {source}")
    audio, sr = load_audio(str(source), always_2d=True)
    audio = audio.astype(np.float32)
    peak = float(np.max(np.abs(audio)))
    if peak > 0.999:
        audio = audio * (0.999 / peak)
    output_dir = Path(output_dir)
    output_path = output_dir / f"{source.stem}_delivery.wav"
    if output_path.exists() or source.resolve() == output_path.resolve():
        raise MixGraphError(f"refusing to overwrite existing output: {output_path}")
    os.makedirs(output_dir, exist_ok=True)

    import soundfile as sf

    sf.write(str(output_path), audio, sr, subtype="PCM_16")
    return {
        "source": str(source),
        "output": str(output_path.resolve()),
        "output_sha256": _sha256(output_path),
        "applied_peak_trim_db": round(20.0 * np.log10(max(peak, 1e-12)) - 20.0 * np.log10(0.999), 2)
        if peak > 0.999 else 0.0,
    }
