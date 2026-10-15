from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from moodify.contracts.commercial_music import (
    ApprovalRecord,
    CandidateTrack,
    HumanDecision,
    JudgeConclusion,
    JudgeRecord,
    RightsConclusion,
    RightsRecord,
    derive_delivery_readiness,
)


NOW = datetime(2026, 10, 8, tzinfo=timezone.utc)
DIGEST = "sha256:" + "a" * 64


def candidate() -> CandidateTrack:
    return CandidateTrack(
        candidate_id="candidate-01",
        cue_id="cue-01",
        source_provider="Suno",
        source_sha256=DIGEST,
        ingested_at=NOW,
    )


def rights(conclusion: RightsConclusion = RightsConclusion.HUMAN_VERIFIED) -> RightsRecord:
    values = dict(
        candidate_id="candidate-01",
        conclusion=conclusion,
        lyrics_source="INTERNAL",
    )
    if conclusion == RightsConclusion.HUMAN_VERIFIED:
        values.update(
            provider_terms_ref="terms/suno/2026-09-03",
            evidence_refs=("evidence/download-receipt.json",),
            reviewed_by="rights-owner",
            reviewed_at=NOW,
        )
    return RightsRecord(**values)


def judge(phase: str, conclusion: JudgeConclusion) -> JudgeRecord:
    return JudgeRecord(
        candidate_id="candidate-01",
        phase=phase,
        conclusion=conclusion,
        judge_version="rules-1.1-uncalibrated",
        evidence_refs=(f"evidence/judge-{phase.lower()}.json",),
    )


def approval(decision: HumanDecision = HumanDecision.APPROVED) -> ApprovalRecord:
    return ApprovalRecord(
        candidate_id="candidate-01",
        decision=decision,
        reviewer="music-director",
        reviewed_at=NOW,
        evidence_refs=("reviews/director-approval.json",),
    )


def test_delivery_requires_rights_two_judges_and_human_approval():
    result = derive_delivery_readiness(
        candidate(),
        rights(),
        judge("BEFORE", JudgeConclusion.HUMAN_REQUIRED),
        judge("AFTER", JudgeConclusion.ACCEPT),
        approval(),
    )
    assert result.ready is True
    assert result.blockers == ()


def test_incomplete_rights_and_retry_are_hard_blockers():
    result = derive_delivery_readiness(
        candidate(),
        rights(RightsConclusion.INCOMPLETE),
        judge("BEFORE", JudgeConclusion.HUMAN_REQUIRED),
        judge("AFTER", JudgeConclusion.RETRY),
        approval(HumanDecision.REVISION_NEEDED),
    )
    assert result.ready is False
    assert result.blockers == (
        "RIGHTS_NOT_HUMAN_VERIFIED",
        "JUDGE_AFTER_RETRY",
        "HUMAN_APPROVAL_MISSING",
    )


def test_rights_cannot_claim_verified_without_human_and_evidence():
    with pytest.raises(ValidationError, match="HUMAN_VERIFIED rights require"):
        RightsRecord(
            candidate_id="candidate-01",
            conclusion=RightsConclusion.HUMAN_VERIFIED,
            lyrics_source="INTERNAL",
        )


def test_candidate_records_source_digest():
    assert candidate().model_dump()["schema"] == "moodify.commercial.candidate/0.1"
    with pytest.raises(ValidationError):
        CandidateTrack(
            candidate_id="candidate-01",
            cue_id="cue-01",
            source_provider="Suno",
            source_sha256="not-a-digest",
            ingested_at=NOW,
        )


def test_cross_candidate_records_never_unlock_delivery():
    foreign = approval().model_copy(update={"candidate_id": "candidate-02"})
    result = derive_delivery_readiness(
        candidate(),
        rights(),
        judge("BEFORE", JudgeConclusion.ACCEPT),
        judge("AFTER", JudgeConclusion.ACCEPT),
        foreign,
    )
    assert result.ready is False
    assert "CANDIDATE_ID_MISMATCH" in result.blockers
