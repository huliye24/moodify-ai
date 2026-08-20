"""Selection decision tests (MFY-CR-P08)."""

from __future__ import annotations

from types import SimpleNamespace

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    FindingStatus,
)
from moodify.reconstruction_job.contract import JobStatus
from moodify.reconstruction_job.selection import select_result


def _finding(category, confidence, requires_human=False):
    return SimpleNamespace(
        finding_id="f1", category=category,
        status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
        confidence=confidence, requires_human_review=requires_human,
        reasoning_summary="", measurement_refs=(), known_ambiguities=(),
    )


def _candidate(cid, gates=(), state="PASS", auto=True):
    return cid, {"path": f"{cid}.wav", "sha256": "x", "metrics": {},
                 "gates": list(gates), "plan_hash": f"plan-{cid}", "intensity": 0.2}


def _pipeline(candidates, ranking, diagnostics=()):
    """Build a PipelineResult-like object; plans mirror diagnostics refs
    (MEDIUM confidence findings enter objective refs -> human review)."""
    plans = [{"candidate_id": "SOURCE", "objective_refs": []}]
    if diagnostics:
        refs = [f"{d.category.value}:{d.status.value}:{d.confidence.value if d.confidence else '-'}"
                for d in diagnostics]
        for cid in ("A", "B", "C"):
            plans.append({"candidate_id": cid, "objective_refs": refs})
    return SimpleNamespace(
        diagnostics=list(diagnostics),
        candidates=dict(candidates),
        ranking=list(ranking),
        identity={},
        plans=plans,
    )


def _rank(cid, auto):
    return {"candidate_id": cid, "auto_approvable": auto, "guard_state": "PASS"}


def test_auto_approvable_candidate_wins(lowpass_wav):
    cands = [_candidate("A"), _candidate("B")]
    result = _pipeline(cands, [_rank("A", True), _rank("B", True)])
    decision = select_result(result)
    assert decision.status == JobStatus.SUCCEEDED.value
    assert decision.selected_candidate == "A"
    assert decision.plan_hash == "plan-A"


def test_hard_gate_failure_blocks_candidate():
    cands = [_candidate("A", gates=["NO_NEW_CLIPPING"]), _candidate("B")]
    result = _pipeline(cands, [_rank("A", True), _rank("B", True)])
    decision = select_result(result)
    assert decision.status == JobStatus.SUCCEEDED.value
    assert decision.selected_candidate == "B"


def test_all_candidates_blocked_yields_source_wins():
    cands = [_candidate("A", gates=["NO_NEW_CLIPPING"]), _candidate("B", gates=["DURATION_PRESERVED"])]
    result = _pipeline(cands, [_rank("A", True), _rank("B", True)])
    decision = select_result(result)
    assert decision.status == JobStatus.SOURCE_WINS.value
    assert decision.selected_candidate == "SOURCE"
    assert decision.identity_status == "SOURCE_PRESERVED"


def test_no_candidates_yields_source_wins():
    result = _pipeline([], [], diagnostics=[])
    decision = select_result(result)
    assert decision.status == JobStatus.SOURCE_WINS.value
    assert decision.selected_candidate == "SOURCE"


def test_identity_human_required_candidate_skipped_when_auto_exists():
    """A HUMAN_REQUIRED verdict disqualifies only that candidate; an
    auto-approvable candidate still wins (P05 semantics)."""
    cands = [_candidate("A"), _candidate("B")]
    pipeline = _pipeline(cands, [_rank("A", True), _rank("B", True)])
    pipeline.identity = {"B": {"state": "HUMAN_REQUIRED"}}
    decision = select_result(pipeline)
    assert decision.status == JobStatus.SUCCEEDED.value
    assert decision.selected_candidate == "A"


def test_identity_human_required_without_auto_stops():
    cands = [_candidate("A")]
    pipeline = _pipeline(cands, [_rank("A", False)], diagnostics=[])
    pipeline.identity = {"A": {"state": "HUMAN_REQUIRED"}}
    decision = select_result(pipeline)
    assert decision.status == JobStatus.HUMAN_REQUIRED.value
    assert decision.human_reasons


def test_medium_confidence_diagnostic_requires_human_even_with_auto():
    cands = [_candidate("A")]
    diagnostic = _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION, ConfidenceLevel.MEDIUM)
    result = _pipeline(cands, [_rank("A", True)], diagnostics=[diagnostic])
    decision = select_result(result)
    assert decision.status == JobStatus.HUMAN_REQUIRED.value
    assert decision.human_reasons


def test_high_confidence_diagnostic_does_not_block():
    cands = [_candidate("A")]
    diagnostic = _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION, ConfidenceLevel.HIGH)
    result = _pipeline(cands, [_rank("A", True)], diagnostics=[diagnostic])
    decision = select_result(result)
    assert decision.status == JobStatus.SUCCEEDED.value


def test_low_confidence_diagnostic_does_not_block():
    cands = [_candidate("A")]
    diagnostic = _finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION, ConfidenceLevel.LOW)
    result = _pipeline(cands, [_rank("A", True)], diagnostics=[diagnostic])
    decision = select_result(result)
    assert decision.status == JobStatus.SUCCEEDED.value
