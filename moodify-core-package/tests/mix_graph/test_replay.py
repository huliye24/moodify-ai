"""Deterministic replay tests: same core + same graph + same input -> same output."""

import hashlib
import json
from pathlib import Path

import pytest

from moodify.mix_graph import run_session
from moodify.mix_graph.graph import load_graph, save_graph
from moodify.mix_graph.schema import canonical_json

pytestmark = [pytest.mark.v01]


def _file_sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _render_to(tmp_path, src, tag):
    out_dir = tmp_path / tag
    graph_file = tmp_path / f"graph_{tag}.json"
    graph_file.write_text(json.dumps({
        "schema": "moodify.mix_graph/0.1",
        "source": str(src),
        "nodes": [
            {"id": "eq_1", "type": "eq",
             "parameters": {"bands": [{"type": "highshelf", "freq_hz": 10000.0, "gain_db": 3.0}]}},
            {"id": "comp_1", "type": "compressor",
             "parameters": {"threshold_db": -14.0, "ratio": 1.5,
                            "attack_ms": 20.0, "release_ms": 200.0}},
            {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    evidence = run_session(load_graph(graph_file), out_dir)
    return evidence


def test_two_renders_are_bit_identical(stereo_wav, tmp_path):
    src, _ = stereo_wav
    first = _render_to(tmp_path, src, "a")
    second = _render_to(tmp_path, src, "b")

    assert first["graph_digest_sha256"] == second["graph_digest_sha256"]
    assert first["output"]["sha256"] == second["output"]["sha256"]
    a = Path(first["output"]["path"]).read_bytes()
    b = Path(second["output"]["path"]).read_bytes()
    assert a == b

    def measured(evidence):
        payload = dict(evidence["verification"])
        return canonical_json(payload)

    assert measured(first) == measured(second)


def test_graph_round_trip_preserves_digest(stereo_wav, tmp_path):
    src, _ = stereo_wav
    _render_to(tmp_path, src, "rt1")
    # Re-save through the model layer and reload: digest must not drift.
    graph = load_graph(tmp_path / "graph_rt1.json")
    resaved = save_graph(graph, tmp_path / "resaved.json")
    assert load_graph(resaved).digest() == graph.digest()


def test_provenance_does_not_change_digest(stereo_wav, tmp_path):
    src, _ = stereo_wav
    a = _render_to(tmp_path, src, "prov1")
    graph_file = tmp_path / "graph_prov2.json"
    graph_file.write_text(json.dumps({
        "schema": "moodify.mix_graph/0.1",
        "source": str(src),
        "intent": "different intent",
        "provenance": {"created_by": "someone else"},
        "notes": "different notes",
        "nodes": [
            {"id": "eq_1", "type": "eq",
             "parameters": {"bands": [{"type": "highshelf", "freq_hz": 10000.0, "gain_db": 3.0}]}},
            {"id": "comp_1", "type": "compressor",
             "parameters": {"threshold_db": -14.0, "ratio": 1.5,
                            "attack_ms": 20.0, "release_ms": 200.0}},
            {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    b = run_session(load_graph(graph_file), tmp_path / "prov2")
    assert a["graph_digest_sha256"] == b["graph_digest_sha256"]
    assert a["output"]["sha256"] == b["output"]["sha256"]
