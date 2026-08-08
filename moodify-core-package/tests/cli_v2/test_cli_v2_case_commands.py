"""DSK-MFY-RUNTIME-INTEGRATION-001 — formal CLI v2 production-case commands."""
from __future__ import annotations

import hashlib
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
        cwd=PACKAGE_ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", timeout=120, check=False)


def payload(result: subprocess.CompletedProcess[str], *, error: bool = False) -> dict:
    stream = result.stderr if error else result.stdout
    return json.loads(stream)


def make_wav(path: Path) -> None:
    sr = 44_100
    t = np.arange(sr // 2) / sr
    sf.write(str(path), 0.3 * np.sin(2 * np.pi * 440 * t), sr, subtype="PCM_16")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SPEC = {"essence": "warm vocal", "must_preserve": ["vocal intimacy"],
        "must_avoid": ["harsh highs"], "desired_change": "gentle normalization"}


def bootstrap(tmp_path: Path) -> tuple[Path, Path, str]:
    project = tmp_path / "project"
    source = tmp_path / "source.wav"
    make_wav(source)
    assert run_cli("project", "init", str(project)).returncode == 0
    assert run_cli("asset", "import", str(project), str(source)).returncode == 0
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(SPEC), encoding="utf-8")
    result = run_cli("case", "create", str(project), "--spec", str(spec_file), "--owner", "tester")
    assert result.returncode == 0, result.stderr
    return project, source, payload(result)["case_id"]


def prepared(project: Path, case_id: str, source: Path | None = None) -> None:
    """Drive the case to APPROVED via the CLI."""
    assert run_cli("case", "analyze", str(project), case_id).returncode == 0
    assert run_cli("case", "approve", str(project), case_id, "--owner", "tester").returncode == 0


# ---------------------------------------------------------------- CLI tests

def test_case_execute_rejects_raw_wav(tmp_path: Path):
    project, source, _ = bootstrap(tmp_path)
    result = run_cli("case", "execute", str(project), str(source))
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "RAW_AUDIO_NOT_ACCEPTED"


def test_case_execute_without_approval_rejected_and_state_preserved(tmp_path: Path):
    project, _, case_id = bootstrap(tmp_path)
    result = run_cli("case", "execute", str(project), case_id)
    assert result.returncode != 0
    doc = payload(result, error=True)
    assert doc["ok"] is False
    assert doc["error_code"] == "ARTISTIC_APPROVAL_REQUIRED"
    assert doc["errors"][0]["field"] == "artistic_approval"
    # current case state preserved: still SPECIFIED (never approved)
    status = payload(run_cli("case", "status", str(project), case_id))
    assert status["case"]["state"] == "SPECIFIED"


def test_case_execute_with_stale_plan_hash_rejected(tmp_path: Path):
    project, _, case_id = bootstrap(tmp_path)
    prepared(project, case_id)
    case_file = project / "cases" / case_id / "case.json"
    data = json.loads(case_file.read_text(encoding="utf-8"))
    data["plan"]["steps"] = [{"type": "gain", "params": {"gain_db": 99.0}, "reason": "tampered"}]
    data["plan_hash"] = hashlib.sha256(json.dumps(data["plan"], sort_keys=True).encode()).hexdigest()
    case_file.write_text(json.dumps(data), encoding="utf-8")
    result = run_cli("case", "execute", str(project), case_id)
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "PLAN_HASH_STALE"


def test_case_execute_with_changed_source_rejected(tmp_path: Path):
    project, source, case_id = bootstrap(tmp_path)
    prepared(project, case_id)
    source.write_bytes(source.read_bytes() + b"x")
    result = run_cli("case", "execute", str(project), case_id)
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "SOURCE_CHANGED"


def test_case_execute_success_returns_json_and_reaches_executed(tmp_path: Path):
    project, source, case_id = bootstrap(tmp_path)
    prepared(project, case_id)
    source_hash_before = sha256(source)
    result = run_cli("case", "execute", str(project), case_id)
    assert result.returncode == 0, result.stderr
    doc = payload(result)
    assert doc["status"] == "executed"
    assert doc["ok"] is True
    assert doc["previous_state"] == "APPROVED"
    assert doc["state"] == "EXECUTED"
    assert doc["execution_id"].startswith("MFY-EXEC-")
    assert Path(doc["output_path"]).is_file()
    assert sha256(source) == source_hash_before
    status = payload(run_cli("case", "status", str(project), case_id))
    assert status["case"]["state"] == "EXECUTED"
    assert status["case"]["execution_record"]["plan_hash"] == status["case"]["plan_hash"]


def test_case_execute_unknown_case_fails_with_stable_code(tmp_path: Path):
    project, _, _ = bootstrap(tmp_path)
    result = run_cli("case", "execute", str(project), "MFY-CASE-NOPE")
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "CASE_NOT_FOUND"


def test_case_verify_and_package_golden_path(tmp_path: Path):
    project, _, case_id = bootstrap(tmp_path)
    prepared(project, case_id)
    assert payload(run_cli("case", "execute", str(project), case_id))["state"] == "EXECUTED"
    verified = run_cli("case", "verify", str(project), case_id)
    assert verified.returncode == 0, verified.stderr
    assert payload(verified)["verification_status"] == "PASS"
    assert payload(verified)["state"] == "VERIFIED"
    packaged = run_cli("case", "package", str(project), case_id)
    assert packaged.returncode == 0, packaged.stderr
    assert payload(packaged)["state"] == "COMPLETED"
    evidence = project / "cases" / case_id / "evidence"
    assert (evidence / "evidence_manifest.json").is_file()
    assert (evidence / "output" / "processed_audio.wav").is_file()


def test_case_package_before_verify_fails(tmp_path: Path):
    project, _, case_id = bootstrap(tmp_path)
    prepared(project, case_id)
    assert payload(run_cli("case", "execute", str(project), case_id))["state"] == "EXECUTED"
    result = run_cli("case", "package", str(project), case_id)
    assert result.returncode != 0
    assert payload(result, error=True)["error_code"] == "VERIFICATION_REQUIRED"


# ---------------------------------------------------------------- legacy CLI

def test_legacy_run_requires_allow_uncontrolled_flag(tmp_path: Path):
    project, _, _ = bootstrap(tmp_path)
    plan = payload(run_cli("plan", "create", str(project), "--intent", '{"gain_db":-1.0}'))["plan"]
    result = run_cli("run", "execute", str(project), "--plan-id", plan["plan_id"],
                     "--output-dir", str(tmp_path / "out"))
    assert result.returncode != 0
    assert payload(result, error=True)["errors"][0]["code"] == "CONTROL_REQUIRED"


def test_legacy_daw_render_classified_uncontrolled(tmp_path: Path):
    project, _, _ = bootstrap(tmp_path)
    plan = payload(run_cli("plan", "create", str(project), "--intent", '{"gain_db":-1.0}'))["plan"]
    result = run_cli("run", "execute", str(project), "--plan-id", plan["plan_id"],
                     "--output-dir", str(tmp_path / "out"), "--allow-uncontrolled")
    assert result.returncode == 0, result.stderr
    doc = payload(result)
    assert doc["production_controlled"] is False
    assert doc["classification"] == "UNCONTROLLED_TOOL_EXECUTION"
    assert doc["formal_moodify_asset"] is False
    # no formal evidence package, no completed case was created
    cases_dir = project / "cases"
    assert not list(cases_dir.glob("*/evidence/evidence_manifest.json"))
    for case_dir in cases_dir.iterdir():
        state = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))["state"]
        assert state != "COMPLETED"
