"""Atomicity tests: no partial promotion state survives any failure path."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest

from moodify_bridge.schemas import HumanApproval, MoodifyRule, RuleState, ValidationResult
from moodify_bridge.serialization import read_model, write_yaml
from moodify_bridge.services import validate_rule
from moodify_bridge.store import LedgerStore


def _make_rule(rule_id: str, version: str, state: RuleState, tmp_path: Path) -> Path:
    rule = MoodifyRule(
        rule_id=rule_id,
        version=version,
        title="test rule",
        state=state,
        rationale="test",
        parameters={"key": "val"},
    )
    path = tmp_path / f"{rule_id}.yaml"
    write_yaml(path, rule)
    return path


def _make_approval(rule_id: str, version: str, tmp_path: Path) -> Path:
    approval = HumanApproval(
        rule_id=rule_id,
        rule_version=version,
        approver="test-reviewer",
        rationale="approved for testing",
    )
    path = tmp_path / f"{rule_id}_approval.yaml"
    write_yaml(path, approval)
    return path


def test_approval_required_versus_present_semantics(tmp_path: Path) -> None:
    """approval_required=false, approval_present=false for PROPOSED rule."""
    store = LedgerStore(tmp_path / "db")
    rule_path = _make_rule("R-A", "1.0", RuleState.PROPOSED, tmp_path)
    rule = read_model(rule_path, MoodifyRule)
    result = validate_rule(store, rule)
    assert result.valid
    assert result.checks["approval_required"] is False
    assert result.checks["approval_present"] is False
    assert result.checks["approval_gate_satisfied"] is True
    assert result.approval_id is None


def test_approval_missing_for_production_yields_error(tmp_path: Path) -> None:
    """PRODUCTION rule without approval fails validation."""
    store = LedgerStore(tmp_path / "db")
    rule_path = _make_rule("R-B", "1.0", RuleState.PRODUCTION, tmp_path)
    rule = read_model(rule_path, MoodifyRule)
    result = validate_rule(store, rule)
    assert not result.valid
    assert result.checks["approval_required"] is True
    assert result.checks["approval_present"] is False
    assert result.checks["approval_gate_satisfied"] is False
    assert "lacks human approval" in result.errors[0]


def test_approval_present_for_production_passes(tmp_path: Path) -> None:
    """PRODUCTION rule with correct approval passes."""
    store = LedgerStore(tmp_path / "db")
    rule_path = _make_rule("R-C", "1.0", RuleState.PRODUCTION, tmp_path)
    approval_path = _make_approval("R-C", "1.0", tmp_path)
    approval = read_model(approval_path, HumanApproval)
    store.add_approval(approval)
    rule = read_model(rule_path, MoodifyRule)
    result = validate_rule(store, rule)
    assert result.valid
    assert result.checks["approval_required"] is True
    assert result.checks["approval_present"] is True
    assert result.checks["approval_gate_satisfied"] is True
    assert result.approval_id is not None


def test_wrong_version_approval_not_accepted(tmp_path: Path) -> None:
    """Approval for version 1.0 does not satisfy version 2.0."""
    store = LedgerStore(tmp_path / "db")
    approval_path = _make_approval("R-D", "1.0", tmp_path)
    store.add_approval(read_model(approval_path, HumanApproval))
    rule_path = _make_rule("R-D", "2.0", RuleState.PRODUCTION, tmp_path)
    rule = read_model(rule_path, MoodifyRule)
    result = validate_rule(store, rule)
    assert not result.valid
    assert result.checks["approval_present"] is False


def test_no_approval_in_db_after_validation_only(tmp_path: Path) -> None:
    """validate_rule never inserts approvals."""
    store = LedgerStore(tmp_path / "db")
    rule_path = _make_rule("R-E", "1.0", RuleState.PROPOSED, tmp_path)
    rule = read_model(rule_path, MoodifyRule)
    validate_rule(store, rule)
    with duckdb.connect(str(store.db_path)) as con:
        cnt = con.execute("SELECT count(*) FROM approvals").fetchone()[0]
    assert cnt == 0


def test_validate_case_returns_approval_id_null(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Case validation does not set an approval_id (it's not rule validation)."""
    project = Path(__file__).parents[1]
    monkeypatch.chdir(project)
    from moodify_bridge.schemas import ProductionCase

    case = read_model(project / "demo/case.yaml", ProductionCase)
    store = LedgerStore(tmp_path / "db")
    store.create_case(case)
    from moodify_bridge.services import validate_case

    result = validate_case(case)
    assert result.approval_id is None


def test_json_output_contains_clear_approval_fields() -> None:
    """The checks dict uses the three new keys."""
    result = ValidationResult(
        subject_type="rule",
        subject_id="R-X@1.0",
        valid=True,
        checks={
            "approval_required": False,
            "approval_present": False,
            "approval_gate_satisfied": True,
        },
    )
    d = json.loads(result.model_dump_json())
    assert d["checks"]["approval_required"] is False
    assert d["checks"]["approval_present"] is False
    assert d["checks"]["approval_gate_satisfied"] is True
