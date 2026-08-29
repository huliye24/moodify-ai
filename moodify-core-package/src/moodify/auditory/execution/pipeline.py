"""Canonical single-decode local Phase-I auditory execution path."""

from __future__ import annotations

import hashlib
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from moodify.auditory.decode import decode
from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.execution.cache import LocalCache
from moodify.auditory.execution.engine import ExecutionEngine
from moodify.auditory.execution.graph import ExecutionNode
from moodify.auditory.execution.identity import AnalysisIdentity
from moodify.auditory.metrics import compute_metrics
from moodify.auditory.representation.build import build_representation
from moodify.auditory.representation.scales import REPRESENTATION_VERSION


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_analysis_nodes(path: Path, sample_rate: int = 48000,
                         rule_version: str = "auditory-rules-v1") -> list[ExecutionNode]:
    path = Path(path)

    def decode_node(_inputs):
        decoded = decode(path, sample_rate)
        probe = asdict(decoded.probe)
        probe.pop("absolute_path", None)
        return {"samples": decoded.samples, "sample_rate": decoded.sample_rate, "probe": probe}

    def metrics_node(inputs):
        item = inputs["decoded_audio"]
        return compute_metrics(item["samples"], item["sample_rate"], SimpleNamespace(**item["probe"]))

    def representation_node(inputs):
        item = inputs["decoded_audio"]
        representation = build_representation(
            item["samples"], item["sample_rate"], item["probe"]["sha256"],
            global_metrics=inputs["global_measurements"],
        )
        return representation.to_dict()

    def events_node(inputs):
        item = inputs["decoded_audio"]
        return run_temporal_hearing(item["samples"], item["sample_rate"]).to_dict()

    def judgment_node(inputs):
        events = inputs["temporal_events"]["events"]
        return {
            "classification": "MEASURED_RISK" if events else "NO_MEASURED_RISK",
            "evidence_state": "SUPPORTED",
            "workflow_decision": "REVIEW_REQUIRED" if events else "PASS_TO_LISTENING",
            "rule_version": rule_version,
            "human_authority": "Final artistic judgment requires human listening.",
        }

    def evidence_node(inputs):
        return {
            "source_sha256": inputs["decoded_audio"]["probe"]["sha256"],
            "measurement_registry_version": "measurement-registry-v1",
            "representation_id": inputs["auditory_representation"]["representation_id"],
            "temporal_profile_id": inputs["temporal_events"]["profile_id"],
            "judgment": inputs["judgment"],
            "coverage": ["level", "integrity", "spectrum", "stereo"],
        }

    def report_node(inputs):
        return {
            "product": "Moodify — The Ear of AI",
            "question": "Can machines learn to hear?",
            "measurements": inputs["global_measurements"],
            "events": inputs["temporal_events"]["events"],
            "judgment": inputs["judgment"],
            "evidence": inputs["evidence_bundle"],
        }

    return [
        ExecutionNode("decoded_audio", "ffmpeg-decode-v1", (), decode_node,
                      resource_class="LARGE", parameters={"sample_rate": sample_rate}),
        ExecutionNode("global_measurements", "measurement-registry-v1", ("decoded_audio",), metrics_node),
        ExecutionNode("auditory_representation", REPRESENTATION_VERSION,
                      ("decoded_audio", "global_measurements"),
                      representation_node, resource_class="MEDIUM"),
        ExecutionNode("temporal_events", "temporal-hearing-v1", ("decoded_audio",), events_node),
        ExecutionNode("judgment", "fail-closed-v1", ("global_measurements", "temporal_events"),
                      judgment_node, parameters={"rule_version": rule_version}),
        ExecutionNode("evidence_bundle", "evidence-bundle-v1",
                      ("decoded_audio", "auditory_representation", "temporal_events", "judgment"),
                      evidence_node),
        ExecutionNode("report", "auditory-report-v1",
                      ("global_measurements", "temporal_events", "judgment", "evidence_bundle"),
                      report_node, cache_policy="RUN_ONLY"),
    ]


def run_local_analysis(path: Path, cache_root: Path, manifest_path: Path | None = None,
                       sample_rate: int = 48000, rule_version: str = "auditory-rules-v1"):
    digest = source_sha256(path)
    identity = AnalysisIdentity(
        source_sha256=digest,
        analysis_profile_id=f"analysis-{sample_rate}-v1",
        temporal_profile_id="temporal-hearing-v1",
        representation_version=REPRESENTATION_VERSION,
        measurement_registry_version="measurement-registry-v1",
    )
    engine = ExecutionEngine(identity, LocalCache(cache_root), manifest_path)
    outputs = engine.run(local_analysis_nodes(path, sample_rate, rule_version))
    return outputs, engine.diagnostics
