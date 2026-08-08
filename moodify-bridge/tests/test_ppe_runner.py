"""Automated tests for the unified PPE runner, manifest artifacts, and determinism."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify_bridge.schemas import PPEFinalStatus
from moodify_bridge.services import (
    _collect_environment,
    determine_final_status,
    ppe_run,
    write_ppe_artifacts,
)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ppe_run_success_generates_nine_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    out = tmp_path / "run"
    manifest = ppe_run(project / "demo/case.yaml", out)
    write_ppe_artifacts(manifest, out)

    expected = [
        "run_manifest.json", "environment.json", "command_results.jsonl",
        "gate_results.json", "evidence.yaml",
        "ledger/ledger.duckdb",
        "reports/case.md", "reports/case.html",
        "FINAL_STATUS.txt",
    ]
    for rel in expected:
        assert (out / rel).exists(), f"Missing artifact: {rel}"

    assert manifest.final_status == PPEFinalStatus.PASS_WITH_WARNINGS


def test_ppe_run_status_is_pass_with_warnings_for_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    out = tmp_path / "run"
    manifest = ppe_run(project / "demo/case.yaml", out)
    assert manifest.final_status == PPEFinalStatus.PASS_WITH_WARNINGS


def test_manifest_references_exist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    out = tmp_path / "run"
    manifest = ppe_run(project / "demo/case.yaml", out)
    write_ppe_artifacts(manifest, out)

    if manifest.evidence_path:
        assert Path(manifest.evidence_path).exists()
    if manifest.report_md_path:
        assert Path(manifest.report_md_path).exists()
    if manifest.report_html_path:
        assert Path(manifest.report_html_path).exists()


def test_final_status_is_fail_for_nonexistent_case(tmp_path: Path) -> None:
    out = tmp_path / "run"
    manifest = ppe_run(Path("nonexistent_case.yaml"), out)
    assert manifest.final_status == PPEFinalStatus.FAIL
    assert len(manifest.gates) == 0
    cmds = list(manifest.commands)
    assert cmds[0].status.value == "FAIL"


def test_determine_final_status_empty_gates_fail() -> None:
    assert determine_final_status([]) == PPEFinalStatus.FAIL


def test_environment_collects_pyyaml_correctly() -> None:
    env = _collect_environment()
    assert env.packages["PyYAML"] != "absent"
    assert "6" in env.packages["PyYAML"]


def test_manifest_contains_verified_artifact_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The persisted manifest must identify every material referenced artifact."""
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)

    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"
    ma = write_ppe_artifacts(ppe_run(project / "demo/case.yaml", out_a), out_a)
    mb = write_ppe_artifacts(ppe_run(project / "demo/case.yaml", out_b), out_b)

    from moodify_bridge.hashing import sha256_file

    expected = {
        "environment.json", "command_results.jsonl", "gate_results.json",
        "FINAL_STATUS.txt", "evidence.yaml", "ledger/ledger.duckdb",
        "reports/case.md", "reports/case.html",
    }
    assert set(ma.artifact_hashes) == expected
    for rel, digest in ma.artifact_hashes.items():
        assert sha256_file(out_a / rel) == digest

    persisted = json.loads((out_a / "run_manifest.json").read_text(encoding="utf-8"))
    assert persisted["artifact_hashes"] == ma.artifact_hashes

    # Gate results should be identical (same JSON structure)
    ga = json.loads((out_a / "gate_results.json").read_text(encoding="utf-8"))
    gb = json.loads((out_b / "gate_results.json").read_text(encoding="utf-8"))
    for i in range(len(ga)):
        assert ga[i]["gate_id"] == gb[i]["gate_id"]
        assert ga[i]["status"] == gb[i]["status"]
        assert ga[i]["reason_code"] == gb[i]["reason_code"]

    # Evidence YAML should match (case digest, measurement IDs)
    import yaml
    ea = yaml.safe_load((out_a / "evidence.yaml").read_text(encoding="utf-8"))
    eb = yaml.safe_load((out_b / "evidence.yaml").read_text(encoding="utf-8"))
    assert ea["case_digest"] == eb["case_digest"]
    assert ea["measurement_ids"] == eb["measurement_ids"]

    # Final status must match
    assert (out_a / "FINAL_STATUS.txt").read_text() == (out_b / "FINAL_STATUS.txt").read_text()
    # Deterministic artifacts have matching identities. DuckDB includes generated
    # timestamps/UUIDs and is deliberately not claimed byte-identical.
    volatile = {
        "ledger/ledger.duckdb", "environment.json", "command_results.jsonl",
        "gate_results.json", "evidence.yaml",
    }
    for rel in expected - volatile:
        assert ma.artifact_hashes[rel] == mb.artifact_hashes[rel]


def test_command_results_no_duplicate_pass_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each action in command_results should appear exactly once."""
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    out = tmp_path / "run"
    manifest = ppe_run(project / "demo/case.yaml", out)
    write_ppe_artifacts(manifest, out)

    entries = _read_jsonl(out / "command_results.jsonl")
    actions = [e["action"] for e in entries]
    assert len(actions) == len(set(actions)), f"Duplicate actions found: {actions}"
    # Each action should have exactly one entry
    from collections import Counter
    counts = Counter(actions)
    for action, count in counts.items():
        assert count == 1, f"Action '{action}' appears {count} times"


def test_no_measurement_no_candidate_gates_are_warn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Synthetic demo has no measurements, no candidates, no approval — all WARN, not PASS."""
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    out = tmp_path / "run"
    manifest = ppe_run(project / "demo/case.yaml", out)

    gate_map = {g.gate_id: g for g in manifest.gates}
    assert gate_map["measurement_available"].status.value == "WARN"
    assert gate_map["candidates_comparable"].status.value == "WARN"
    assert gate_map["human_approved"].status.value == "WARN"
    assert gate_map["measurement_available"].reason_code == "no_measurements_recorded"
    assert gate_map["human_approved"].reason_code == "not_applicable"
