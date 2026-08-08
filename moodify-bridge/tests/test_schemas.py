from pathlib import Path

import pytest
from pydantic import ValidationError

from moodify_bridge.schemas import DecisionRecord, ProductionCase, RuleRecord, RuleState
from moodify_bridge.serialization import read_model


def test_demo_case_is_strict_and_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).parents[1]
    monkeypatch.chdir(root)
    case = read_model(root / "demo/case.yaml", ProductionCase)
    assert case.golden
    assert {item.kind.value for item in case.assets} >= {"stem", "midi", "score", "lyrics"}


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs"):
        ProductionCase.model_validate({"schema_version": "1.0.0", "unexpected": True})


def test_decision_cannot_select_unregistered_candidate() -> None:
    with pytest.raises(ValidationError, match="selected candidate"):
        DecisionRecord(
            decision_id="DEC-CASE-20260801-0001-v1",
            case_id="11111111-1111-4111-8111-111111111111",
            candidate_ids=("CAND-CASE-20260801-0001-01",),
            selected_candidate_id="CAND-CASE-20260801-0001-02",
            decision="select", reason="test", evaluation_ids=("EVAL-X-v1",),
            decision_maker_type="human", decision_maker_id="reviewer",
        )


def test_production_rule_requires_human_approval() -> None:
    with pytest.raises(ValidationError, match="human approval"):
        RuleRecord(rule_id="RULE-WSE-001", version="1.0", title="test",
                   state=RuleState.PRODUCTION, rationale="test", parameters={}, domain="WSE")
