import pytest

from moodify.auditory.net_gain import GainDimension, NetGainEvidence


def dimension(name, state):
    refs = () if state in {"NOT_MEASURED", "INCONCLUSIVE"} else (f"evidence:{name}",)
    return GainDimension(name=name, state=state, evidence_refs=refs)


def complete_dimensions(target="IMPROVED", identity="UNCHANGED", artifacts="UNCHANGED"):
    return (
        dimension("TARGET_GAIN", target),
        dimension("IDENTITY_PRESERVATION", identity),
        dimension("NEW_ARTIFACT_RISK", artifacts),
        dimension("LOUDNESS_BIAS", "UNCHANGED"),
        dimension("REPRODUCIBILITY", "UNCHANGED"),
    )


def evidence(dimensions=None, loudness_matched=True):
    return NetGainEvidence(
        schema_version="net-gain-evidence-v0.experimental",
        source_sha256="a" * 64,
        candidate_sha256="b" * 64,
        loudness_matched=loudness_matched,
        dimensions=dimensions or complete_dimensions(),
    )


def test_complete_positive_evidence_still_requires_human_judgment():
    result = evidence()
    assert result.evidence_complete is True
    assert result.workflow_recommendation == "HUMAN_REQUIRED"
    assert result.to_dict()["aggregate_score"] is None
    assert result.to_dict()["authority"] == "EVIDENCE_ONLY"


def test_unmatched_loudness_is_inconclusive():
    assert evidence(loudness_matched=False).workflow_recommendation == "INCONCLUSIVE"


def test_no_target_gain_keeps_original():
    assert evidence(complete_dimensions(target="UNCHANGED")).workflow_recommendation == "KEEP_ORIGINAL"


def test_new_artifact_keeps_original_and_identity_drift_escalates():
    assert evidence(complete_dimensions(artifacts="DEGRADED")).workflow_recommendation == "KEEP_ORIGINAL"
    assert evidence(complete_dimensions(identity="DEGRADED")).workflow_recommendation == "HUMAN_REQUIRED"


def test_missing_measurement_cannot_carry_invented_value():
    with pytest.raises(ValueError, match="cannot carry a value"):
        GainDimension(name="TARGET_GAIN", state="NOT_MEASURED", value=1.0)

