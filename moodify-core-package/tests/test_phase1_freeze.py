"""Phase I freeze acceptance tests (MFY-PHASE1-FREEZE-001, 08_ACCEPTANCE_TESTS).

A. Scope freeze config exists and Phase II features are enumerated.
C. Reproducibility: rule/model versions recorded on judgments.
D. Failure semantics: BLOCKING findings without evidence are surfaced, never silent.
F. Regression: canonical CLI v2 entry remains.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from moodify.auditory.judgment import (
    JUDGMENT_RULES_VERSION,
    UNIVERSAL_THRESHOLDS,
    evaluate_risk_flags,
    judge,
)
from moodify.auditory.models import Judgment
from moodify.auditory.reports import build_auditory_report
from moodify.cli_v2.main import build_parser
from moodify.phase import PHASE2_ENV, phase2_experiments_enabled

CORE_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONFIG = CORE_PACKAGE_ROOT / "configs" / "phase1_scope.yaml"

EXPECTED_PHASE2_FROZEN = {
    "cwc_token",
    "marketplace",
    "transaction_center",
    "nft_or_collectible_trading",
    "physical_art_commerce",
    "copyright_exchange",
    "social_graph",
    "feed",
    "invitation_growth",
    "complex_creator_center",
    "publishing_distribution_network",
    "recommendation_network",
    "ai_comic",
    "ai_3d",
    "ecosystem_expansion",
    "enterprise_admin_suite",
}


@pytest.fixture
def sample_delta() -> dict:
    return {
        "clipping_sample_count": {"before": 0, "after": 1200, "absolute_delta": 1200},
        "true_peak_dbfs": {"before": -1.2, "after": -0.2, "absolute_delta": 1.0},
        "integrated_lufs": {"before": -16.0, "after": -11.0, "absolute_delta": 5.0},
        "crest_factor_db": {"before": 8.0, "after": 3.0, "absolute_delta": -5.0},
        "phase_risk_ratio": {"before": 0.01, "after": 0.05, "absolute_delta": 0.04},
        "finite_sample_ratio": {"before": 1.0, "after": 0.99, "absolute_delta": -0.01},
    }


@pytest.fixture
def before_metrics() -> dict:
    return {k: {"value": v["before"]} for k, v in {
        "clipping_sample_count": {"before": 0},
        "true_peak_dbfs": {"before": -1.2},
        "integrated_lufs": {"before": -16.0},
        "crest_factor_db": {"before": 8.0},
        "phase_risk_ratio": {"before": 0.01},
        "finite_sample_ratio": {"before": 1.0},
    }.items()}


@pytest.fixture
def after_metrics() -> dict:
    return {k: {"value": v["after"]} for k, v in {
        "clipping_sample_count": {"after": 1200},
        "true_peak_dbfs": {"after": -0.2},
        "integrated_lufs": {"after": -11.0},
        "crest_factor_db": {"after": 3.0},
        "phase_risk_ratio": {"after": 0.05},
        "finite_sample_ratio": {"after": 0.99},
    }.items()}


# --- A. Scope Freeze ------------------------------------------------------


def test_phase1_scope_config_exists():
    assert CONFIG.exists(), f"missing {CONFIG}"


def test_phase1_scope_freeze_behavior_default_off():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert cfg["organizing_question"] == "Can machines learn to hear?"
    assert cfg["canonical_loop"] == [
        "listen", "represent", "judge", "intervene", "verify", "learn",
    ]
    assert cfg["freeze_behavior"]["default"] == "feature_flag_off"
    assert cfg["freeze_behavior"]["hide_from_primary_navigation"] is True
    assert cfg["freeze_behavior"]["destructive_delete_requires_proof"] is True


def test_phase1_scope_enumerates_all_phase2_frozen():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    frozen = set(cfg["phase2_frozen"])
    assert EXPECTED_PHASE2_FROZEN <= frozen, f"missing: {EXPECTED_PHASE2_FROZEN - frozen}"


def test_phase2_product_surfaces_are_off_by_default(monkeypatch):
    monkeypatch.delenv(PHASE2_ENV, raising=False)
    assert not phase2_experiments_enabled()
    choices = build_parser()._subparsers._group_actions[0].choices
    assert "feed" not in choices
    assert "access" not in choices


def test_phase2_api_routes_are_off_by_default(monkeypatch):
    monkeypatch.delenv(PHASE2_ENV, raising=False)
    from moodify.api.main import app

    paths = {route.path for route in app.routes}
    assert not any(path.startswith("/api/v1/feed") for path in paths)
    for frozen_prefix in ("/api/v1/auth", "/api/v1/referral", "/api/v1/cwc", "/api/v1/compute"):
        assert not any(path.startswith(frozen_prefix) for path in paths)


def test_phase2_labs_require_explicit_opt_in(monkeypatch):
    monkeypatch.setenv(PHASE2_ENV, "true")
    choices = build_parser()._subparsers._group_actions[0].choices
    assert {"feed", "access"} <= set(choices)


# --- C. Reproducibility ---------------------------------------------------


def test_judgment_rules_version_recorded(sample_delta, before_metrics, after_metrics):
    flags = evaluate_risk_flags(sample_delta, before_metrics, after_metrics)
    assert flags, "sample delta should trigger flags"
    for f in flags:
        assert f.rule_or_model_version == f"judgment-rules-v{JUDGMENT_RULES_VERSION}"
        assert f.reference_basis, "every finding needs a reference basis"


def test_universal_thresholds_versioned():
    assert JUDGMENT_RULES_VERSION
    assert "new_clipping" in UNIVERSAL_THRESHOLDS


# --- D. Failure Semantics --------------------------------------------------


def test_risk_flag_contract_fields(sample_delta, before_metrics, after_metrics):
    flags = evaluate_risk_flags(sample_delta, before_metrics, after_metrics)
    blocking = [f for f in flags if f.severity == "BLOCKING"]
    assert blocking, "new clipping should be BLOCKING"
    d = blocking[0].to_dict()
    for field in (
        "code", "severity", "label", "observed_value", "unit", "reference_basis",
        "confidence", "classification", "rule_or_model_version", "evidence_refs",
    ):
        assert field in d, f"contract field missing: {field}"
    assert d["classification"] in {
        "TECHNICAL_RISK", "ARTISTIC_CHARACTERISTIC", "LIKELY_ARTIFACT",
        "STRUCTURAL_ANOMALY", "INFORMATIONAL", "UNCERTAIN", "INSUFFICIENT_EVIDENCE",
    }


def test_blocking_finding_always_has_evidence_refs(sample_delta, before_metrics, after_metrics):
    flags = evaluate_risk_flags(sample_delta, before_metrics, after_metrics)
    for f in flags:
        if f.severity == "BLOCKING":
            assert f.evidence_refs, "BLOCKING finding must resolve to evidence"


def test_high_severity_finding_without_evidence_marks_report_partial(tmp_path):
    finding = {
        "code": "FAKE_BLOCKING", "severity": "BLOCKING",
        "message": "unsupported", "evidence_refs": [],
    }
    report = build_auditory_report(
        tmp_path / "auditory_report.json",
        source_name="t.wav", case_id="case-1", source_sha256="a" * 64,
        analysis_version="1.0", overall_status="OK", metrics={},
        findings=[finding], evidence_index={}, summary="s",
    )
    assert report["overall_status"] == "PARTIAL"
    assert report["unresolved_evidence_findings"] == ["FAKE_BLOCKING"]


def test_evidence_refs_resolve_to_index(tmp_path):
    finding = {
        "code": "X", "severity": "BLOCKING", "message": "m",
        "evidence_refs": ["metrics.json", "scan_manifest.json"],
    }
    report = build_auditory_report(
        tmp_path / "auditory_report.json",
        source_name="t.wav", case_id="case-2", source_sha256="b" * 64,
        analysis_version="1.0", overall_status="OK", metrics={},
        findings=[finding],
        evidence_index={"metrics.json": "sha256:abc", "scan_manifest.json": "sha256:def"},
        summary="s",
    )
    for ref in finding["evidence_refs"]:
        assert ref in report["evidence_index"]


def test_missing_named_evidence_marks_report_partial(tmp_path):
    finding = {
        "code": "X", "severity": "BLOCKING", "message": "m",
        "evidence_refs": ["missing.json"],
    }
    report = build_auditory_report(
        tmp_path / "auditory_report.json",
        source_name="t.wav", case_id="case-missing", source_sha256="c" * 64,
        analysis_version="1.0", overall_status="OK", metrics={},
        findings=[finding], evidence_index={}, summary="s",
    )
    assert report["overall_status"] == "PARTIAL"
    assert report["unresolved_evidence_details"] == [
        {"code": "X", "missing_refs": ["missing.json"]}
    ]


def test_unmeasured_sections_never_fabricate_pass(tmp_path):
    report = build_auditory_report(
        tmp_path / "auditory_report.json",
        source_name="t.wav", case_id="case-empty", source_sha256="d" * 64,
        analysis_version="1.0", overall_status="OK", metrics={}, findings=[],
        evidence_index={}, summary="s",
    )
    assert report["overall_status"] == "PARTIAL"
    assert set(report["sections"].values()) == {"UNKNOWN"}


def test_judge_does_not_fabricate_positive_judgment(sample_delta, before_metrics, after_metrics):
    flags = evaluate_risk_flags(sample_delta, before_metrics, after_metrics)
    j = judge(sample_delta, before_metrics, after_metrics, plan=None, risk_flags=flags)
    assert isinstance(j, Judgment)
    assert j.workflow_decision in {"REJECT_TECHNICAL", "INCONCLUSIVE"}
    assert not j.artistic_approval_granted


# --- F. Regression ---------------------------------------------------------


def test_cli_v2_entry_contract():
    """CLI v2 是规范入口；JSON 契约文件存在。"""
    contract = CORE_PACKAGE_ROOT.parents[0] / "docs" / "architecture" / "CLI_V2_COMMAND_CONTRACT.md"
    assert contract.exists(), "CLI v2 contract doc must be preserved"
