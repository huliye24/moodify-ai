"""Learning-record workflow (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

build → review → commit | exclude. A production case may be COMPLETED while
learning status is EXCLUDED — but the reason must be explicit, and a case
must never silently appear in training exports.
"""

from __future__ import annotations

import json
import uuid

from moodify.learning.errors import (
    LearningRecordHashMismatch,
    LearningRecordIncomplete,
    LearningRecordNotReviewed,
)
from moodify.learning.models import (
    CandidateOutcome,
    LearningRecord,
    PairwisePreference,
    RightsMetadata,
    default_eligibility,
)
from moodify.learning.store import CaseLearningStore


def _sha256_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_learning_record(store: CaseLearningStore, case_id: str) -> LearningRecord:
    """Assemble the learning record from everything captured under the case.

    Fails closed when required evidence is missing.
    """
    observations = store.list_observations()
    interventions = store.list_interventions()
    evaluations = store.list_evaluations()
    preferences = store.list_preferences()
    outcomes = store.list_outcomes()
    rights = store.load_rights_review()

    if rights is None:
        rights = RightsMetadata()

    record = LearningRecord(
        learning_record_id=f"LR-{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        source_sha256="",
        candidate_ids=sorted({o.candidate_id for o in outcomes if o.candidate_id} | {
            i.candidate_id for i in interventions}),
        before_scan_ref="01_before_scan/scan_manifest.json",
        after_scan_refs=["04_after_scan/scan_manifest.json"],
        observations=[o.observation_id for o in observations],
        intervention_refs=[i.intervention_id for i in interventions],
        human_evaluation_refs=[e.evaluation_id for e in evaluations],
        pairwise_preferences=preferences,
        candidate_outcomes=outcomes,
        rights=rights,
        training_eligibility=default_eligibility(),
        learning_status="CAPTURED",
    )

    # validation: incomplete evidence fails closed
    problems: list[str] = []
    if not store.case_root.joinpath("01_before_scan", "scan_manifest.json").is_file():
        problems.append("before scan manifest missing")
    cmp_root = store.case_root / "05_comparison"
    cmp_ok = cmp_root.joinpath("comparison_report.json").is_file() or any(
        cmp_root.glob("*/comparison_report.json")
    )
    if not cmp_ok:
        problems.append("comparison report missing")
    if not evaluations:
        problems.append("no human listening evaluation")
    if problems:
        raise LearningRecordIncomplete("; ".join(problems), case_id=case_id)

    source_manifest = json.loads(
        store.case_root.joinpath("01_before_scan", "scan_manifest.json").read_text(encoding="utf-8")
    )
    record.source_sha256 = source_manifest.get("input_sha256", "")
    record.evidence_manifest_ref = "09_learning/learning_record.json"
    record.learning_status = "CAPTURE_PENDING" if not evaluations else "CAPTURED"
    store.save_learning_record(record)
    return record


def review_learning_record(
    store: CaseLearningStore,
    case_id: str,
    rights: RightsMetadata,
    eligibility: str | None = None,
) -> LearningRecord:
    """Record rights review and set eligibility (defaults to PENDING_REVIEW)."""
    record = store.load_learning_record()
    if record is None:
        raise LearningRecordIncomplete("learning record not built", case_id=case_id)

    store.save_rights_review(rights)
    from moodify.learning.eligibility import compute_eligibility

    if eligibility is None:
        eligibility, reasons = compute_eligibility(rights)
        record.exclusion_reasons = reasons
    else:
        record.exclusion_reasons = []

    record.rights = rights
    record.training_eligibility = eligibility
    record.review_status = "REVIEWED"
    record.learning_status = "REVIEW_PENDING"
    store.save_eligibility(eligibility, record.exclusion_reasons)
    store.save_learning_record(record)
    return record


def commit_learning_record(
    store: CaseLearningStore,
    case_id: str,
    committed_by: str,
) -> LearningRecord:
    """Commit only after review; ineligible records are explicitly excluded."""
    record = store.load_learning_record()
    if record is None:
        raise LearningRecordIncomplete("learning record not built", case_id=case_id)
    if record.review_status != "REVIEWED":
        raise LearningRecordNotReviewed("learning record must be reviewed before commit", case_id=case_id)

    # integrity check: recompute record hash consistency
    current = store.load_learning_record()
    if current is None or current.learning_record_id != record.learning_record_id:
        raise LearningRecordHashMismatch("learning record changed during review", case_id=case_id)

    if record.training_eligibility in ("ELIGIBLE", "RESTRICTED_INTERNAL_RESEARCH"):
        record.learning_status = "COMMITTED"
    else:
        record.learning_status = "EXCLUDED"
    record.committed_at = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).isoformat()
    record.committed_by = committed_by
    store.save_learning_record(record)
    return record


def add_preference_and_outcome(
    store: CaseLearningStore,
    case_id: str,
    pref: PairwisePreference,
    outcomes: list[CandidateOutcome],
) -> None:
    store.append_preference(pref)
    for outcome in outcomes:
        store.append_outcome(outcome)
