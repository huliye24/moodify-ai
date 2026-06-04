"""Tests for TIDAL-INTELLIGENCE-009 — evidence scoring, ranking, planning, gates, briefs (MHP-539~550)."""
import pytest
from moodify_runtime.tidal_intelligence import (
    EvidenceScore, TaskPriority, AdaptivePlan, GateDecision,
    MorningBrief, LoopCheckResult, CraftFeedbackSelection,
    SynthesizedEvidence,
    score_mrs_evidence, score_ct_evidence, score_runtime_evidence,
    score_listening_evidence, score_craft_evidence, score_all_evidence,
    rank_tasks, plan_adaptive_queue, decide_gate, generate_morning_brief,
    anti_loop_check, select_craft_operations, synthesize_mrs_ct,
    load_tidal_intelligence_config, run_intelligence_smoke,
)


class TestEvidenceScoring:
    """MHP-539"""

    def test_mrs_null_returns_zero(self):
        e = score_mrs_evidence(None)
        assert e.score == 0.0 and e.confidence == 0.0

    def test_mrs_high_accuracy(self):
        e = score_mrs_evidence({"gate_accuracy": 0.95, "over_dark_level": "none", "sample_count": 100})
        assert e.score > 0.7
        assert e.confidence == 1.0

    def test_mrs_over_dark_penalty(self):
        e = score_mrs_evidence({"gate_accuracy": 0.8, "over_dark_level": "severe", "sample_count": 50})
        assert e.weighted_score < 0.8

    def test_ct_null_returns_zero(self):
        e = score_ct_evidence(None)
        assert e.score == 0.0

    def test_ct_with_critical_issues(self):
        e = score_ct_evidence([{"severity": "critical", "issue": "over_dark"},
                                {"severity": "warn", "issue": "harshness"},
                                {"severity": "info", "issue": "ok"}])
        assert e.score < 0.5  # 2 issues out of 3

    def test_ct_clean(self):
        e = score_ct_evidence([{"severity": "info", "issue": "ok"}])
        assert e.score == 1.0

    def test_runtime_null_returns_zero(self):
        e = score_runtime_evidence(None)
        assert e.score == 0.0

    def test_runtime_healthy(self):
        e = score_runtime_evidence({"tasks_succeeded": 48, "tasks_processed": 50, "crashed": False})
        assert e.score > 0.8

    def test_runtime_crashed(self):
        e = score_runtime_evidence({"tasks_succeeded": 10, "tasks_processed": 50, "crashed": True})
        assert e.score < 0.5

    def test_listening_null_returns_zero(self):
        e = score_listening_evidence(None)
        assert e.score == 0.0

    def test_listening_high_agreement(self):
        e = score_listening_evidence({"reviewer_agreement": 0.9, "samples_reviewed": 30})
        assert e.weighted_score > 0.5

    def test_craft_null_returns_zero(self):
        e = score_craft_evidence(None)
        assert e.score == 0.0

    def test_craft_high_adoption(self):
        e = score_craft_evidence({"adopted_count": 25, "total_count": 30})
        assert e.score > 0.7

    def test_score_all_evidence_returns_five_sources(self):
        scores = score_all_evidence()
        assert len(scores) == 5
        assert {s.source for s in scores} == {"mrs", "ct", "runtime", "listening", "craft"}

    def test_score_all_sorted_by_weighted_score(self):
        scores = score_all_evidence(
            mrs={"gate_accuracy": 0.9, "over_dark_level": "none", "sample_count": 100},
            ct=[{"severity": "info"}],
            runtime={"tasks_succeeded": 48, "tasks_processed": 50, "crashed": False},
        )
        for i in range(len(scores) - 1):
            assert scores[i].weighted_score >= scores[i+1].weighted_score


class TestTaskPriority:
    """MHP-540"""

    def test_compute_basic(self):
        tp = TaskPriority(task_id="test", base_priority=0.5, value_score=0.6, urgency=0.7)
        p = tp.compute()
        assert 0 < p <= 1.0

    def test_compute_with_evidence_boost(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9)]
        tp = TaskPriority(task_id="test", base_priority=0.5, value_score=0.8, urgency=0.9)
        p = tp.compute(evidence)
        assert p > 0.5  # Should be boosted

    def test_risk_penalty_reduces_priority(self):
        tp_no_risk = TaskPriority(task_id="safe", base_priority=0.7, risk_penalty=0.0)
        tp_risk = TaskPriority(task_id="risky", base_priority=0.7, risk_penalty=0.5)
        assert tp_no_risk.compute() > tp_risk.compute()

    def test_rank_tasks_sorts_by_priority(self):
        tasks = [
            {"id": "low", "base_priority": 0.1, "value_score": 0.1, "urgency": 0.1},
            {"id": "high", "base_priority": 0.9, "value_score": 0.9, "urgency": 0.9},
        ]
        ranked = rank_tasks(tasks)
        assert ranked[0].task_id == "high"
        assert ranked[1].task_id == "low"

    def test_rank_tasks_respects_dependencies_metadata(self):
        tasks = [
            {"id": "A", "depends_on": ["B"]},
            {"id": "B", "depends_on": []},
        ]
        ranked = rank_tasks(tasks)
        # Both ranked, but planner should handle dependency order
        assert len(ranked) == 2


class TestAdaptivePlanner:
    """MHP-541"""

    def test_plan_fits_budget(self):
        tasks = [{"id": f"t{i}", "base_priority": 0.5, "estimated_cost_s": 200} for i in range(10)]
        plan = plan_adaptive_queue(tasks, budget_s=600)
        assert len(plan.tasks) <= 3  # 3*200 = 600

    def test_plan_respects_dependencies(self):
        tasks = [
            {"id": "A", "base_priority": 0.9, "depends_on": ["B"]},
            {"id": "B", "base_priority": 0.8, "depends_on": []},
        ]
        plan = plan_adaptive_queue(tasks)
        tids = [t.task_id for t in plan.tasks]
        # B must come before A (dependency ordering)
        if "A" in tids and "B" in tids:
            assert tids.index("B") < tids.index("A")

    def test_plan_dry_run_warns(self):
        plan = plan_adaptive_queue([], dry_run=True)
        assert any("DRY-RUN" in w for w in plan.warnings)


class TestGateDecision:
    """MHP-542"""

    def test_no_evidence_hold(self):
        g = decide_gate("test-target")
        assert g.decision == "HOLD"

    def test_all_strong_adopt(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9),
                     EvidenceScore(source="runtime", weight=1.0, score=0.9, confidence=0.9)]
        g = decide_gate("test", evidence, min_confidence=0.3)
        assert g.decision == "ADOPT"

    def test_mixed_evidence_pass(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9),
                     EvidenceScore(source="ct", weight=1.0, score=0.6, confidence=0.6)]
        g = decide_gate("test", evidence)
        assert g.decision in ("PASS", "ADOPT")

    def test_missing_required_source_holds(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9)]
        g = decide_gate("test", evidence, required_sources=["mrs", "runtime"])
        assert g.decision == "HOLD"

    def test_gate_report_generates_markdown(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9)]
        g = decide_gate("NEM-TEST", evidence)
        report = g.to_report()
        assert "NEM-TEST" in report
        assert "mrs" in report


class TestMorningBrief:
    """MHP-543"""

    def test_generates_brief(self):
        evidence = [EvidenceScore(source="mrs", weight=1.0, score=0.9, confidence=0.9)]
        ranked = [TaskPriority(task_id="T1", final_priority=0.85)]
        gate = GateDecision(gate_id="G1", target="N1", decision="PASS", confidence=0.8)
        brief = generate_morning_brief(
            [{"tasks_succeeded": 10, "tasks_processed": 10, "tasks_failed": 0, "errors": []}],
            ranked, [gate], evidence)
        assert brief.tasks_total == 10
        assert brief.tasks_succeeded == 10
        assert "mrs" in brief.evidence_health

    def test_brief_markdown_has_sections(self):
        brief = generate_morning_brief(
            [{"tasks_succeeded": 1, "tasks_processed": 1, "tasks_failed": 0, "errors": []}],
            ranked_tasks=[TaskPriority(task_id="T1", final_priority=0.9)])
        assert "Summary" in brief.raw_markdown
        assert "Top Priorities" in brief.raw_markdown

    def test_alerts_on_failures(self):
        brief = generate_morning_brief(
            [{"tasks_succeeded": 0, "tasks_processed": 5, "tasks_failed": 5,
              "errors": ["something broke"]}])
        assert len(brief.alerts) > 0
        assert len(brief.recommendations) > 0

    def test_to_dict_roundtrip(self):
        brief = generate_morning_brief([])
        d = brief.to_dict()
        assert d["tasks_total"] == 0
        assert isinstance(d["evidence_health"], dict)


class TestAntiLoop:
    """MHP-546"""

    def test_no_loop_detected(self):
        r = anti_loop_check([{"task_id": "A"}, {"task_id": "B"}, {"task_id": "C"}, {"task_id": "D"}])
        assert r.safe and not r.loop_detected

    def test_repeat_loop_detected(self):
        r = anti_loop_check([{"task_id": "A"}, {"task_id": "A"}, {"task_id": "A"}])
        assert not r.safe and r.loop_detected
        assert r.pattern == "repeat"

    def test_alternating_loop_detected(self):
        r = anti_loop_check([{"task_id": "A"}, {"task_id": "B"}, {"task_id": "A"}, {"task_id": "B"}])
        assert not r.safe and r.loop_detected
        assert r.pattern == "alternating"

    def test_failing_loop_detected(self):
        r = anti_loop_check([
            {"task_id": "A", "ok": False}, {"task_id": "A", "ok": False},
            {"task_id": "A", "ok": False}])
        assert not r.safe

    def test_short_history_safe(self):
        r = anti_loop_check([{"task_id": "A"}])
        assert r.safe and not r.loop_detected


class TestCraftFeedback:
    """MHP-547"""

    def test_selects_operations(self):
        sel = select_craft_operations(
            [{"severity": "warn", "issue": "over_dark"},
             {"severity": "info", "issue": "dynamics_flat"}])
        assert len(sel.selected_operations) > 0
        assert "input_normalize" in sel.selected_operations
        assert "silence_trim" in sel.selected_operations

    def test_respects_max_ops(self):
        sel = select_craft_operations(
            [{"severity": "warn", "issue": "over_dark"},
             {"severity": "warn", "issue": "over_bright"},
             {"severity": "warn", "issue": "narrow_stereo"},
             {"severity": "warn", "issue": "sibilance"},
             {"severity": "warn", "issue": "transient_damage"},
             {"severity": "warn", "issue": "harshness"}],
            max_ops=3)
        assert len(sel.selected_operations) <= 3

    def test_low_risk_ceiling(self):
        sel = select_craft_operations(
            [{"severity": "warn", "issue": "over_dark"}],
            max_risk="low")
        risky = {"overdark_fix", "transient_repair", "spectral_carve", "de_ess"}
        assert not any(op in risky for op in sel.selected_operations)

    def test_high_mrs_minimal_processing(self):
        sel = select_craft_operations(
            [{"severity": "info", "issue": "dynamics_flat"}],
            mrs_score=0.85)
        assert "minimal" in sel.justification.lower() or sel.risk_level == "low"


class TestMRSSynthesis:
    """MHP-548"""

    def test_both_agree(self):
        s = synthesize_mrs_ct(
            {"sample_id": "s1", "mrs_score": 0.8, "mrs_delta": 0.2, "over_dark_level": "none", "source": "cal"},
            [{"severity": "info"}])
        assert s.agreement_score > 0.5
        assert "good" in s.recommendation.lower()

    def test_mrs_good_ct_bad(self):
        s = synthesize_mrs_ct(
            {"sample_id": "s2", "mrs_score": 0.8, "mrs_delta": 0.1, "over_dark_level": "none", "source": "cal"},
            [{"severity": "critical"}, {"severity": "warn"}, {"severity": "warn"}])
        assert s.agreement_score < 0.5

    def test_both_bad(self):
        s = synthesize_mrs_ct(
            {"sample_id": "s3", "mrs_score": 0.2, "mrs_delta": -0.1, "over_dark_level": "severe", "source": "cal"},
            [{"severity": "critical"}, {"severity": "critical"}])
        assert s.agreement_score < 0.3
        assert "priority" in s.recommendation.lower()


class TestConfig:
    """MHP-549"""

    def test_default_profile(self):
        cfg = load_tidal_intelligence_config("default")
        assert cfg["min_evidence_confidence"] == 0.3
        assert cfg["max_concurrent_tasks"] == 3

    def test_conservative_profile(self):
        cfg = load_tidal_intelligence_config("conservative")
        assert cfg["min_evidence_confidence"] > cfg["max_concurrent_tasks"] / 10  # stricter

    def test_overnight_profile(self):
        cfg = load_tidal_intelligence_config("overnight")
        assert cfg["budget_s"] >= 3600  # long budget


class TestSmoke:
    """MHP-550"""

    def test_smoke_runs_and_passes(self):
        r = run_intelligence_smoke()
        assert r["smoke_ok"], f"Smoke failed: {r}"
        assert "mrs" in r["evidence_scores"]
        assert len(r["ranked"]) == 3
        assert r["gate"] in ("PASS", "ADOPT")
        assert r["anti_loop_safe"]
        assert len(r["craft_ops"]) > 0
