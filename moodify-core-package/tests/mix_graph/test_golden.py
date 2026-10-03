"""Golden end-to-end case: demo/input/example.mp3 through a clean_master graph.

Reproduce the committed evidence with:
    cd moodify-core-package
    PYTHONPATH=src python -c "from moodify.release_cli import main; \
main(['finishing','new','--preset','clean_master','--source','../demo/input/example.mp3','--out','../artifacts/mix_graph_v01/golden/graph.json']); \
main(['finishing','render','../artifacts/mix_graph_v01/golden/graph.json','--output-dir','../artifacts/mix_graph_v01/golden'])"
"""

from pathlib import Path

import pytest

from moodify.mix_graph import run_session
from moodify.mix_graph.graph import graph_from_preset, load_graph, save_graph

pytestmark = [pytest.mark.v01]

GOLDEN_SOURCE = Path(__file__).resolve().parents[3] / "demo" / "input" / "example.mp3"

pytest.importorskip("librosa", reason="mp3 golden source needs the librosa fallback")


@pytest.mark.skipif(not GOLDEN_SOURCE.is_file(), reason="golden source not present")
def test_golden_clean_master_replay(tmp_path_factory):
    out_root = tmp_path_factory.mktemp("golden")
    graph = graph_from_preset("clean_master", str(GOLDEN_SOURCE))

    evidences = []
    for tag in ("run1", "run2"):
        out_dir = out_root / tag
        graph_file = out_dir / "graph.json"
        save_graph(graph, graph_file)
        evidences.append(run_session(load_graph(graph_file), out_dir))

    first, second = evidences
    # 1. deterministic replay: identical digest, identical bytes
    assert first["graph_digest_sha256"] == second["graph_digest_sha256"]
    assert first["output"]["sha256"] == second["output"]["sha256"]

    # 2. evidence completeness: 3 nodes (eq/comp/limiter), gates passed
    assert [node["type"] for node in first["nodes"]] == ["eq", "compressor", "limiter"]
    invariants = first["verification"]["invariants"]
    assert invariants == {"finite_output": True, "length_preserved": True,
                          "channels_preserved": True}
    assert first["verification"]["peak_gate"]["passed"] is True

    # 3. chain sanity: no runaway gain from the clean_master chain
    loudness_delta = first["verification"]["deltas"]["loudness_lu"]
    assert abs(loudness_delta) <= 6.0
