"""MFY-PHASE1-DEPTH-006 local execution correctness gates."""

from __future__ import annotations

import json

import numpy as np
import pytest

from moodify.auditory.execution import (
    AnalysisIdentity,
    ExecutionEngine,
    ExecutionInterrupted,
    ExecutionNode,
    FeatureBus,
    LocalCache,
)
from moodify.auditory.execution.chunking import chunked_peak_rms
from moodify.auditory.execution.planner import ExecutionMode, build_plan


def _identity(**changes) -> AnalysisIdentity:
    values = {
        "source_sha256": "a" * 64,
        "analysis_profile_id": "analysis-v1",
        "temporal_profile_id": "temporal-v1",
        "representation_version": "rep-v1",
        "measurement_registry_version": "measurement-v1",
    }
    values.update(changes)
    return AnalysisIdentity(**values)


def _nodes(calls: dict[str, int], rule_version: str = "rule-v1"):
    def decoded(_):
        calls["decode"] = calls.get("decode", 0) + 1
        return {"samples": np.arange(32, dtype=np.float32), "sample_rate": 8}

    def features(inputs):
        calls["transform"] = calls.get("transform", 0) + 1
        x = inputs["decoded_audio"]["samples"]
        return {"peak": float(np.max(x)), "energy": float(np.sum(x * x))}

    def judgment(inputs):
        calls["judgment"] = calls.get("judgment", 0) + 1
        return {"rule": rule_version, "peak": inputs["features"]["peak"]}

    return [
        ExecutionNode("decoded_audio", "decode-v1", (), decoded, resource_class="LARGE"),
        ExecutionNode("features", "features-v1", ("decoded_audio",), features,
                      resource_class="MEDIUM"),
        ExecutionNode("judgment", "judgment-v1", ("features",), judgment,
                      parameters={"rule_version": rule_version}),
    ]


def test_analysis_identity_and_semantic_invalidation():
    base = _identity()
    same = _identity()
    assert base.logical_id == same.logical_id
    assert base.node_key("features", "v1") == same.node_key("features", "v1")
    assert base.node_key("features", "v1") != _identity(source_sha256="b" * 64).node_key("features", "v1")
    assert base.node_key("features", "v1") != base.node_key("features", "v2")
    assert base.node_key("features", "v1") != _identity(representation_version="rep-v2").node_key("features", "v1")


def test_cold_warm_equivalence_and_single_decode(tmp_path):
    cache = LocalCache(tmp_path / "cache")
    cold_calls: dict[str, int] = {}
    cold = ExecutionEngine(_identity(), cache)
    first = cold.run(_nodes(cold_calls))
    assert cold_calls == {"decode": 1, "transform": 1, "judgment": 1}
    assert cold.diagnostics.decoded_source_count == 1

    warm_calls: dict[str, int] = {}
    warm = ExecutionEngine(_identity(), cache)
    second = warm.run(_nodes(warm_calls))
    assert warm_calls == {}
    assert warm.diagnostics.cache_hits == 3
    assert warm.diagnostics.nodes_reused == 3
    assert warm.diagnostics.decoded_source_count == 0
    assert first["judgment"] == second["judgment"]
    assert np.array_equal(first["decoded_audio"]["samples"], second["decoded_audio"]["samples"])


def test_rule_only_change_reuses_decode_and_features(tmp_path):
    cache = LocalCache(tmp_path / "cache")
    ExecutionEngine(_identity(), cache).run(_nodes({}))
    calls: dict[str, int] = {}
    engine = ExecutionEngine(_identity(), cache)
    result = engine.run(_nodes(calls, "rule-v2"))
    assert calls == {"judgment": 1}
    assert engine.diagnostics.cache_hits == 2
    assert result["judgment"]["rule"] == "rule-v2"


def test_corrupt_cache_is_recomputed_not_trusted(tmp_path):
    cache = LocalCache(tmp_path / "cache")
    ExecutionEngine(_identity(), cache).run(_nodes({}))
    feature_payload = next(
        p for p in cache.root.rglob("payload.json")
        if json.loads((p.parent / "manifest.json").read_text())["node_id"] == "features"
    )
    feature_payload.write_text("corrupt", encoding="utf-8")
    calls: dict[str, int] = {}
    engine = ExecutionEngine(_identity(), cache)
    result = engine.run(_nodes(calls))
    assert calls == {"transform": 1}
    assert engine.diagnostics.cache_corruptions == 1
    assert result["features"]["peak"] == 31.0


def test_interrupted_resume_equals_uninterrupted(tmp_path):
    cache = LocalCache(tmp_path / "cache")
    manifest = tmp_path / "run.json"
    calls: dict[str, int] = {}
    with pytest.raises(ExecutionInterrupted):
        ExecutionEngine(_identity(), cache, manifest).run(_nodes(calls), stop_after="features")
    assert json.loads(manifest.read_text())["status"] == "RUNNING"
    resumed = ExecutionEngine(_identity(), cache, manifest)
    resumed_result = resumed.run(_nodes(calls))
    assert json.loads(manifest.read_text())["status"] == "COMPLETED"
    assert resumed.diagnostics.cache_hits == 2

    fresh = ExecutionEngine(_identity(), LocalCache(tmp_path / "fresh"))
    fresh_result = fresh.run(_nodes({}))
    assert resumed_result["judgment"] == fresh_result["judgment"]


def test_chunk_equivalence_and_bounded_iteration():
    rng = np.random.default_rng(606)
    samples = rng.normal(0, 0.1, (48001, 2)).astype(np.float32)
    first = chunked_peak_rms(samples, 1024)
    second = chunked_peak_rms(samples, 8192)
    direct = (float(np.max(np.abs(samples))), float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))))
    assert first == pytest.approx(direct, abs=1e-12)
    assert second == pytest.approx(direct, abs=1e-12)


def test_feature_bus_is_immutable_and_observable():
    bus = FeatureBus()
    values = np.zeros((8, 2), dtype=np.float32)
    bus.publish("decoded_audio", values, "decode", "v1")
    assert bus.get("decoded_audio") is values
    assert bus.bytes_estimate == values.nbytes
    with pytest.raises(ValueError):
        bus.publish("decoded_audio", values, "decode", "v1")
    bus.release("decoded_audio")
    assert bus.bytes_estimate == 0


def test_planner_boundaries():
    measure = build_plan(ExecutionMode.MEASURE_ONLY)
    report = build_plan(ExecutionMode.AUDITORY_REPORT)
    assert measure == ("source_identity", "decoded_audio", "global_measurements")
    assert set(measure).issubset(report)
    assert "recommendation" not in report
    assert "mastering" not in report
