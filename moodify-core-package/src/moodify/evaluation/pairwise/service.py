"""Pairwise judge orchestration (DSK-MFY-PAIRWISE-JUDGE-001).

Candidates are analyzed independently through the canonical auditory scan
pipeline, compared dimension-by-dimension, and judged under a versioned
policy. All artifacts are persisted immutably under
`<case_root>/06_pairwise/`; preference data lands in the learning store and
machine-only labels are never marked training-eligible.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import load_scan_evidence, scan_audio
from moodify.evaluation.pairwise.dimensions import compare_dimensions
from moodify.evaluation.pairwise.models import (
    HumanPairwiseDecision,
    PairwiseCandidate,
    PairwiseComparison,
    PreferenceRecord,
)
from moodify.evaluation.pairwise.policy import DecisionPolicy, decide

PAIRWISE_DIR = "06_pairwise"
DEFAULT_PROFILE = "MFY-WSE-SCAN-PROFILE-001"


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _hash_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pairwise_judge(
    case_id: str,
    case_root: Path,
    candidate_a_path: Path,
    candidate_b_path: Path,
    profile_name: str = DEFAULT_PROFILE,
    policy: DecisionPolicy | None = None,
) -> dict[str, Any]:
    """Analyze both candidates independently, compare, judge, and persist."""
    a_path = Path(candidate_a_path).resolve()
    b_path = Path(candidate_b_path).resolve()
    for label, path in (("A", a_path), ("B", b_path)):
        if not path.is_file():
            raise FileNotFoundError(f"candidate {label} not found: {path}")

    policy = policy or DecisionPolicy()
    profile = get_profile(profile_name)
    pairwise_dir = case_root / PAIRWISE_DIR
    a_scan_dir = pairwise_dir / "candidate_a_scan"
    b_scan_dir = pairwise_dir / "candidate_b_scan"

    failures: list[str] = []
    try:
        scan_audio(case_id, "pairwise_a", a_path, a_scan_dir, profile=profile)
        evidence_a = load_scan_evidence(a_scan_dir, profile)
    except Exception as exc:
        failures.append(f"candidate_a:{type(exc).__name__}")
        evidence_a = None
    try:
        scan_audio(case_id, "pairwise_b", b_path, b_scan_dir, profile=profile)
        evidence_b = load_scan_evidence(b_scan_dir, profile)
    except Exception as exc:
        failures.append(f"candidate_b:{type(exc).__name__}")
        evidence_b = None

    if evidence_a is not None and evidence_b is not None:
        dimensions = compare_dimensions(evidence_a.metrics, evidence_b.metrics)
    else:
        dimensions = []

    judgment = decide(
        dimensions,
        policy,
        pairwise_case_id=case_id,
        analysis_failed=failures or None,
    )

    candidates = [
        PairwiseCandidate(
            candidate_id=f"cand-a-{uuid4().hex[:12]}",
            pairwise_case_id=case_id,
            label="A",
            source_audio_id=str(a_path),
            source_hash=_hash_file(a_path),
            analysis_dir=str(a_scan_dir) if evidence_a else "",
            analysis_run_id=evidence_a.case_id if evidence_a else "",
        ),
        PairwiseCandidate(
            candidate_id=f"cand-b-{uuid4().hex[:12]}",
            pairwise_case_id=case_id,
            label="B",
            source_audio_id=str(b_path),
            source_hash=_hash_file(b_path),
            analysis_dir=str(b_scan_dir) if evidence_b else "",
            analysis_run_id=evidence_b.case_id if evidence_b else "",
        ),
    ]
    comparison = PairwiseComparison(
        comparison_id=f"cmp-{uuid4().hex[:12]}",
        pairwise_case_id=case_id,
        comparison_version="1.0",
        dimension_results=tuple(dimensions),
        evidence_coverage=judgment.evidence_coverage,
    )

    pairwise_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(pairwise_dir / "candidates.json", {"candidates": [c.to_dict() for c in candidates]})
    _atomic_write(pairwise_dir / "comparison.json", comparison.to_dict())
    _atomic_write(pairwise_dir / "judgment.json", judgment.to_dict())
    _atomic_write(pairwise_dir / "policy.json", policy.to_dict())

    if not failures and judgment.outcome != "INCONCLUSIVE":
        _append_preference_record(
            case_root,
            PreferenceRecord(
                preference_record_id=f"pref-{uuid4().hex[:12]}",
                pairwise_case_id=case_id,
                preferred_candidate=judgment.outcome[0],
                label_source="MACHINE_ONLY",
                machine_outcome=judgment.outcome,
                machine_confidence=judgment.confidence_level,
                eligible_for_training=False,
            ),
        )

    return {
        "judgment_id": judgment.judgment_id,
        "pairwise_case_id": case_id,
        "outcome": judgment.outcome,
        "confidence_level": judgment.confidence_level,
        "winner_margin": judgment.winner_margin,
        "evidence_coverage": judgment.evidence_coverage,
        "top_reasons": list(judgment.top_reasons),
        "limitations": list(judgment.limitations),
        "dimension_results": [d.to_dict() for d in dimensions],
        "analysis_failed": failures,
        "judgment_dir": str(pairwise_dir),
    }


def record_human_decision(
    case_root: Path,
    pairwise_case_id: str,
    decision: str,
    machine_outcome: str,
    machine_confidence: str,
    override_reason: str = "",
) -> dict[str, Any]:
    """Persist a human confirmation/override as a first-class event."""
    if decision not in {"CONFIRM_MODEL", "CHOOSE_A", "CHOOSE_B", "UNDECIDED"}:
        raise ValueError(f"invalid human decision: {decision}")

    human = HumanPairwiseDecision(
        human_decision_id=f"hum-{uuid4().hex[:12]}",
        pairwise_case_id=pairwise_case_id,
        decision=decision,
        machine_outcome=machine_outcome,
        override_reason=override_reason,
    )
    pairwise_dir = case_root / PAIRWISE_DIR
    pairwise_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(pairwise_dir / "human_decision.json", human.to_dict())

    if decision == "CONFIRM_MODEL":
        preferred = machine_outcome[0] if machine_outcome in {"A_WINS", "B_WINS"} else None
        label_source = "HUMAN_CONFIRMED"
    elif decision == "CHOOSE_A":
        preferred, label_source = "A", "HUMAN_OVERRIDE"
    elif decision == "CHOOSE_B":
        preferred, label_source = "B", "HUMAN_OVERRIDE"
    else:
        preferred, label_source = None, "HUMAN_CONFIRMED"

    record = PreferenceRecord(
        preference_record_id=f"pref-{uuid4().hex[:12]}",
        pairwise_case_id=pairwise_case_id,
        preferred_candidate=preferred,
        label_source=label_source,
        machine_outcome=machine_outcome,
        machine_confidence=machine_confidence,
        eligible_for_training=preferred is not None,
    )
    _append_preference_record(case_root, record)
    return {"human_decision": human.to_dict(), "preference_record": record.to_dict()}


def _append_preference_record(case_root: Path, record: PreferenceRecord) -> None:
    from moodify.learning.models import PairwisePreference
    from moodify.learning.store import CaseLearningStore

    store = CaseLearningStore(case_root)
    store.append_preference(
        PairwisePreference(
            case_id=record.pairwise_case_id,
            preferred_candidate_id=record.preferred_candidate or "",
            other_candidate_id="",
            basis=record.label_source,
            evaluator_id="pairwise-judge",
            label_source=record.label_source,
            machine_outcome=record.machine_outcome,
            machine_confidence=record.machine_confidence,
            eligible_for_training=record.eligible_for_training,
        )
    )
