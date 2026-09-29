"""CLI tests for `moodify finishing new/render/verify/export`."""

import json

import pytest

from moodify.release_cli import main

pytestmark = [pytest.mark.v01]


def test_new_render_verify_export_cycle(stereo_wav, tmp_path, capsys):
    src, _ = stereo_wav
    graph_file = tmp_path / "graph.json"
    out_dir = tmp_path / "out"

    rc = main(["finishing", "new", "--preset", "clean_master",
               "--source", str(src), "--out", str(graph_file)])
    assert rc == 0
    capsys.readouterr()  # discard `new` output before reading `render` output

    rc = main(["finishing", "render", str(graph_file), "--output-dir", str(out_dir)])
    assert rc == 0
    evidence = json.loads(capsys.readouterr().out)
    assert evidence["status"] == "rendered"
    output_path = evidence["output"]["path"]

    rc = main(["finishing", "verify", "--source", str(src),
               "--output", output_path, "--max-peak-dbfs", "-1.0"])
    assert rc == 0
    verify = json.loads(capsys.readouterr().out)
    assert verify["status"] == "measured"
    assert verify["peak_gate"]["passed"] is True

    rc = main(["finishing", "export", "--audio", output_path,
               "--output-dir", str(out_dir)])
    assert rc == 0
    exported = json.loads(capsys.readouterr().out)
    assert exported["output"].endswith("_delivery.wav")


def test_render_error_exits_2(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema": "moodify.mix_graph/0.1", "source": "x.wav",
                               "nodes": []}), encoding="utf-8")
    rc = main(["finishing", "render", str(bad), "--output-dir", str(tmp_path / "out")])
    assert rc == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"


def test_new_prints_graph_without_out(stereo_wav, capsys):
    src, _ = stereo_wav
    rc = main(["finishing", "new", "--preset", "warm_vocal", "--source", str(src)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["graph_digest_sha256"]
    node_types = [node["type"] for node in payload["graph"]["nodes"]]
    assert node_types == ["eq", "compressor", "stereo", "limiter"]
    assert "reverb" in payload["graph"]["notes"]
