from pathlib import Path
import json
import wave

from moodify.adapters.auditory.ocean_listen.config import OceanRunOptions
from moodify.adapters.auditory.ocean_listen.runner import OceanRunner


def _write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


def test_fake_process_end_to_end(tmp_path: Path):
    audio = tmp_path / "song.wav"
    _write_wav(audio)
    fake_root = Path(__file__).parent / "fake_ocean"

    options = OceanRunOptions(
        ocean_root=fake_root,
        output_root=tmp_path / "out",
        deep=True,
        expected_commit=None,
        timeout_seconds=30,
    )
    result = OceanRunner(options).run(audio)

    assert result["quality_gate"]["verdict"] == "PASS"
    run_dir = Path(result["execution"]["run_dir"])
    assert (run_dir / "raw" / "ocean_report.json").is_file()
    assert (
        run_dir / "normalized" / "auditory_observation.v1.json"
    ).is_file()
    assert (run_dir / "quality" / "gate_result.json").is_file()
    assert (run_dir / "evidence" / "run_manifest.json").is_file()
    manifest = json.loads(
        (run_dir / "evidence" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["authority"]["sensor_output_only"] is True
    assert manifest["authority"]["may_transition_to_technically_validated"] is False
