"""Automated tests for CLI stable error codes, exit codes, and no-traceback behavior."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from moodify_bridge.cli import app
from moodify_bridge.schemas import HumanApproval, MoodifyRule, RuleState
from moodify_bridge.serialization import write_yaml

runner = CliRunner()


def _write_rule(path: Path, rule_id: str, version: str, state: RuleState) -> None:
    write_yaml(path, MoodifyRule(
        rule_id=rule_id, version=version, title="test",
        state=state, rationale="test", parameters={},
    ))


def _write_approval(path: Path, rule_id: str, version: str) -> None:
    write_yaml(path, HumanApproval(
        rule_id=rule_id, rule_version=version,
        approver="reviewer", rationale="ok",
    ))


def _run(args: list[str]) -> tuple[str, int]:
    result = runner.invoke(app, args, catch_exceptions=False)
    return result.stdout + "\n" + (result.stderr or ""), result.exit_code


class TestRulePromoteErrors:
    def test_approval_file_missing(self, tmp_path: Path) -> None:
        rule_path = tmp_path / "rule.yaml"
        _write_rule(rule_path, "R-X", "1.0", RuleState.PROPOSED)
        output, code = _run([
            "rule", "promote", str(rule_path), "experimental",
            str(tmp_path / "no_approval.yaml"), "--root", str(tmp_path / "db"),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "APPROVAL_FILE_MISSING" in output

    def test_rule_file_missing(self, tmp_path: Path) -> None:
        approval_path = tmp_path / "approval.yaml"
        _write_approval(approval_path, "R-X", "1.0")
        output, code = _run([
            "rule", "promote", str(tmp_path / "no_rule.yaml"), "experimental",
            str(approval_path), "--root", str(tmp_path / "db"),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "RULE_FILE_MISSING" in output

    def test_approval_rule_mismatch(self, tmp_path: Path) -> None:
        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-A", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-B", "2.0")
        output, code = _run([
            "rule", "promote", str(rule_path), "experimental",
            str(approval_path), "--root", str(tmp_path / "db"),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "APPROVAL_RULE_MISMATCH" in output

    def test_invalid_transition(self, tmp_path: Path) -> None:
        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-C", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-C", "1.0")
        output, code = _run([
            "rule", "promote", str(rule_path), "production",
            str(approval_path), "--root", str(tmp_path / "db"),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "INVALID_RULE_TRANSITION" in output

    def test_no_traceback_in_error_output(self, tmp_path: Path) -> None:
        rule_path = tmp_path / "rule.yaml"
        _write_rule(rule_path, "R-D", "1.0", RuleState.PROPOSED)
        result = runner.invoke(app, [
            "rule", "promote", str(rule_path), "experimental",
            str(tmp_path / "no_file.yaml"), "--root", str(tmp_path / "db"),
        ], catch_exceptions=False)
        output = result.stdout + "\n" + (result.stderr or "")
        assert result.exit_code == 2
        assert "Traceback" not in output
        # The error output before '[' should not contain File/Error traceback header
        prefix = output.split("[")[0]
        assert "Error" not in prefix or "APPROVAL" in output


class TestPpeRunErrors:
    def test_output_dir_not_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        out = tmp_path / "not_empty"
        out.mkdir()
        (out / "sentinel.txt").write_text("x")
        output, code = _run([
            "ppe", "run", str(project / "demo/case.yaml"),
            "--output-dir", str(out),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "OUTPUT_DIR_NOT_EMPTY" in output

    def test_missing_case_returns_fail_exit_1(self, tmp_path: Path) -> None:
        output, code = _run([
            "ppe", "run", str(tmp_path / "no_case.yaml"),
            "--output-dir", str(tmp_path / "out"),
        ])
        assert code == 1, f"Expected exit 1, got {code}. Output: {output}"
        assert "FAIL" in output


class TestAtomicPromotion:
    def test_no_db_approval_after_failed_transition(self, tmp_path: Path) -> None:
        """Illegal transition must not leave approval in DB."""
        import duckdb

        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-E", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-E", "1.0")
        db_root = tmp_path / "db"
        output, code = _run([
            "rule", "promote", str(rule_path), "production",
            str(approval_path), "--root", str(db_root),
        ])
        assert code == 2, f"Expected exit 2, got {code}. Output: {output}"
        assert "INVALID_RULE_TRANSITION" in output

        db_path = db_root / "ledger.duckdb"
        if db_path.exists():
            con = duckdb.connect(str(db_path))
            cnt = con.execute("SELECT count(*) FROM approvals").fetchone()[0]
            assert cnt == 0, f"Found {cnt} approvals after failed promotion"

    def test_successful_promotion_writes_both_db_and_file(self, tmp_path: Path) -> None:
        """Successful promotion writes approval + updates rule file."""
        import duckdb

        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-F", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-F", "1.0")
        db_root = tmp_path / "db"
        output, code = _run([
            "rule", "promote", str(rule_path), "experimental",
            str(approval_path), "--root", str(db_root),
        ])
        assert code == 0, f"Expected exit 0, got {code}. Output: {output}"

        con = duckdb.connect(str(db_root / "ledger.duckdb"))
        cnt = con.execute("SELECT count(*) FROM approvals").fetchone()[0]
        assert cnt == 1

        from moodify_bridge.serialization import read_model
        rule = read_model(rule_path, MoodifyRule)
        assert rule.state == RuleState.EXPERIMENTAL

    def test_no_partial_state_on_write_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """If file write fails during promotion, no partial state should remain."""
        import duckdb

        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-G", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-G", "1.0")
        db_root = tmp_path / "db"

        from moodify_bridge import services as svc

        call_count = [0]

        def failing_write(path: Path, rule: object) -> None:
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("simulated write failure")

        monkeypatch.setattr(svc, "_write_rule_file", failing_write)

        result = runner.invoke(app, [
            "rule", "promote", str(rule_path), "experimental",
            str(approval_path), "--root", str(db_root),
        ], catch_exceptions=True)
        assert result.exit_code != 0, f"Expected non-zero exit, got {result.exit_code}"

        # DB must NOT have approval
        db_path = db_root / "ledger.duckdb"
        if db_path.exists():
            con = duckdb.connect(str(db_path))
            cnt = con.execute("SELECT count(*) FROM approvals").fetchone()[0]
            assert cnt == 0, f"Partial state: {cnt} approvals in DB after write failure"

        # Rule file must be unchanged
        from moodify_bridge.serialization import read_model
        rule = read_model(rule_path, MoodifyRule)
        assert rule.state == RuleState.PROPOSED, f"Rule state changed to {rule.state}"

    def test_replace_failure_is_preserved_and_recovered(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A post-DB replace failure must retain recovery state and finish idempotently."""
        import duckdb

        from moodify_bridge import services as svc
        from moodify_bridge.serialization import read_model

        rule_path = tmp_path / "rule.yaml"
        approval_path = tmp_path / "approval.yaml"
        _write_rule(rule_path, "R-H", "1.0", RuleState.PROPOSED)
        _write_approval(approval_path, "R-H", "1.0")
        db_root = tmp_path / "db"
        real_replace = svc._replace_file

        def failing_replace(src: Path, dst: Path) -> None:
            raise OSError("simulated replace failure")

        monkeypatch.setattr(svc, "_replace_file", failing_replace)
        first = runner.invoke(app, [
            "rule", "promote", str(rule_path), "experimental",
            str(approval_path), "--root", str(db_root),
        ], catch_exceptions=False)
        assert first.exit_code == 3
        assert "PROMOTION_RECOVERY_REQUIRED" in first.stderr
        assert read_model(rule_path, MoodifyRule).state == RuleState.PROPOSED
        marker = rule_path.with_suffix(rule_path.suffix + svc.PROMOTION_MARKER_SUFFIX)
        assert marker.exists()
        marker_payload = __import__("json").loads(marker.read_text(encoding="utf-8"))
        assert Path(marker_payload["temp_path"]).exists()
        with duckdb.connect(str(db_root / "ledger.duckdb")) as con:
            assert con.execute("SELECT count(*) FROM approvals").fetchone()[0] == 1

        monkeypatch.setattr(svc, "_replace_file", real_replace)
        second = runner.invoke(app, [
            "rule", "promote", str(rule_path), "experimental",
            str(approval_path), "--root", str(db_root),
        ], catch_exceptions=False)
        assert second.exit_code == 0, second.stderr
        assert read_model(rule_path, MoodifyRule).state == RuleState.EXPERIMENTAL
        assert not marker.exists()
        assert not Path(marker_payload["temp_path"]).exists()
        with duckdb.connect(str(db_root / "ledger.duckdb")) as con:
            assert con.execute("SELECT count(*) FROM approvals").fetchone()[0] == 1
