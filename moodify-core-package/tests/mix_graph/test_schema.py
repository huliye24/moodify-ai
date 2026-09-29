"""Schema validation tests for moodify.mix_graph/0.1."""

import pytest

from moodify.mix_graph.schema import MixGraphError, canonical_json, validate_graph

pytestmark = [pytest.mark.v01]


def base_graph(**overrides):
    graph = {
        "schema": "moodify.mix_graph/0.1",
        "source": "audio.wav",
        "nodes": [
            {"id": "lim_1", "type": "limiter", "parameters": {"ceiling_db": -1.0}},
        ],
    }
    graph.update(overrides)
    return graph


def test_minimal_valid_graph_canonicalizes():
    canonical = validate_graph(base_graph())
    assert canonical["schema"] == "moodify.mix_graph/0.1"
    assert canonical["status"] == "EXPERIMENTAL"
    node = canonical["nodes"][0]
    assert node["enabled"] is True
    assert node["parameters"] == {"ceiling_db": -1.0, "input_gain_db": 0.0}


def test_source_relative_and_optional_sections():
    graph = base_graph(
        intent="transparent finishing",
        verification={"max_peak_dbfs": -1.0},
        provenance={"created_by": "test"},
        notes="ok",
    )
    canonical = validate_graph(graph)
    assert canonical["intent"] == "transparent finishing"
    assert canonical["verification"] == {"max_peak_dbfs": -1.0}


def test_unknown_top_level_key_rejected():
    with pytest.raises(MixGraphError, match="unknown keys"):
        validate_graph(base_graph(unexpected=1))


def test_missing_required_key_rejected():
    graph = base_graph()
    del graph["nodes"]
    with pytest.raises(MixGraphError, match="missing required"):
        validate_graph(graph)


def test_wrong_schema_id_rejected():
    with pytest.raises(MixGraphError, match="unsupported schema"):
        validate_graph(base_graph(schema="moodify.mix_graph/0.2"))


def test_empty_nodes_rejected():
    with pytest.raises(MixGraphError, match="1..32"):
        validate_graph(base_graph(nodes=[]))


def test_duplicate_node_ids_rejected():
    node = {"id": "x", "type": "limiter", "parameters": {"ceiling_db": -1.0}}
    with pytest.raises(MixGraphError, match="duplicate node id"):
        validate_graph(base_graph(nodes=[node, node]))


def test_unknown_node_type_rejected():
    node = {"id": "x", "type": "reverb", "parameters": {}}
    with pytest.raises(MixGraphError, match="type must be one of"):
        validate_graph(base_graph(nodes=[node]))


def test_unknown_node_key_rejected():
    node = {"id": "x", "type": "limiter", "parameters": {}, "wet": 1}
    with pytest.raises(MixGraphError, match="unknown keys"):
        validate_graph(base_graph(nodes=[node]))


def test_non_bool_enabled_rejected():
    node = {"id": "x", "type": "limiter", "parameters": {}, "enabled": "yes"}
    with pytest.raises(MixGraphError, match="enabled must be a boolean"):
        validate_graph(base_graph(nodes=[node]))


def test_bad_id_characters_rejected():
    node = {"id": "bad id!", "type": "limiter", "parameters": {}}
    with pytest.raises(MixGraphError, match="id must match"):
        validate_graph(base_graph(nodes=[node]))


def test_verification_out_of_range_rejected():
    with pytest.raises(MixGraphError, match="max_peak_dbfs"):
        validate_graph(base_graph(verification={"max_peak_dbfs": 3.0}))


def test_provider_parameter_error_names_the_node():
    node = {"id": "eq_bad", "type": "eq", "parameters": {"bands": []}}
    with pytest.raises(MixGraphError, match="eq_bad"):
        validate_graph(base_graph(nodes=[node]))


def test_canonical_json_is_deterministic():
    a = canonical_json(validate_graph(base_graph()))
    b = canonical_json(validate_graph(base_graph()))
    assert a == b
    assert a.endswith("\n")
