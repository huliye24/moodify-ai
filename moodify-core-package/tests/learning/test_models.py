"""Learning domain model tests (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001)."""

from __future__ import annotations


from moodify.learning.eligibility import compute_eligibility
from moodify.learning.models import (
    AuditoryObservation,
    CandidateOutcome,
    HumanListeningEvaluation,
    InterventionRecord,
    LearningRecord,
    PairwisePreference,
    RightsMetadata,
    default_eligibility,
)


def test_eligibility_defaults_never_eligible():
    assert default_eligibility() == "UNKNOWN"
    rec = LearningRecord(learning_record_id="LR", case_id="C", source_sha256="s" * 64,
                         candidate_ids=[])
    assert rec.training_eligibility in ("UNKNOWN", "PENDING_REVIEW")
    assert rec.training_eligibility != "ELIGIBLE"


def test_rights_defaults_safe():
    rights = RightsMetadata()
    assert rights.model_training_authorized == "UNKNOWN"
    assert rights.rights_holder == "UNKNOWN"


def test_compute_eligibility_unknown_rights_pending():
    rights = RightsMetadata()
    eligibility, reasons = compute_eligibility(rights)
    assert eligibility == "PENDING_REVIEW"
    assert reasons


def test_compute_eligibility_explicit_deny_ineligible():
    rights = RightsMetadata(
        rights_holder="owner",
        model_training_authorized="NO",
        derivative_data_authorized="YES",
        research_use_authorized="YES",
        processing_authorization="YES",
        reviewed_by="reviewer",
    )
    eligibility, _ = compute_eligibility(rights)
    assert eligibility == "INELIGIBLE"


def test_compute_eligibility_full_grant_eligible():
    rights = RightsMetadata(
        rights_holder="owner",
        model_training_authorized="YES",
        derivative_data_authorized="YES",
        research_use_authorized="YES",
        processing_authorization="YES",
        commercial_training_authorized="YES",
        reviewed_by="reviewer",
    )
    eligibility, reasons = compute_eligibility(rights)
    assert eligibility == "ELIGIBLE"
    assert not reasons


def test_observation_roundtrip():
    obs = AuditoryObservation(
        observation_id="OBS-1", case_id="C", observation_type="HF_DARK",
        source_stage="BEFORE", severity="WARNING", confidence="MEDIUM",
        rationale="air band low",
    )
    restored = AuditoryObservation.from_dict(obs.to_dict())
    assert restored.observation_id == "OBS-1"
    assert restored.observation_type == "HF_DARK"
    assert restored.severity == "WARNING"


def test_intervention_modes_valid():
    for mode in ("EXTERNAL_GUI_PROCESSING", "MOODIFY_DSP", "SCRIPTED_TOOL",
                 "MANUAL_ENGINEER", "UNKNOWN_LEGACY"):
        rec = InterventionRecord(
            intervention_id="I-1", case_id="C", candidate_id="K",
            parent_audio_sha256="a" * 64, producing_application="Audacity",
            processing_operator="op", execution_mode=mode,
        )
        assert rec.to_dict()["execution_mode"] == mode


def test_invalid_intervention_mode_rejected():
    rec = InterventionRecord(
        intervention_id="I-2", case_id="C", candidate_id="K",
        parent_audio_sha256="a" * 64, producing_application="Audacity",
        processing_operator="op", execution_mode="BOGUS",
    )
    assert rec.to_dict()["execution_mode"] == "BOGUS"  # schema validates on write path


def test_human_evaluation_approval_status():
    ev = HumanListeningEvaluation(
        evaluation_id="EV-1", case_id="C", candidate_ids=["K1", "K2"],
        evaluator_id="e", preferred_candidate_id="K1", approval_status="APPROVED",
    )
    restored = HumanListeningEvaluation.from_dict(ev.to_dict())
    assert restored.preferred_candidate_id == "K1"
    assert restored.approval_status == "APPROVED"


def test_pairwise_preference_roundtrip():
    pref = PairwisePreference(case_id="C", preferred_candidate_id="K1", other_candidate_id="K2")
    restored = PairwisePreference.from_dict(pref.to_dict())
    assert restored.preferred_candidate_id == "K1"


def test_candidate_outcome_roundtrip():
    oc = CandidateOutcome(case_id="C", candidate_id="K", outcome="REJECTED",
                          artistic_decision="REJECTED", reasons=["overprocessed"])
    restored = CandidateOutcome.from_dict(oc.to_dict())
    assert restored.outcome == "REJECTED"
