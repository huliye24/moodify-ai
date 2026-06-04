"""Tests for TIDAL-OPERATIONS-010 — control API, dashboard, alerts, approvals, pause (MHP-593~604)."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from moodify_runtime.tidal_operations import (
    TidalControlState, DashboardSnapshot, OperatorAlert, ApprovalRequest,
    EmergencyPause, OperatorNote,
    get_tidal_state, request_tidal_pause, request_tidal_resume,
    get_dashboard_snapshot, get_cycle_timeline,
    get_brief_inbox, save_morning_brief,
    create_approval, resolve_approval,
    create_alert, get_active_alerts, acknowledge_alert,
    emergency_pause, write_operator_note, read_operator_notes,
    run_operations_smoke, _parse_etime,
)


class TestEtimeParser:
    def test_hh_mm_ss(self):
        assert _parse_etime("01:30:45") == 3600 + 1800 + 45

    def test_dd_hh_mm_ss(self):
        assert _parse_etime("2-03:30:00") == 2 * 86400 + 3 * 3600 + 1800

    def test_zero(self):
        assert _parse_etime("00:00:00") == 0


class TestControlState:
    """MHP-593"""

    def test_default_state(self):
        s = TidalControlState()
        assert not s.running
        assert s.pid is None

    def test_to_dict(self):
        d = TidalControlState(running=True, pid=1234, current_cycle=5).to_dict()
        assert d["running"] and d["pid"] == 1234 and d["current_cycle"] == 5

    def test_get_state_returns_object(self):
        s = get_tidal_state()
        assert isinstance(s, TidalControlState)
        assert not s.running or isinstance(s.pid, (int, type(None)))

    def test_pause_resume_cycle(self):
        r1 = request_tidal_pause("test")
        assert r1["ok"]
        r2 = request_tidal_resume()
        assert r2["ok"]


class TestDashboard:
    """MHP-594"""

    def test_snapshot_default(self):
        s = get_dashboard_snapshot()
        assert isinstance(s, DashboardSnapshot)
        assert "tidal" in s.health
        assert "disk" in s.health

    def test_snapshot_to_dict(self):
        d = get_dashboard_snapshot().to_dict()
        assert "tidal" in d
        assert "health" in d
        assert "recent_cycles" in d


class TestTimeline:
    """MHP-595"""

    def test_timeline_no_file(self):
        tl = get_cycle_timeline(records_file="nonexistent.jsonl")
        assert isinstance(tl, list)


class TestBriefInbox:
    """MHP-596"""

    def test_save_and_list_briefs(self):
        path = save_morning_brief("# Test Brief\ncontent", brief_dir="outputs/tidal/briefs")
        assert path.endswith(".md")
        briefs = get_brief_inbox("outputs/tidal/briefs")
        assert len(briefs) >= 1


class TestApprovals:
    """MHP-597"""

    def test_create_approval(self):
        ar = create_approval("gate_override", "needs review")
        assert ar.status == "pending"
        assert ar.request_type == "gate_override"

    def test_resolve_approved(self):
        ar = create_approval("pause", "reason")
        resolved = resolve_approval(ar, True, note="ok")
        assert resolved.status == "approved"
        assert resolved.resolved_at != ""

    def test_resolve_denied(self):
        ar = create_approval("config_change", "reason")
        resolved = resolve_approval(ar, False, note="no")
        assert resolved.status == "denied"


class TestAlerts:
    """MHP-599"""

    def test_create_alert(self):
        a = create_alert("warn", "disk low", title="Low Disk")
        assert a.level == "warn"
        assert a.title == "Low Disk"
        assert not a.acknowledged

    def test_get_active_alerts(self):
        create_alert("info", "test1")
        create_alert("critical", "test2")
        active = get_active_alerts()
        assert len(active) >= 2

    def test_acknowledge_alert(self):
        a = create_alert("info", "to ack")
        result = acknowledge_alert(a.alert_id)
        assert result is not None
        assert result.acknowledged

    def test_acknowledge_nonexistent(self):
        result = acknowledge_alert("no-such-id")
        assert result is None

    def test_invalid_level_defaults_to_info(self):
        a = create_alert("INVALID", "msg")
        assert a.level == "info"


class TestEmergencyPause:
    """MHP-601"""

    def test_emergency_pause_creates_record(self):
        ep = emergency_pause("disk full", triggered_by="auto-guard")
        assert ep.reason == "disk full"
        assert ep.status == "active"

    def test_emergency_pause_with_auto_resume(self):
        ep = emergency_pause("transient", auto_resume=True, auto_resume_after_s=300)
        assert ep.auto_resume
        assert ep.auto_resume_after_s == 300


class TestOperatorNotes:
    """MHP-602"""

    def test_write_and_read_notes(self):
        n = write_operator_note("task-001", "needs review", tags=["review"])
        assert n.note_id is not None
        notes = read_operator_notes("task-001")
        assert len(notes) >= 1
        assert notes[-1].content == "needs review"

    def test_read_all_notes(self):
        notes = read_operator_notes()
        assert isinstance(notes, list)

    def test_tags_persisted(self):
        n = write_operator_note("task-tag", "test", tags=["urgent", "mrs"])
        notes = read_operator_notes("task-tag")
        assert "urgent" in notes[-1].tags
        assert "mrs" in notes[-1].tags


class TestSmoke:
    """MHP-604"""

    def test_smoke_runs(self):
        r = run_operations_smoke()
        assert r["smoke_ok"], f"Smoke failed: {r}"
        assert r["control_api_ok"]
        assert r["alert_created"] and r["alert_ack"]
        assert r["approval_created"] and r["approval_resolved"]
        assert r["note_written"] and r["notes_read"] > 0
        assert r["pause_ok"] and r["resume_ok"]
