from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGE_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "moodify", *args],
        cwd=PACKAGE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def payload(result: subprocess.CompletedProcess[str], *, error: bool = False) -> dict:
    stream = result.stderr if error else result.stdout
    return json.loads(stream)


def make_wav(path: Path) -> None:
    sr = 44_100
    t = np.arange(sr // 10) / sr
    sf.write(path, 0.05 * np.sin(2 * np.pi * 440 * t), sr, subtype="PCM_16")


def bootstrap(tmp_path: Path, *, dry_run: bool = False) -> tuple[Path, Path, str]:
    project = tmp_path / "项目 with space"
    source = tmp_path / "音频 source.wav"
    make_wav(source)
    assert run_cli("project", "init", str(project)).returncode == 0
    assert run_cli("asset", "import", str(project), str(source)).returncode == 0
    args = ["plan", "create", str(project), "--intent", '{"gain_db":-1.0}']
    if dry_run:
        args.append("--dry-run")
    result = run_cli(*args)
    assert result.returncode == 0
    return project, source, payload(result)["plan"]["plan_id"]


def test_official_entrypoint_returns_one_json_document():
    result = run_cli("version")
    assert result.returncode == 0
    assert result.stderr == ""
    assert payload(result)["status"] == "ok"


def test_project_asset_and_plan_are_persisted(tmp_path: Path):
    project, _, plan_id = bootstrap(tmp_path)
    data = json.loads((project / "project.json").read_text(encoding="utf-8"))
    assert len(data["assets"]) == 1
    assert data["plans"][0]["plan_id"] == plan_id


def test_asset_import_is_idempotent(tmp_path: Path):
    project, source, _ = bootstrap(tmp_path)
    result = run_cli("asset", "import", str(project), str(source))
    assert result.returncode == 0
    assert payload(result)["status"] == "unchanged"
    data = json.loads((project / "project.json").read_text(encoding="utf-8"))
    assert len(data["assets"]) == 1


def test_dry_run_plan_cannot_execute_and_creates_no_output(tmp_path: Path):
    project, _, plan_id = bootstrap(tmp_path, dry_run=True)
    output = tmp_path / "should-not-exist"
    result = run_cli("run", "execute", str(project), "--plan-id", plan_id, "--output-dir", str(output), "--allow-uncontrolled")
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "DRY_RUN_PLAN"
    assert not output.exists()


def test_execute_and_verify_closed_loop(tmp_path: Path):
    project, source, plan_id = bootstrap(tmp_path)
    source_hash_before = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
    output = tmp_path / "render output"
    executed = run_cli("run", "execute", str(project), "--plan-id", plan_id, "--output-dir", str(output), "--allow-uncontrolled")
    assert executed.returncode == 0, executed.stderr
    executed_json = payload(executed)
    assert (output / "render.wav").is_file()
    verified = run_cli("run", "verify", str(project), "--run-id", executed_json["run_id"], "--allow-uncontrolled")
    assert verified.returncode == 0, verified.stderr
    assert payload(verified)["status"] == "verified"
    assert __import__("hashlib").sha256(source.read_bytes()).hexdigest() == source_hash_before


def test_source_hash_change_fails_closed(tmp_path: Path):
    project, source, plan_id = bootstrap(tmp_path)
    source.write_bytes(source.read_bytes() + b"changed")
    output = tmp_path / "must-not-render"
    result = run_cli("run", "execute", str(project), "--plan-id", plan_id, "--output-dir", str(output), "--allow-uncontrolled")
    assert result.returncode == 4
    assert payload(result, error=True)["errors"][0]["code"] == "SOURCE_HASH_MISMATCH"
    assert not output.exists()


def test_invalid_intent_and_unsafe_gain_fail_closed(tmp_path: Path):
    project, _, _ = bootstrap(tmp_path)
    invalid = run_cli("plan", "create", str(project), "--intent", "[]")
    assert invalid.returncode != 0
    assert payload(invalid, error=True)["errors"][0]["code"] == "INTENT_INVALID"
    unsafe = run_cli("plan", "create", str(project), "--intent", '{"gain_db":99}')
    assert unsafe.returncode != 0
    assert payload(unsafe, error=True)["errors"][0]["code"] == "PLAN_UNSAFE"


def test_existing_output_is_never_overwritten(tmp_path: Path):
    project, _, plan_id = bootstrap(tmp_path)
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("user data", encoding="utf-8")
    result = run_cli("run", "execute", str(project), "--plan-id", plan_id, "--output-dir", str(output), "--allow-uncontrolled")
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "OUTPUT_EXISTS"
    assert marker.read_text(encoding="utf-8") == "user data"


def test_verify_rejects_tampered_output(tmp_path: Path):
    project, _, plan_id = bootstrap(tmp_path)
    output = tmp_path / "tamper-check"
    executed = run_cli("run", "execute", str(project), "--plan-id", plan_id, "--output-dir", str(output), "--allow-uncontrolled")
    assert executed.returncode == 0
    run_id = payload(executed)["run_id"]
    (output / "render.wav").write_bytes((output / "render.wav").read_bytes() + b"tampered")
    verified = run_cli("run", "verify", str(project), "--run-id", run_id, "--allow-uncontrolled")
    assert verified.returncode == 5
    assert payload(verified, error=True)["errors"][0]["code"] == "VERIFICATION_FAILED"
