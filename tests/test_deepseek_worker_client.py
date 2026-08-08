"""Tests for deepseek_worker_client — transport layer for DeepSeek v4 API."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from scripts.deepseek_worker_client import (
    load_jsonl,
    write_jsonl,
    validate_output,
    process_tasks,
)


class TestLoadJsonl:
    def test_empty_file(self):
        d = tempfile.mkdtemp()
        path = Path(d) / "empty.jsonl"
        path.write_text("", encoding="utf-8")
        assert load_jsonl(path) == []

    def test_nonexistent_file(self):
        assert load_jsonl(Path("/nonexistent/tasks.jsonl")) == []

    def test_loads_records(self):
        d = tempfile.mkdtemp()
        path = Path(d) / "tasks.jsonl"
        path.write_text(
            '{"task_id":"1","loop":"runtime_reliability"}\n'
            '{"task_id":"2","loop":"scoring_calibration"}\n',
            encoding="utf-8",
        )
        rows = load_jsonl(path)
        assert len(rows) == 2
        assert rows[0]["task_id"] == "1"
        assert rows[1]["task_id"] == "2"

    def test_skips_blank_lines(self):
        d = tempfile.mkdtemp()
        path = Path(d) / "tasks.jsonl"
        path.write_text('\n{"task_id":"1"}\n\n', encoding="utf-8")
        rows = load_jsonl(path)
        assert len(rows) == 1


class TestWriteJsonl:
    def test_writes_and_reads(self):
        d = tempfile.mkdtemp()
        path = Path(d) / "out.jsonl"
        rows = [{"task_id": "1"}, {"task_id": "2"}]
        write_jsonl(path, rows)
        loaded = load_jsonl(path)
        assert loaded == rows


class TestValidateOutput:
    SCHEMA = {
        "type": "object",
        "required": ["task_id", "loop", "severity", "reason", "next_action", "needs_human_review"],
        "properties": {
            "task_id": {"type": "string"},
            "loop": {"enum": ["runtime_reliability", "scoring_calibration", "craft_preset_selection", "operator_report"]},
            "severity": {"enum": ["low", "medium", "high"]},
            "reason": {"type": "string", "maxLength": 180},
            "next_action": {"type": "string", "maxLength": 220},
            "needs_human_review": {"type": "boolean"},
        },
        "additionalProperties": False,
    }

    def test_valid_output(self):
        output = {
            "task_id": "t1",
            "loop": "runtime_reliability",
            "severity": "medium",
            "reason": "test reason",
            "next_action": "test action",
            "needs_human_review": True,
        }
        assert validate_output(output, self.SCHEMA) == []

    def test_missing_required_field(self):
        output = {"task_id": "t1"}
        errors = validate_output(output, self.SCHEMA)
        assert any("loop" in e for e in errors)

    def test_invalid_enum(self):
        output = {
            "task_id": "t1",
            "loop": "invalid_loop",
            "severity": "low",
            "reason": "x",
            "next_action": "y",
            "needs_human_review": False,
        }
        errors = validate_output(output, self.SCHEMA)
        assert any("invalid_loop" in e for e in errors)

    def test_reason_too_long(self):
        output = {
            "task_id": "t1",
            "loop": "runtime_reliability",
            "severity": "low",
            "reason": "x" * 200,
            "next_action": "y",
            "needs_human_review": False,
        }
        errors = validate_output(output, self.SCHEMA)
        assert any("maxLength" in e or "length" in e for e in errors)

    def test_extra_properties_rejected(self):
        output = {
            "task_id": "t1",
            "loop": "runtime_reliability",
            "severity": "low",
            "reason": "x",
            "next_action": "y",
            "needs_human_review": False,
            "invented_field": "bad",
        }
        errors = validate_output(output, self.SCHEMA)
        assert any("additional" in e for e in errors)

    def test_invalid_severity(self):
        output = {
            "task_id": "t1",
            "loop": "runtime_reliability",
            "severity": "critical",
            "reason": "x",
            "next_action": "y",
            "needs_human_review": False,
        }
        errors = validate_output(output, self.SCHEMA)
        assert any("critical" in e for e in errors)


class TestProcessTasks:
    SCHEMA = TestValidateOutput.SCHEMA

    def test_dry_run_skips_api(self):
        d = tempfile.mkdtemp()
        tasks = [{"task_id": "t1", "loop": "runtime_reliability"}]
        result = process_tasks(
            tasks, "prompt", self.SCHEMA,
            "", "", "", 30,
            dry_run=True, out_dir=Path(d),
        )
        assert result["total"] == 1
        assert result["validated"] == 1
        assert result["rejected"] == 0
        assert result["dry_run"] is True

        outputs = load_jsonl(Path(result["outputs_path"]))
        assert outputs[0]["reason"] == "dry-run: no API call"

    @patch("scripts.deepseek_worker_client.call_deepseek")
    def test_valid_call(self, mock_call):
        mock_call.return_value = {
            "task_id": "t1",
            "loop": "runtime_reliability",
            "severity": "low",
            "reason": "ok",
            "next_action": "proceed",
            "needs_human_review": False,
        }
        d = tempfile.mkdtemp()
        tasks = [{"task_id": "t1", "loop": "runtime_reliability"}]
        result = process_tasks(
            tasks, "prompt", self.SCHEMA,
            "key", "url", "model", 30,
            dry_run=False, out_dir=Path(d),
        )
        assert result["validated"] == 1
        assert result["rejected"] == 0

    @patch("scripts.deepseek_worker_client.call_deepseek")
    def test_rejected_on_api_error(self, mock_call):
        mock_call.side_effect = RuntimeError("API down")
        d = tempfile.mkdtemp()
        tasks = [{"task_id": "t1", "loop": "runtime_reliability"}]
        result = process_tasks(
            tasks, "prompt", self.SCHEMA,
            "key", "url", "model", 30,
            dry_run=False, out_dir=Path(d),
        )
        assert result["validated"] == 0
        assert result["rejected"] == 1

    @patch("scripts.deepseek_worker_client.call_deepseek")
    def test_rejected_on_invalid_output(self, mock_call):
        mock_call.return_value = {"task_id": "t1"}
        d = tempfile.mkdtemp()
        tasks = [{"task_id": "t1", "loop": "runtime_reliability"}]
        result = process_tasks(
            tasks, "prompt", self.SCHEMA,
            "key", "url", "model", 30,
            dry_run=False, out_dir=Path(d),
        )
        assert result["rejected"] == 1
