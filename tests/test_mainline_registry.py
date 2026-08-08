"""Tests for mainline_registry — strategic pack and gate report registry."""
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.mainline_registry import (
    read_registry,
    append_registry,
    register_pack,
    register_gate_report,
    list_packs,
    list_gate_reports,
    latest_pack,
    pack_summary,
)


class TestReadRegistry:
    def test_empty_file(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        p.write_text("", encoding="utf-8")
        assert read_registry(p) == []

    def test_nonexistent(self):
        assert read_registry(Path("/nonexistent/reg.jsonl")) == []

    def test_reads_entries(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        p.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
        rows = read_registry(p)
        assert len(rows) == 2


class TestAppendRegistry:
    def test_appends(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        append_registry(p, {"pack_id": "p1"})
        append_registry(p, {"pack_id": "p2"})
        rows = read_registry(p)
        assert len(rows) == 2
        assert rows[0]["pack_id"] == "p1"


class TestRegisterPack:
    def test_creates_entry(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        entry = register_pack(p, "pack-001", "E-CHAIN-015", "NEM-015",
                              "/tmp/pack", 4,
                              xclp_scores={"deepseek": 65.0})
        assert entry["pack_id"] == "pack-001"
        assert entry["task_count"] == 4
        assert entry["xclp_scores"]["deepseek"] == 65.0
        assert "registered_at" in entry

        rows = read_registry(p)
        assert len(rows) == 1


class TestRegisterGateReport:
    def test_creates_gate_entry(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        entry = register_gate_report(p, "deepseek_client", "E-CHAIN-015",
                                     65.0, "NEM-ready", "ADOPT", True,
                                     "/tmp/report.md")
        assert entry["type"] == "gate_report"
        assert entry["module_name"] == "deepseek_client"
        assert entry["passed"] is True


class TestListFunctions:
    def test_list_packs_only(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        register_pack(p, "p1", "EC-1", "NEM-1", "/tmp", 1)
        register_gate_report(p, "mod", "EC-1", 65, "NEM-ready", "ADOPT", True, "/tmp/r.md")
        register_pack(p, "p2", "EC-1", "NEM-2", "/tmp", 2)
        assert len(list_packs(p)) == 2
        assert len(list_gate_reports(p)) == 1

    def test_latest_pack(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        register_pack(p, "p1", "EC-1", "NEM-1", "/tmp", 1)
        register_pack(p, "p2", "EC-1", "NEM-2", "/tmp", 2)
        assert latest_pack(p)["pack_id"] == "p2"

    def test_latest_pack_empty(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        assert latest_pack(p) is None

    def test_pack_summary(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "reg.jsonl"
        register_pack(p, "p1", "EC-1", "NEM-1", "/tmp", 4)
        register_gate_report(p, "mod", "EC-1", 80, "Core", "CORE", True, "/tmp/r.md")
        s = pack_summary(p)
        assert s["total_packs"] == 1
        assert s["total_gate_reports"] == 1
        assert s["latest_pack"] == "p1"
