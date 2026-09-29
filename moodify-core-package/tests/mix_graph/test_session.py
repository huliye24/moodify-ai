"""Session executor tests: rendering, bypass semantics, evidence, guards."""


import numpy as np
import pytest
import soundfile as sf
from pathlib import Path

from moodify.audio_io import load_audio
from moodify.mix_graph import MixGraphError, run_session
from moodify.mix_graph.graph import graph_from_dict

pytestmark = [pytest.mark.v01]


def graph_nodes(nodes):
    return nodes


def make_graph(path, nodes, verification=None):
    return graph_from_dict({
        "schema": "moodify.mix_graph/0.1",
        "source": path.name,
        "nodes": nodes,
        **({"verification": verification} if verification else {}),
    }, base_dir=path.parent)


def test_session_renders_and_writes_evidence(stereo_wav, tmp_path):
    src, _ = stereo_wav
    graph = make_graph(src, [
        {"id": "eq_1", "type": "eq", "enabled": True,
         "parameters": {"bands": [{"type": "highshelf", "freq_hz": 10000.0, "gain_db": 3.0}]},
         "reason": "air lift"},
        {"id": "lim_1", "type": "limiter", "enabled": True,
         "parameters": {"ceiling_db": -1.0}},
    ])
    evidence = run_session(graph, tmp_path / "out")

    assert evidence["status"] == "rendered"
    assert evidence["output"]["written"] is True
    assert Path(evidence["output"]["evidence_path"]).is_file()
    assert evidence["graph_digest_sha256"]
    assert evidence["verification"]["invariants"] == {
        "finite_output": True, "length_preserved": True, "channels_preserved": True}
    assert evidence["verification"]["peak_gate"]["passed"] is True
    assert len(evidence["nodes"]) == 2
    assert evidence["nodes"][0]["reason"] == "air lift"
    assert "before" in evidence["nodes"][0] and "after" in evidence["nodes"][0]


def test_all_bypassed_output_is_bitwise_source(stereo_wav, tmp_path):
    src, _ = stereo_wav
    graph = make_graph(src, [
        {"id": "eq_1", "type": "eq", "enabled": False,
         "parameters": {"bands": [{"type": "highshelf", "freq_hz": 10000.0, "gain_db": 6.0}]}},
        {"id": "lim_1", "type": "limiter", "enabled": False,
         "parameters": {"ceiling_db": -1.0}},
    ])
    evidence = run_session(graph, tmp_path / "out")
    assert all(node.get("bypassed") for node in evidence["nodes"])

    source_audio, _ = load_audio(str(src), always_2d=True)
    output_audio, _ = load_audio(evidence["output"]["path"], always_2d=True)
    assert np.array_equal(source_audio, output_audio)


def test_bypassed_limiter_does_not_cap(stereo_wav, tmp_path):
    src, _ = stereo_wav
    loud = tmp_path / "loud.wav"
    audio, sr = load_audio(str(src), always_2d=True)
    sf.write(str(loud), (audio * 3.0).astype(np.float32), sr, subtype="PCM_16")

    graph = make_graph(loud, [
        {"id": "lim_1", "type": "limiter", "enabled": False,
         "parameters": {"ceiling_db": -1.0}}])
    evidence = run_session(graph, tmp_path / "out")
    assert evidence["verification"]["peak_gate"]["passed"] is False


def test_dry_run_writes_nothing(stereo_wav, tmp_path):
    src, _ = stereo_wav
    graph = make_graph(src, [
        {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}}])
    evidence = run_session(graph, tmp_path / "out", dry_run=True)

    assert evidence["status"] == "dry_run"
    assert evidence["output"]["written"] is False
    out_dir = tmp_path / "out"
    assert not out_dir.exists() or list(out_dir.iterdir()) == []  # no wav, no evidence


def test_refuses_to_overwrite_output(stereo_wav, tmp_path):
    src, _ = stereo_wav
    graph = make_graph(src, [
        {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}}])
    run_session(graph, tmp_path / "out")
    with pytest.raises(MixGraphError, match="refusing to overwrite"):
        run_session(graph, tmp_path / "out")


def test_missing_source_raises(tmp_path):
    graph = graph_from_dict({
        "schema": "moodify.mix_graph/0.1",
        "source": "missing.wav",
        "nodes": [{"id": "lim_1", "type": "limiter", "parameters": {}}],
    }, base_dir=tmp_path)
    with pytest.raises(MixGraphError, match="source is not a file"):
        run_session(graph, tmp_path / "out")


def test_mono_source_is_upsampled_and_recorded(mono_wav, tmp_path):
    src, _ = mono_wav
    graph = make_graph(src, [
        {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}}])
    evidence = run_session(graph, tmp_path / "out")
    assert evidence["session"]["mono_upsampled_to_stereo"] is True
    assert evidence["verification"]["invariants"]["channels_preserved"] is True


def test_explicit_verification_limit_wins(stereo_wav, tmp_path):
    src, _ = stereo_wav
    graph = make_graph(src, [
        {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}}],
        verification={"max_peak_dbfs": -20.0})
    evidence = run_session(graph, tmp_path / "out")
    gate = evidence["verification"]["peak_gate"]
    assert gate["limit"] == -20.0
    assert gate["passed"] is False
