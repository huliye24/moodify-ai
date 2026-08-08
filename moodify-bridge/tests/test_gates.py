from __future__ import annotations

import pytest
from pydantic import ValidationError

from moodify_bridge.schemas import GateResult, GateStatus


def test_gate_result_accepts_valid_enum() -> None:
    g = GateResult(
        gate_id="input_complete",
        status=GateStatus.PASS,
        blocking=True,
        reason_code="all_inputs_present",
        message="All required inputs are registered and readable.",
    )
    assert g.status is GateStatus.PASS
    assert g.blocking is True


def test_gate_result_rejects_unknown_gate_id() -> None:
    with pytest.raises(ValidationError, match="String should match pattern"):
        GateResult(
            gate_id="unknown_gate",
            status=GateStatus.PASS,
            blocking=False,
            reason_code="ok",
            message="ok",
        )


def test_gate_result_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs"):
        GateResult(
            gate_id="input_complete",
            status=GateStatus.PASS,
            blocking=True,
            reason_code="ok",
            message="ok",
            unknown_field="intruder",
        )


def test_gate_status_enum_values() -> None:
    assert {s.value for s in GateStatus} == {"PASS", "WARN", "FAIL"}


def test_blocking_fail_aggregation() -> None:
    gates: list[GateResult] = [
        GateResult(
            gate_id="input_complete",
            status=GateStatus.PASS,
            blocking=True,
            reason_code="ok",
            message="ok",
        ),
        GateResult(
            gate_id="identity_consistent",
            status=GateStatus.WARN,
            blocking=False,
            reason_code="no_audio",
            message="No audio assets to hash-verify.",
        ),
        GateResult(
            gate_id="human_approved",
            status=GateStatus.WARN,
            blocking=False,
            reason_code="not_applicable",
            message="No promotion requested; approval is not applicable.",
        ),
    ]
    has_blocking_fail = any(g.status == GateStatus.FAIL and g.blocking for g in gates)
    has_warnings = any(g.status == GateStatus.WARN for g in gates)
    assert not has_blocking_fail
    assert has_warnings


def test_blocking_fail_not_cancelled_by_pass() -> None:
    gates: list[GateResult] = [
        GateResult(
            gate_id="input_complete",
            status=GateStatus.PASS,
            blocking=True,
            reason_code="ok",
            message="ok",
        ),
        GateResult(
            gate_id="report_complete",
            status=GateStatus.FAIL,
            blocking=True,
            reason_code="report_missing",
            message="Report artifact not found.",
        ),
    ]
    has_blocking_fail = any(g.status == GateStatus.FAIL and g.blocking for g in gates)
    assert has_blocking_fail
