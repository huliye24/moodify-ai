import pytest

from moodify.auditory.hearing_state import (
    HearingObservation,
    HearingState,
    ProviderProvenance,
    ProviderRun,
)
from moodify.auditory.provider_catalog import get_candidate, production_eligible


def provenance(provider_id="muq"):
    return ProviderProvenance(
        provider_id=provider_id,
        provider_version="0.1",
        model_id="baseline",
        model_revision="sha256:test",
        code_license="MIT",
        weights_license="CC-BY-NC-4.0",
        commercial_use="RESTRICTED",
        source_uri="https://example.invalid/provider",
    )


def test_hearing_state_is_evidence_only_and_serializable():
    source = provenance()
    observation = HearingObservation(
        namespace="music_embedding.muq",
        value=[0.1, 0.2],
        evidence_kind="MODEL_INFERRED",
        confidence=None,
        provenance=source,
        limitations=("research baseline",),
    )
    state = HearingState(
        hearing_state_version="hear-v0.experimental",
        source_sha256="a" * 64,
        auditory_representation_ref="rep-1",
        provider_runs=(ProviderRun("MUSIC_REPRESENTATION", "AVAILABLE", source, (observation,)),),
    )

    payload = state.to_dict()
    assert payload["judge_ready"] is True
    assert payload["authority"] == "EVIDENCE_ONLY"
    assert payload["provider_runs"][0]["observations"][0]["evidence_kind"] == "MODEL_INFERRED"


def test_missing_capability_fails_readiness_without_inventing_values():
    state = HearingState(
        hearing_state_version="hear-v0.experimental",
        source_sha256="b" * 64,
        auditory_representation_ref="rep-2",
        provider_runs=(ProviderRun("SEMANTIC", "NOT_RUN", provenance("clap")),),
        missing_capabilities=("SEMANTIC",),
    )
    assert state.judge_ready is False


def test_available_run_requires_observation():
    with pytest.raises(ValueError, match="must contain observations"):
        ProviderRun("ACOUSTIC", "AVAILABLE", provenance("essentia"))


def test_catalog_is_fail_closed_for_production():
    assert get_candidate("muse").use_class == "EVALUATION_ONLY"
    assert production_eligible("laion-clap") is False

