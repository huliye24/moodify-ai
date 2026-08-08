from pathlib import Path
import json
import wave

from moodify.adapters.auditory.ocean_listen.mapper import map_report_file


def _write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


def test_mapping_preserves_sensor_boundary(tmp_path: Path):
    audio = tmp_path / "sample.wav"
    _write_wav(audio)
    fixture = Path(__file__).parent / "fixtures" / "ocean_report_minimal.json"
    output = tmp_path / "observation.json"

    result = map_report_file(
        fixture,
        source_audio=audio,
        run_id="run-1",
        upstream_commit="fixture-commit",
        output_path=output,
        deep_expected=True,
    )

    assert output.is_file()
    assert result["schema_version"] == "moodify.auditory-observation/1.0"
    assert result["classification"]["authority"] == "sensor_only"
    assert result["quality_gate"]["verdict"] == "PASS"
    assert result["notes"][0]["model_confidence_proxy"] > 0
    assert result["notes"][0]["selection_status"] == "candidate"
    assert result["voice"]["status"] == "experimental"
    assert any(
        warning["code"] == "SENSOR_NOT_JUDGMENT"
        for warning in result["uncertainty"]
    )

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["observation_id"] == result["observation_id"]


def test_observation_id_deterministic_for_identical_inputs():
    from moodify.adapters.auditory.ocean_listen.mapper import map_ocean_report

    report = {
        "name": "x",
        "duration": 2.0,
        "notes": [],
        "total_notes": 0,
        "stems": [],
        "timeline": [],
    }
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        handle.write(b"RIFF")
        audio = handle.name
    kwargs = dict(source_audio=audio, run_id="RUN-1", upstream_commit="c",
                  module_manifest={}, raw_report_path="r.json", deep_expected=False)
    first = map_ocean_report(report, **kwargs)
    second = map_ocean_report(report, **kwargs)
    assert first["observation_id"] == second["observation_id"]
    assert len(first["observation_id"]) == 36  # deterministic UUID
