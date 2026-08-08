from pathlib import Path

import duckdb
import pytest

from moodify_bridge.schemas import HumanApproval, MoodifyRule, RuleState
from moodify_bridge.serialization import read_model, write_yaml
from moodify_bridge.services import compile_evidence, promote_rule, validate_case
from moodify_bridge.store import LedgerStore


def test_case_is_immutable_and_revision_is_appended(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = Path(__file__).parents[1]; monkeypatch.chdir(project)
    case = read_model(project / "demo/case.yaml", __import__("moodify_bridge.schemas", fromlist=["ProductionCase"]).ProductionCase)
    db = LedgerStore(tmp_path); db.create_case(case)
    with pytest.raises(ValueError, match="immutable"):
        db.create_case(case)
    db.append_revision(case.case_id, {"title": "corrected"}, "typo")
    with duckdb.connect(str(db.db_path)) as con:
        assert con.execute("SELECT count(*) FROM ledger_events WHERE event_type='revision_appended'").fetchone()[0] == 1
    assert db.get_case(case.case_id).title == case.title


def test_missing_measurement_is_warning_not_invention(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = Path(__file__).parents[1]; monkeypatch.chdir(project)
    from moodify_bridge.schemas import ProductionCase
    case = read_model(project / "demo/case.yaml", ProductionCase)
    db = LedgerStore(tmp_path); db.create_case(case)
    packet = compile_evidence(db, case.case_id)
    assert packet.measurement_ids == ()
    assert any("no measurements" in warning for warning in packet.warnings)
    assert validate_case(case).valid


def test_promotion_requires_explicit_approval(tmp_path: Path) -> None:

    rule_path = tmp_path / "rule.yaml"
    rule = MoodifyRule(rule_id="R-TEST-001", version="1.0", title="test",
                       state=RuleState.PROPOSED, rationale="test", parameters={})
    write_yaml(rule_path, rule)
    db = LedgerStore(tmp_path / "db")
    with pytest.raises(PermissionError, match="human approval"):
        promote_rule(db, rule_path, RuleState.EXPERIMENTAL)
    approval = HumanApproval(rule_id="R-TEST-001", rule_version="1.0",
                             approver="reviewer", rationale="ok")
    db.add_approval(approval)
    promoted = promote_rule(db, rule_path, RuleState.EXPERIMENTAL)
    assert promoted.state is RuleState.EXPERIMENTAL
