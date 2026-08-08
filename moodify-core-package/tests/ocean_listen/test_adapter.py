"""Ocean sensor adapter tests: source identity, idempotency, evidence registry."""
from __future__ import annotations

import json
import wave
from pathlib import Path
from unittest.mock import patch

import pytest

from moodify.adapters.auditory.ocean_listen.adapter import (
    SourceHashMismatch,
    run_sensor,
)
from moodify.adapters.auditory.ocean_listen.config import OceanRunOptions


def _write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _config(tmp_path: Path) -> dict:
    return {
        "enabled": True,
        "ocean_root": str(tmp_path / "ocean"),
        "output_root": str(tmp_path / "out"),
        "cache_root": str(tmp_path / "cache"),
        "analysis_profile": "shallow",
        "mode": "auto",
        "lyrics_mode": "disabled",
        "timeout_seconds": 30,
        "allow_unreviewed_commit": False,
    }


def test_source_hash_mismatch_rejected(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    case_root = tmp_path / "cases" / "CASE-1"
    case_root.mkdir(parents=True)
    with pytest.raises(SourceHashMismatch, match="hash mismatch"):
        run_sensor(
            case_id="CASE-1",
            case_root=case_root,
            source_path=audio,
            source_sha256="0" * 64,
            config=_config(tmp_path),
            fake=True,
        )


def test_fake_run_registers_evidence_and_is_idempotent(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    case_root = tmp_path / "cases" / "CASE-1"
    case_root.mkdir(parents=True)
    config = _config(tmp_path)

    first = run_sensor(
        case_id="CASE-1", case_root=case_root, source_path=audio,
        source_sha256=_sha256(audio), config=config, fake=True,
    )
    assert first.gate_status == "PASS"
    assert first.observation is not None
    registry = json.loads(first.registry_path.read_text(encoding="utf-8"))
    assert registry["schema"] == "moodify.evidence-registry/1.0"
    assert len(registry["artifacts"]) == 6
    assert all(a["artifact_sha256"] for a in registry["artifacts"])
    assert all(a["producer"].startswith("ocean-listen@") for a in registry["artifacts"])
    assert (first.run_dir / "raw" / "ocean_report.json").is_file()
    assert (first.run_dir / "logs" / "stdout.log").is_file()

    second = run_sensor(
        case_id="CASE-1", case_root=case_root, source_path=audio,
        source_sha256=_sha256(audio), config=config, fake=True,
    )
    assert second.run_id == first.run_id
    assert second.gate_status == "PASS"


def test_config_change_produces_different_run_id(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    case_root = tmp_path / "cases" / "CASE-1"
    case_root.mkdir(parents=True)
    sha = _sha256(audio)

    base = _config(tmp_path)
    first = run_sensor(case_id="CASE-1", case_root=case_root, source_path=audio,
                       source_sha256=sha, config=base, fake=True)
    changed = dict(base)
    changed["analysis_profile"] = "deep"
    second = run_sensor(case_id="CASE-1", case_root=case_root, source_path=audio,
                        source_sha256=sha, config=changed, fake=True)
    assert second.run_id != first.run_id


def test_unreviewed_commit_forces_pin(tmp_path: Path) -> None:
    config = dict(_config(tmp_path))
    config["upstream_commit"] = "deadbeef"
    config["allow_unreviewed_commit"] = False
    from moodify.adapters.auditory.ocean_listen.adapter import _resolve_options
    from moodify.adapters.auditory.ocean_listen.config import PINNED_OCEAN_COMMIT

    options = _resolve_options(config, tmp_path, "CASE-1")
    assert options.expected_commit == PINNED_OCEAN_COMMIT

    config["allow_unreviewed_commit"] = True
    options = _resolve_options(config, tmp_path, "CASE-1")
    assert options.expected_commit == "deadbeef"


def test_windows_paths_work(tmp_path: Path) -> None:
    audio = tmp_path / "song with spaces.wav"
    _write_wav(audio)
    case_root = tmp_path / "case with spaces" / "CASE-1"
    case_root.mkdir(parents=True)
    result = run_sensor(
        case_id="CASE-1", case_root=case_root, source_path=audio,
        source_sha256=_sha256(audio), config=_config(tmp_path), fake=True,
    )
    assert result.gate_status == "PASS"
    assert " " in str(result.registry_path)


def test_gate_fail_keeps_evidence_but_no_observation(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    case_root = tmp_path / "cases" / "CASE-1"
    case_root.mkdir(parents=True)
    fake_result = {
        "quality_gate": {"verdict": "FAIL", "warnings": [], "errors": ["OCEAN_NON_FINITE_NUMBER"]},
        "observation": None,
    }
    with (
        patch("moodify.adapters.auditory.ocean_listen.adapter.OceanRunner") as runner_cls,
        patch(
            "moodify.adapters.auditory.ocean_listen.adapter._artifact_path",
            return_value=tmp_path / "placeholder.json",
        ),
    ):
        runner_cls.return_value.run.return_value = fake_result
        (tmp_path / "placeholder.json").write_text("{}", encoding="utf-8")
        result = run_sensor(
            case_id="CASE-1", case_root=case_root, source_path=audio,
            source_sha256=_sha256(audio), config=_config(tmp_path), fake=False,
        )
    assert result.gate_status == "FAIL"
    assert result.observation is None
    assert result.registry_path.is_file()
    registry = json.loads(result.registry_path.read_text(encoding="utf-8"))
    assert registry["gate"]["status"] == "FAIL"


def test_runner_timeout_raises_and_keeps_logs(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    fake_root = tmp_path / "fake_ocean"
    fake_root.mkdir()
    (fake_root / "ocean.py").write_text("", encoding="utf-8")
    (fake_root / "LICENSE").write_text("MIT", encoding="utf-8")
    (fake_root / "NOTICES").write_text("n", encoding="utf-8")

    from moodify.adapters.auditory.ocean_listen.errors import OceanExecutionError
    from moodify.adapters.auditory.ocean_listen.runner import OceanRunner

    options = OceanRunOptions(
        ocean_root=fake_root,
        output_root=tmp_path / "out",
        expected_commit=None,
        timeout_seconds=1,
    )
    with patch("subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("x", 1)):
        with pytest.raises(OceanExecutionError, match="timed out"):
            OceanRunner(options).run(audio)


def test_runner_nonzero_exit_writes_failure_manifest(tmp_path: Path) -> None:
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    fake_root = tmp_path / "fake_ocean"
    fake_root.mkdir()
    (fake_root / "ocean.py").write_text("", encoding="utf-8")
    (fake_root / "LICENSE").write_text("MIT", encoding="utf-8")
    (fake_root / "NOTICES").write_text("n", encoding="utf-8")

    from moodify.adapters.auditory.ocean_listen.errors import OceanExecutionError
    from moodify.adapters.auditory.ocean_listen.runner import OceanRunner

    options = OceanRunOptions(
        ocean_root=fake_root,
        output_root=tmp_path / "out",
        expected_commit=None,
        timeout_seconds=5,
    )
    with patch("subprocess.run", return_value=__import__("subprocess").CompletedProcess([], 3, stdout="o", stderr="boom")):
        with pytest.raises(OceanExecutionError, match="exit code 3"):
            OceanRunner(options).run(audio)
    manifests = list((tmp_path / "out").rglob("run_manifest.json"))
    assert manifests
    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert payload["status"] == "OCEAN_EXECUTION_FAILED"
