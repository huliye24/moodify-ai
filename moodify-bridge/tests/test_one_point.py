"""Tests for OnePointSpec, OnePointResult, conflict detection, and refine_prepare."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from moodify_bridge.hashing import sha256_file
from moodify_bridge.schemas import OnePointResult, OnePointSpec, OnePointStatus
from moodify_bridge.services import detect_conflicts, refine_prepare


def _make_spec(**overrides) -> OnePointSpec:
    defaults = {
        "source": "E:/moodify/moodify-bridge/demo/case.yaml",
        "essence": "test work",
        "must_preserve": ("identity",),
        "desired_change": "verify integrity",
        "must_avoid": ("corruption",),
        "human_owner": "tester",
    }
    defaults.update(overrides)
    return OnePointSpec(**defaults)


class TestOnePointSpec:
    def test_valid_spec(self) -> None:
        spec = _make_spec()
        assert spec.essence == "test work"
        assert len(spec.must_preserve) == 1

    def test_empty_essence_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _make_spec(essence="")

    def test_empty_must_preserve_rejected(self) -> None:
        with pytest.raises(ValidationError, match="must_preserve"):
            _make_spec(must_preserve=())

    def test_empty_must_avoid_rejected(self) -> None:
        with pytest.raises(ValidationError, match="must_avoid"):
            _make_spec(must_avoid=())

    def test_empty_human_owner_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _make_spec(human_owner="")

    @pytest.mark.parametrize("field", ["source", "essence", "desired_change", "human_owner"])
    def test_whitespace_only_text_rejected(self, field: str) -> None:
        with pytest.raises(ValidationError):
            _make_spec(**{field: "   "})

    def test_blank_constraint_item_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _make_spec(must_preserve=("identity", "   "))

    def test_unknown_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs"):
            OnePointSpec(
                source="x", essence="x", must_preserve=("x",),
                desired_change="x", must_avoid=("x",), human_owner="x",
                unknown_field="intruder",
            )

    def test_essence_too_long_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _make_spec(essence="x" * 501)


class TestConflictDetection:
    def test_no_conflict(self) -> None:
        spec = _make_spec(
            must_preserve=("identity",),
            desired_change="verify integrity",
            must_avoid=("corruption",),
        )
        assert detect_conflicts(spec) == []

    def test_bright_vs_dark_conflict(self) -> None:
        spec = _make_spec(
            must_preserve=("dark tonal character",),
            desired_change="make it bright and airy",
        )
        conflicts = detect_conflicts(spec)
        assert len(conflicts) > 0
        assert any("bright" in c and "dark" in c for c in conflicts)

    def test_loudness_in_desire_vs_dynamic_in_preserve(self) -> None:
        spec = _make_spec(
            must_preserve=("dynamic range",),
            desired_change="increase loudness",
        )
        conflicts = detect_conflicts(spec)
        assert len(conflicts) > 0

    def test_desire_in_avoid_keyword(self) -> None:
        spec = _make_spec(
            desired_change="add reverb",
            must_avoid=("dry signal loss",),
        )
        conflicts = detect_conflicts(spec)
        assert len(conflicts) > 0
        assert any("reverb" in c and "dry" in c for c in conflicts)

    def test_direct_desired_and_avoided_term_conflict(self) -> None:
        spec = _make_spec(
            desired_change="increase saturation gently",
            must_avoid=("saturation artifacts",),
        )
        assert any("saturation" in conflict for conflict in detect_conflicts(spec))


class TestOnePointResult:
    def test_result_status_values(self) -> None:
        statuses = {s.value for s in OnePointStatus}
        assert statuses == {"READY_FOR_REVIEW", "BLOCKED", "NEEDS_EVIDENCE", "FAILED"}

    def test_no_final_status(self) -> None:
        assert "FINAL" not in {s.value for s in OnePointStatus}
        assert "COMPLETED" not in {s.value for s in OnePointStatus}
        assert "APPROVED" not in {s.value for s in OnePointStatus}

    def test_result_forbidden_fields(self) -> None:
        fields = set(OnePointResult.model_fields.keys())
        assert "final" not in fields
        assert "approved" not in fields
        assert "score" not in fields
        assert "rating" not in fields


class TestRefinePrepare:
    def test_success_reads_demo_case(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"))
        out = tmp_path / "run"
        result = refine_prepare(spec, out)
        assert result.status == OnePointStatus.READY_FOR_REVIEW
        assert (out / "result.json").exists()
        assert (out / "summary.md").exists()
        assert (out / "summary.html").exists()
        assert (out / "FINAL_STATUS.txt").exists()
        assert (out / "evidence").is_dir()

    def test_blocked_on_conflict(self, tmp_path: Path) -> None:
        spec = _make_spec(
            must_preserve=("dark tonal character",),
            desired_change="make it bright",
        )
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.BLOCKED
        assert "BLOCKED" in (tmp_path / "run" / "FINAL_STATUS.txt").read_text()

    def test_needs_evidence_on_missing_source(self, tmp_path: Path) -> None:
        spec = _make_spec(source="E:/nonexistent/path.yaml")
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.NEEDS_EVIDENCE

    def test_five_narratives_in_summary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"))
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.READY_FOR_REVIEW
        summary = (tmp_path / "run" / "summary.md").read_text(encoding="utf-8")
        assert "Essence" in summary
        assert "Protect" in summary
        assert "Allow" in summary
        assert "Action" in summary
        assert "Entrust" in summary

    def test_no_internal_acronyms_in_summary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"))
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.READY_FOR_REVIEW
        summary = (tmp_path / "run" / "summary.md").read_text(encoding="utf-8")
        for acronym in ("WSE", "MSE", "PPE", "MRS"):
            assert acronym not in summary, f"Internal acronym '{acronym}' leaked into summary"

    def test_no_false_improvement_claims_in_summary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"))
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.READY_FOR_REVIEW
        summary = (tmp_path / "run" / "summary.md").read_text(encoding="utf-8")
        # Check system-generated false claims (not human-entrustment language)
        for word in ("improved", "enhanced", "better", "mastered", "processed audio",
                     "final version", "final output", "auto-final"):
            assert word not in summary.lower(), f"'{word}' should not appear in summary"

    def test_human_owner_always_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"), human_owner="Alice Producer")
        result = refine_prepare(spec, tmp_path / "run")
        assert "Alice Producer" in result.entrust
        assert "Alice Producer" in result.owner

    def test_evidence_paths_exist(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        project = Path(__file__).parents[1]
        monkeypatch.chdir(project)
        spec = _make_spec(source=str(project / "demo/case.yaml"))
        result = refine_prepare(spec, tmp_path / "run")
        assert result.status == OnePointStatus.READY_FOR_REVIEW
        evidence_dir = tmp_path / "run" / "evidence"
        assert evidence_dir.is_dir()
        expected = {
            "spec.yaml", "case.yaml", "run_manifest.json", "gate_results.json",
            "environment.json", "command_results.jsonl", "evidence.yaml",
            "FINAL_STATUS.txt", "package_manifest.json",
        }
        assert expected.issubset({path.name for path in evidence_dir.rglob("*") if path.is_file()})
        package = json.loads((evidence_dir / "package_manifest.json").read_text(encoding="utf-8"))
        for relative, digest in package["artifacts"].items():
            assert sha256_file(tmp_path / "run" / relative) == digest
        assert result.evidence_path == "evidence/package_manifest.json"

    def test_blocked_summary_does_not_claim_work_was_prepared(self, tmp_path: Path) -> None:
        spec = _make_spec(
            must_preserve=("dark tonal character",),
            desired_change="make it bright",
        )
        refine_prepare(spec, tmp_path / "run")
        summary = (tmp_path / "run" / "summary.md").read_text(encoding="utf-8")
        assert "No action taken" in summary
        assert "verified input integrity" not in summary
        assert "## Avoid" not in summary
        assert [line for line in summary.splitlines() if line.startswith("## ")] == [
            "## Essence", "## Protect", "## Allow", "## Action", "## Entrust",
        ]
