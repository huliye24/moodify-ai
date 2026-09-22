import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from moodify import release_cli
from moodify.sound_protocol import PROTOCOL, ProtocolError, execute_job, validate_job


def job(tmp_path: Path):
    source = tmp_path / "source.wav"
    source.write_bytes(b"test input")
    return {"protocol": PROTOCOL, "source": "source.wav", "preset": "clean_master",
            "output_dir": "out"}


def test_validation_resolves_paths_and_rejects_unknown_fields(tmp_path):
    data = job(tmp_path)
    valid = validate_job(data, tmp_path)
    assert valid["source"] == str(tmp_path / "source.wav")
    assert valid["expected_output"] == str(tmp_path / "out" / "source_clean_master.wav")
    with pytest.raises(ProtocolError, match="exactly"):
        validate_job({**data, "command": "rm"}, tmp_path)
    with pytest.raises(ProtocolError, match="unknown preset"):
        validate_job({**data, "preset": "auto"}, tmp_path)


def test_refuses_overwrite(tmp_path):
    data = job(tmp_path)
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "source_clean_master.wav").write_bytes(b"original")
    with pytest.raises(ProtocolError, match="overwrite"):
        validate_job(data, tmp_path)


def test_cli_validate_machine_readable(tmp_path, capsys):
    path = tmp_path / "job.json"
    path.write_text(json.dumps(job(tmp_path)), encoding="utf-8")
    assert release_cli.main(["protocol", "validate", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "valid"


def test_execute_calls_existing_core_and_emits_evidence(tmp_path, monkeypatch):
    data = validate_job(job(tmp_path), tmp_path)
    output = Path(data["expected_output"])

    def fake_process(source, preset, output_dir):
        assert source == data["source"]
        assert preset == "clean_master"
        assert output_dir == data["output_dir"]
        output.parent.mkdir()
        output.write_bytes(b"audio output")
        return SimpleNamespace(success=True, output_path=str(output),
                               diagnosis=SimpleNamespace(to_dict=lambda: {"issues": []}))

    monkeypatch.setattr("moodify.v01_pipeline.process_audio", fake_process)
    result = execute_job(data)
    assert result["status"] == "processed_review_required"
    assert result["review_required"] is True
    assert len(result["output_sha256"]) == 64
    assert result["core_parameters"]["P06_compression_ratio"] == 1.20


def test_cli_process_real_audio(tmp_path, capsys):
    import numpy as np
    import soundfile as sf

    sample_rate = 22050
    samples = np.sin(2 * np.pi * 440 * np.arange(sample_rate) / sample_rate).astype("float32") * 0.1
    sf.write(tmp_path / "source.wav", samples, sample_rate)
    path = tmp_path / "job.json"
    path.write_text(json.dumps({"protocol": PROTOCOL, "source": "source.wav",
                                "preset": "clean_master", "output_dir": "out"}), encoding="utf-8")
    assert release_cli.main(["protocol", "process", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert Path(result["output"]).is_file()
    assert result["review_required"] is True
