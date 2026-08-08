"""Tests for the project governance ledger (023)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.project_governance.cadence import daily_check, stage_check, weekly_check
from tools.project_governance.gate import validate_ledger
from tools.project_governance.ledger import (
    TaskLedger,
    derive_state,
    load_ledger,
    new_event,
    save_ledger,
)
from tools.project_governance.views import (
    build_awaiting_review_table,
    build_conflict_table,
    build_in_progress_table,
    build_task_table,
)


def _ledger(*events) -> TaskLedger:
    ledger = TaskLedger()
    for event in events:
        ledger.append(event)
    return ledger


def _orch(task: str, ts: str = "2026-08-02T00:00:01Z", seq: str = "1") -> object:
    return new_event(task, f"e{seq}-{task}", "orchestration", "test", ts, "src", "ev")


def _handoff(task: str, ts: str = "2026-08-02T00:00:02Z", seq: str = "2") -> object:
    return new_event(task, f"e{seq}-{task}", "handoff", "test", ts, "src", "ev")


def _accept(task: str, ts: str = "2026-08-02T00:00:03Z", seq: str = "3") -> object:
    return new_event(task, f"e{seq}-{task}", "acceptance", "test", ts, "src", "ev")


def _rework(task: str, ts: str = "2026-08-02T00:00:04Z", seq: str = "4") -> object:
    return new_event(task, f"e{seq}-{task}", "rework", "test", ts, "src", "ev")


class TestDeriveState:
    def test_planned_from_orchestration(self) -> None:
        state, _ = derive_state([_orch("T1")])
        assert state == "PLANNED"

    def test_ready_from_handoff(self) -> None:
        state, _ = derive_state([_orch("T1"), _handoff("T1")])
        assert state == "READY_FOR_REVIEW"

    def test_accepted_from_acceptance(self) -> None:
        state, _ = derive_state([_orch("T1"), _handoff("T1"), _accept("T1")])
        assert state == "ACCEPTED"

    def test_silent_downgrade_detected(self) -> None:
        state, conflict = derive_state([
            _orch("T1"),
            _handoff("T1"),
            _accept("T1"),
            _handoff("T1", ts="2026-08-02T00:00:04Z", seq="4"),
        ])
        assert state == "ACCEPTED"
        assert conflict and "after acceptance" in conflict

    def test_empty_unknown(self) -> None:
        state, _ = derive_state([])
        assert state == "UNKNOWN"


class TestGate:
    def test_duplicate_event_id_rejected_on_append(self) -> None:
        a = _orch("T1")
        ledger = _ledger(a)
        with pytest.raises(ValueError, match="duplicate"):
            ledger.append(new_event("T1", a.event_id, "handoff", "test", "2026-08-02T00:00:02Z", "s", "e"))

    def test_missing_evidence_on_acceptance(self) -> None:
        event = new_event("T1", "e3", "acceptance", "test", "2026-08-02T00:00:03Z", "src", "")
        issues = validate_ledger(_ledger(event))
        assert any(i["kind"] == "missing_evidence" for i in issues)

    def test_silent_downgrade_flagged(self) -> None:
        ledger = _ledger(
            _orch("T1"),
            _handoff("T1"),
            _accept("T1"),
            _handoff("T1", ts="2026-08-02T00:00:04Z", seq="4"),
        )
        issues = validate_ledger(ledger)
        assert any(i["kind"] == "silent_downgrade" for i in issues)

    def test_clean_ledger_passes(self) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _accept("T1"))
        assert validate_ledger(ledger) == []


class TestViews:
    def test_task_table_single_state_per_task(self) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _accept("T1"), _orch("T2"))
        table = build_task_table(ledger)
        assert len(table) == 2
        states = {r["task_id"]: r["state"] for r in table}
        assert states == {"T1": "ACCEPTED", "T2": "PLANNED"}

    def test_planned_not_in_progress(self) -> None:
        ledger = _ledger(_orch("T1"), _orch("T2"))
        assert build_in_progress_table(ledger) == []

    def test_in_progress_only_active(self) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _rework("T1"), _orch("T2"))
        rows = build_in_progress_table(ledger)
        assert [r["task_id"] for r in rows] == ["T1"]

    def test_awaiting_review(self) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _orch("T2"), _accept("T2"))
        rows = build_awaiting_review_table(ledger)
        assert [r["task_id"] for r in rows] == ["T1"]

    def test_conflict_table(self) -> None:
        ledger = _ledger(
            _orch("T1"),
            _handoff("T1"),
            _accept("T1"),
            _handoff("T1", ts="2026-08-02T00:00:04Z", seq="4"),
        )
        rows = build_conflict_table(ledger)
        assert len(rows) == 1


class TestCadence:
    def test_daily_pass_on_clean(self, tmp_path: Path) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"))
        path = tmp_path / "ledger.jsonl"
        save_ledger(ledger, path)
        result = daily_check(path)
        assert result["pass"] is True

    def test_stage_openable_when_clean(self, tmp_path: Path) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"))
        path = tmp_path / "ledger.jsonl"
        save_ledger(ledger, path)
        result = stage_check(path)
        assert result["next_task_openable"] is True

    def test_stage_not_openable_with_conflict(self, tmp_path: Path) -> None:
        ledger = _ledger(
            _orch("T1"),
            _handoff("T1"),
            _accept("T1"),
            _handoff("T1", ts="2026-08-02T00:00:04Z", seq="4"),
        )
        path = tmp_path / "ledger.jsonl"
        save_ledger(ledger, path)
        result = stage_check(path)
        assert result["next_task_openable"] is False

    def test_weekly_reports_share(self, tmp_path: Path) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _accept("T1"), _orch("T2"), _handoff("T2"))
        path = tmp_path / "ledger.jsonl"
        save_ledger(ledger, path)
        result = weekly_check(path)
        assert result["accepted"] == 1
        assert result["started"] == 2
        assert result["accepted_share_pct"] == 50.0


class TestRoundTrip:
    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        ledger = _ledger(_orch("T1"), _handoff("T1"), _accept("T1"))
        path = tmp_path / "ledger.jsonl"
        save_ledger(ledger, path)
        restored = load_ledger(path)
        assert len(restored.events) == 3
        assert restored.state_of("T1") == ledger.state_of("T1")

    def test_append_only_duplicate_rejected(self) -> None:
        a = _orch("T1")
        ledger = _ledger(a)
        with pytest.raises(ValueError, match="duplicate"):
            ledger.append(new_event("T1", a.event_id, "handoff", "t", "ts", "s"))
