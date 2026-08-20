"""Deterministic Case Runner E2E on synthetic fixtures.

MFY_EAR_DETERMINISTIC_CASE_RUNNER_001: idempotency, atomicity, config snapshot,
stable failure codes. Synthetic sine fixture only — never private catalogue.
"""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest

from moodify.data_factory.case_runner import (
    CONFIG_FILE,
    CaseRunner,
    CaseRunnerError,
    FAILURE_EXECUTION_FAILED,
    FAILURE_INVALID_INPUT,
)


@pytest.fixture()
def sine_wav(tmp_path: Path) -> Path:
    path = tmp_path / "sine_440.wav"
    rate, seconds = 22050, 1.5
    samples = (0.25 * np.sin(2 * np.pi * 440 * np.arange(int(rate * seconds)) / rate)).astype(np.float32)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((samples * 32767).astype(np.int16).tobytes())
    return path


@pytest.fixture()
def runner(tmp_path: Path) -> CaseRunner:
    return CaseRunner(tmp_path / "output")


def test_case_completes_with_config_snapshot(runner: CaseRunner, sine_wav: Path):
    case_dir = runner.submit(sine_wav, idempotency_key="case-e2e-001")
    assert case_dir.is_dir()
    config = json.loads((case_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    assert config["idempotency_key"] == "case-e2e-001"
    assert config["scan_profile_id"] == "MFY-WSE-SCAN-PROFILE-001"
    assert len(config["source_sha256"]) == 64
    # production case marked completed
    case = json.loads((case_dir / "production_case.json").read_text(encoding="utf-8"))
    assert case["lifecycle_state"] == "COMPLETED"
    assert case["authority_state"] == "ALGORITHM"


def test_idempotent_resubmission_returns_same_case(runner: CaseRunner, sine_wav: Path):
    first = runner.submit(sine_wav, idempotency_key="case-e2e-002")
    second = runner.submit(sine_wav, idempotency_key="case-e2e-002")
    assert first == second
    # exactly one case produced for this key
    cases = list((runner.output_root / "cases").glob("case_*"))
    assert len(cases) == 1


def test_invalid_input_failure_code(runner: CaseRunner, tmp_path: Path):
    missing = tmp_path / "nope.wav"
    with pytest.raises(CaseRunnerError) as exc:
        runner.submit(missing, idempotency_key="case-e2e-003")
    assert exc.value.code == FAILURE_INVALID_INPUT


def test_failed_execution_leaves_no_partial_case(runner: CaseRunner, tmp_path: Path):
    bad = tmp_path / "empty.wav"
    bad.write_bytes(b"RIFFxxxx")  # truncated container
    with pytest.raises(CaseRunnerError) as exc:
        runner.submit(bad, idempotency_key="case-e2e-004")
    assert exc.value.code == FAILURE_EXECUTION_FAILED
    # temp dir cleaned; no case dir produced
    cases = list((runner.output_root / "cases").glob("case_*"))
    assert cases == []
    tmp = list((runner.output_root / "cases" / ".tmp").glob("*")) if (runner.output_root / "cases" / ".tmp").exists() else []
    assert tmp == []
