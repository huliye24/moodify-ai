"""case analyze --sensor ocean --fake end-to-end (no upstream, no models)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import wave
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGE_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "moodify", *args],
        cwd=PACKAGE_ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", timeout=120, check=False,
    )


def payload(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def make_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


def bootstrap(tmp_path: Path) -> tuple[Path, str]:
    project = tmp_path / "project"
    source = tmp_path / "source.wav"
    make_wav(source)
    assert run_cli("project", "init", str(project)).returncode == 0
    imported = payload(run_cli("asset", "import", str(project), str(source)))
    asset_id = imported["asset"]["asset_id"]
    created = payload(run_cli("case", "create", str(project), "--spec",
                              '{"essence": "x", "must_preserve": ["a"], "must_avoid": ["b"], "desired_change": "c"}',
                              "--owner", "tester", "--asset-id", asset_id))
    return project, created["case_id"]


def test_analyze_with_fake_sensor_reaches_technical_gate(tmp_path: Path) -> None:
    project, case_id = bootstrap(tmp_path)
    result = run_cli("case", "analyze", str(project), case_id,
                     "--sensor", "ocean", "--fake")
    assert result.returncode == 0, result.stderr
    body = payload(result)
    assert body["status"] == "planned"
    assert body["state"] == "TECHNICALLY_VALIDATED"

    case_root = project / "cases" / case_id
    registry = case_root / "06_ocean_listen" / "evidence_registry.json"
    assert registry.is_file()
    data = json.loads(registry.read_text(encoding="utf-8"))
    assert data["gate"]["status"] == "PASS"
    assert len(data["artifacts"]) == 6

    case_json = json.loads((case_root / "case.json").read_text(encoding="utf-8"))
    assert case_json["analysis"].get("sensor") == "ocean"
    assert "auditory_observation" in case_json["analysis"]
    assert case_json["analysis"]["sensor_gate"] == "PASS"


def test_analyze_without_sensor_has_no_ocean_evidence(tmp_path: Path) -> None:
    project, case_id = bootstrap(tmp_path)
    result = run_cli("case", "analyze", str(project), case_id)
    assert result.returncode == 0, result.stderr
    assert payload(result)["state"] == "TECHNICALLY_VALIDATED"
    registry = project / "cases" / case_id / "06_ocean_listen" / "evidence_registry.json"
    assert not registry.exists()
