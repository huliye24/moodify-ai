"""Capability Registry 0.1 — IDs, declarations, validation and discovery.

The registry is the canonical answer to "what can Moodify do?". These tests
protect the properties that make that answer trustworthy:

* an ID cannot smuggle in a provider name or a version;
* a declaration set cannot be internally inconsistent;
* the snapshot is deterministic enough to hash;
* a status reflects repository reality, not a filename.

Deliberately *not* tested: the exact classification of every capability. That
is a judgement with a justification in ``notes``, and pinning each one here
would turn a re-classification into a false failure. Only the load-bearing
classifications are asserted.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from moodify.capabilities import (
    CAPABILITY_SCHEMA,
    RETRYABLE_FAILURE_CODES,
    Capability,
    CapabilityNotFound,
    CapabilityRegistry,
    CapabilityStatus,
    CommercialUse,
    Determinism,
    ExecutionMode,
    Failure,
    FailureCode,
    IOType,
    Locality,
    Provider,
    ProviderNotFound,
    ProviderStatus,
    ProviderType,
    Redistribution,
    RegistryValidationError,
    StrategicPosture,
    builtin_registry,
    get_capability,
    get_provider,
    has_capability,
    is_retryable,
    list_capabilities,
    list_providers,
    providers_for,
    registry_snapshot,
    registry_snapshot_json,
    validate_capability_id,
    validate_provider_id,
)

PROVIDER_A = "prov.alpha"


def _cap(capability_id: str, **overrides) -> Capability:
    payload = dict(
        capability_id=capability_id,
        title="T",
        description="D",
        domain=capability_id.split(".", 1)[0],
        status=CapabilityStatus.CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.REPORT,),
        failure_codes=(FailureCode.EXECUTION_FAILED,),
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
    )
    payload.update(overrides)
    return Capability(**payload)


def _prov(provider_id: str, capability_ids: tuple[str, ...], **overrides) -> Provider:
    payload = dict(
        provider_id=provider_id,
        name="P",
        provider_type=ProviderType.LIBRARY,
        capability_ids=capability_ids,
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license="MIT",
    )
    payload.update(overrides)
    return Provider(**payload)


# ── A. capability IDs ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "value",
    [
        "audio.decode",
        "audio.analyze",
        "stem.separate",
        "clipping.repair",
        "midi.transcribe",
        "structure.analyze",
        "delivery.export",
        "pitch.correct",
    ],
)
def test_valid_capability_ids(value):
    assert validate_capability_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "stem",
        "stem.",
        ".separate",
        "stem..separate",
        "stem.separate.extra",  # three segments
        "stem.separate.v1",  # version encoded in the ID
        "stem.v2",
        "Demucs.separate",  # provider name as domain
        "stem.Separate",  # not lowercase
        "2stem.separate",  # segment may not start with a digit
        "_stem.separate",  # segment may not start with an underscore
        "stem-separate",  # not dot-separated
        " stem.separate",
        "stem separate",
        "stem.separate ",
        "音频.分析",  # not ASCII
    ],
)
def test_malformed_capability_ids_are_rejected(value):
    with pytest.raises(ValueError):
        validate_capability_id(value)


@pytest.mark.parametrize("value", ["stem2.separate", "clipping2.repair", "a1.b2"])
def test_digits_after_the_first_character_are_allowed(value):
    """Only the *first* character of a segment is restricted."""
    assert validate_capability_id(value) == value


@pytest.mark.parametrize("value", ["demucs.run", "basic_pitch.run", "ffmpeg.convert"])
def test_provider_named_capabilities_are_wellformed_but_absent(value):
    """These parse — the rule they break is architectural, not syntactic.

    The registry simply does not declare them; the ID format cannot detect a
    vendor name. Recorded here so the boundary is explicit rather than
    implied.
    """
    assert validate_capability_id(value) == value
    assert not has_capability(value)


@pytest.mark.parametrize(
    "value", ["moodify.auditory", "lalal.cloud", "ffmpeg.system", "basic_pitch.local"]
)
def test_valid_provider_ids(value):
    assert validate_provider_id(value) == value


@pytest.mark.parametrize("value", ["cloud", "1lalal.cloud", "moodify..auditory", "moodify."])
def test_malformed_provider_ids_are_rejected(value):
    with pytest.raises(ValueError):
        validate_provider_id(value)


def test_domain_must_match_the_id_prefix():
    with pytest.raises(ValidationError):
        _cap("stem.separate", domain="audio")


def test_capability_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        _cap("audio.decode", surprise=True)


def test_capability_requires_input_and_output_types():
    with pytest.raises(ValidationError):
        _cap("audio.decode", input_types=())
    with pytest.raises(ValidationError):
        _cap("audio.decode", output_types=())


def test_capability_requires_a_failure_code():
    with pytest.raises(ValidationError):
        _cap("audio.decode", failure_codes=())


def test_capability_is_frozen():
    cap = _cap("audio.decode")
    with pytest.raises(ValidationError):
        cap.title = "changed"


# ── B. registry validation ────────────────────────────────────────────────


def test_duplicate_capability_id_is_rejected():
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry([_cap("audio.decode"), _cap("audio.decode")], [])
    assert "duplicate capability ID" in str(excinfo.value)


def test_duplicate_provider_id_is_rejected():
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry(
            [_cap("audio.decode")],
            [_prov(PROVIDER_A, ("audio.decode",)), _prov(PROVIDER_A, ("audio.decode",))],
        )
    assert "duplicate provider ID" in str(excinfo.value)


def test_capability_referencing_unknown_provider_is_rejected():
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry([_cap("audio.decode", provider_ids=(PROVIDER_A,))], [])
    assert "unknown provider" in str(excinfo.value)


def test_provider_referencing_unknown_capability_is_rejected():
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry([], [_prov(PROVIDER_A, ("audio.decode",))])
    assert "unknown capability" in str(excinfo.value)


def test_asymmetric_reference_is_rejected_when_capability_lists_only():
    """The capability claims a provider that does not claim it back.

    Both declarations are individually well-formed, so only the registry's
    cross-checking can catch this.
    """
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry(
            [_cap("audio.decode", provider_ids=(PROVIDER_A,)), _cap("audio.verify")],
            [_prov(PROVIDER_A, ("audio.verify",))],
        )
    assert "does not declare" in str(excinfo.value)


def test_asymmetric_reference_is_rejected_when_provider_lists_only():
    with pytest.raises(RegistryValidationError) as excinfo:
        CapabilityRegistry(
            [_cap("audio.decode")],
            [_prov(PROVIDER_A, ("audio.decode",))],
        )
    assert "does not declare" in str(excinfo.value)


def test_symmetric_references_are_accepted():
    registry = CapabilityRegistry(
        [_cap("audio.decode", provider_ids=(PROVIDER_A,))],
        [_prov(PROVIDER_A, ("audio.decode",))],
    )
    assert registry.providers_for("audio.decode")[0].provider_id == PROVIDER_A


def test_duplicate_list_entries_are_rejected():
    with pytest.raises(ValidationError):
        _cap("audio.decode", failure_codes=(FailureCode.EXECUTION_FAILED,) * 2)
    with pytest.raises(ValidationError):
        _prov(PROVIDER_A, ("audio.decode", "audio.decode"))


# ── C. query API ──────────────────────────────────────────────────────────


def test_get_capability_returns_the_declaration():
    assert get_capability("stem.separate").capability_id == "stem.separate"


def test_get_capability_raises_for_unknown():
    with pytest.raises(CapabilityNotFound):
        get_capability("nope.nothing")


def test_not_found_is_a_key_error():
    """So callers can use dict-style defensive access."""
    assert issubclass(CapabilityNotFound, KeyError)
    assert issubclass(ProviderNotFound, KeyError)


def test_has_capability_never_raises():
    assert has_capability("stem.separate") is True
    assert has_capability("nope.nothing") is False
    assert has_capability(None) is False
    assert has_capability(123) is False


def test_get_provider_and_not_found():
    assert get_provider("ffmpeg.system").provider_id == "ffmpeg.system"
    with pytest.raises(ProviderNotFound):
        get_provider("nope.nothing")


def test_providers_for_returns_sorted_providers():
    names = [p.provider_id for p in providers_for("stem.separate")]
    assert names == sorted(names)
    assert "lalal.cloud" in names


def test_providers_for_unknown_capability_raises():
    """Undeclared is a different answer from declared-with-no-provider."""
    with pytest.raises(CapabilityNotFound):
        providers_for("nope.nothing")


def test_providers_for_declared_capability_with_no_provider_is_empty():
    assert providers_for("lyrics.align") == ()


def test_list_capabilities_is_sorted_and_filterable():
    everything = list_capabilities()
    ids = [c.capability_id for c in everything]
    assert ids == sorted(ids)

    canonical = list_capabilities(status=CapabilityStatus.CANONICAL)
    assert canonical
    assert all(c.status is CapabilityStatus.CANONICAL for c in canonical)

    audio = list_capabilities(domain="audio")
    assert audio
    assert all(c.domain == "audio" for c in audio)
    assert len(audio) <= len(everything)


def test_filters_combine():
    both = list_capabilities(status=CapabilityStatus.CANONICAL, domain="audio")
    assert all(c.status is CapabilityStatus.CANONICAL and c.domain == "audio" for c in both)


def test_list_providers_is_sorted_and_filterable():
    ids = [p.provider_id for p in list_providers()]
    assert ids == sorted(ids)
    assert all(
        p.status is ProviderStatus.EXPERIMENTAL
        for p in list_providers(status=ProviderStatus.EXPERIMENTAL)
    )


# ── D. snapshot ───────────────────────────────────────────────────────────


def test_snapshot_schema():
    assert registry_snapshot()["schema"] == CAPABILITY_SCHEMA == "moodify.capabilities/0.1"


def test_snapshot_is_deterministic():
    assert registry_snapshot_json() == registry_snapshot_json()


def test_snapshot_is_json_serializable_and_sorted():
    snapshot = registry_snapshot()
    json.dumps(snapshot)  # must not raise
    caps = [c["capability_id"] for c in snapshot["capabilities"]]
    provs = [p["provider_id"] for p in snapshot["providers"]]
    assert caps == sorted(caps)
    assert provs == sorted(provs)


def test_snapshot_covers_every_declaration():
    snapshot = registry_snapshot()
    assert len(snapshot["capabilities"]) == len(list_capabilities())
    assert len(snapshot["providers"]) == len(list_providers())


def test_snapshot_separates_code_and_weights_licenses():
    by_id = {p["provider_id"]: p for p in registry_snapshot()["providers"]}
    assert "code_license" in by_id["ffmpeg.system"]
    assert "weights_license" in by_id["ffmpeg.system"]


# ── E. failure vocabulary ─────────────────────────────────────────────────


REQUIRED_FAILURE_CODES = {
    "DEPENDENCY_MISSING",
    "PROVIDER_UNAVAILABLE",
    "INVALID_INPUT",
    "UNSUPPORTED_FORMAT",
    "RESOURCE_LIMIT",
    "AUTH_REQUIRED",
    "RATE_LIMITED",
    "EXECUTION_FAILED",
    "QUALITY_GATE_FAILED",
    "REVIEW_REQUIRED",
    "NOT_IMPLEMENTED",
}


def test_vocabulary_contains_the_required_codes():
    assert REQUIRED_FAILURE_CODES <= {code.value for code in FailureCode}


def test_retryable_classification():
    assert is_retryable(FailureCode.RATE_LIMITED)
    assert is_retryable(FailureCode.TIMEOUT)
    # Deterministic properties of the request are not retryable.
    for code in (
        FailureCode.INVALID_INPUT,
        FailureCode.UNSUPPORTED_FORMAT,
        FailureCode.NOT_IMPLEMENTED,
        FailureCode.REVIEW_REQUIRED,
        FailureCode.DEPENDENCY_MISSING,
    ):
        assert not is_retryable(code), code


def test_failure_of_derives_retryable():
    assert Failure.of(FailureCode.RATE_LIMITED, "slow down").retryable is True
    assert Failure.of(FailureCode.INVALID_INPUT, "bad").retryable is False


def test_failure_requires_message_and_is_strict():
    with pytest.raises(ValidationError):
        Failure(code=FailureCode.EXECUTION_FAILED, message="   ", retryable=True)
    with pytest.raises(ValidationError):
        Failure(code=FailureCode.EXECUTION_FAILED, message="x", retryable=True, extra=1)


def test_failure_is_frozen():
    failure = Failure.of(FailureCode.EXECUTION_FAILED, "boom")
    with pytest.raises(ValidationError):
        failure.message = "changed"


def test_retryable_table_only_holds_known_codes():
    assert RETRYABLE_FAILURE_CODES <= set(FailureCode)


# ── F. license metadata ───────────────────────────────────────────────────


def test_weights_license_is_independent_of_code_license():
    """The domain's most common trap: permissive code, restrictive weights.

    Modelled on a real pattern found during ECOSYSTEM 001 research, where two
    widely-used engines ship permissive code over non-commercial weights.
    """
    trap = _prov(
        "trap.example",
        ("audio.decode",),
        code_license="MIT",
        weights_license="CC-BY-NC-SA-4.0",
        commercial_use=CommercialUse.RESTRICTED,
    )
    assert trap.code_license == "MIT"
    assert trap.weights_license == "CC-BY-NC-SA-4.0"
    assert trap.commercial_use is CommercialUse.RESTRICTED
    assert "code_license" in Provider.model_fields
    assert "weights_license" in Provider.model_fields


def test_a_real_provider_declares_both_license_kinds():
    basic_pitch = get_provider("basic_pitch.local")
    assert basic_pitch.code_license == "Apache-2.0"
    assert basic_pitch.weights_license == "Apache-2.0"


def test_provider_without_weights_may_declare_none():
    """A system binary is not the same as unverified weights."""
    assert get_provider("ffmpeg.system").weights_license is None
    assert get_provider("music21.local").weights_license is None


def test_unknown_is_an_explicit_allowed_state():
    assert CommercialUse.UNKNOWN in set(CommercialUse)
    assert Redistribution.UNKNOWN in set(Redistribution)
    assert get_provider("ffmpeg.system").redistribution is Redistribution.UNKNOWN


def test_restricted_commercial_use_is_visible():
    assert get_provider("lalal.cloud").commercial_use is CommercialUse.RESTRICTED


# ── G. repository-truth assertions (load-bearing only) ────────────────────


def test_analysis_is_canonical_and_defers_to_human_authority():
    analyze = get_capability("audio.analyze")
    assert analyze.status is CapabilityStatus.CANONICAL
    assert analyze.requires_human_review is True
    assert FailureCode.REVIEW_REQUIRED in analyze.failure_codes


def test_not_everything_defers_to_human_review():
    """If every capability required review, the flag would carry no signal."""
    assert any(not c.requires_human_review for c in list_capabilities())


def test_understanding_gaps_are_recorded_as_types_without_producers():
    """The audit's central finding, pinned so it cannot silently improve."""
    assert get_capability("structure.analyze").status is CapabilityStatus.PARTIAL
    assert get_capability("rhythm.analyze").status is CapabilityStatus.PARTIAL
    for capability_id in ("lyrics.align", "harmony.analyze", "instrument.identify"):
        assert get_capability(capability_id).status is CapabilityStatus.ABSENT


def test_stem_separation_is_experimental_with_two_paths():
    separate = get_capability("stem.separate")
    assert separate.status is CapabilityStatus.EXPERIMENTAL
    assert separate.locality is Locality.HYBRID
    assert len(separate.provider_ids) == 2


def test_absent_capabilities_have_no_provider():
    """Nothing may claim to implement a capability we declare non-existent."""
    for capability in list_capabilities():
        if capability.status is CapabilityStatus.ABSENT:
            assert capability.provider_ids == (), capability.capability_id


def test_absent_capabilities_declare_not_implemented():
    for capability in list_capabilities():
        if capability.status is CapabilityStatus.ABSENT:
            assert FailureCode.NOT_IMPLEMENTED in capability.failure_codes


def test_declared_failure_codes_are_from_the_vocabulary():
    for capability in list_capabilities():
        assert capability.failure_codes
        for code in capability.failure_codes:
            assert isinstance(code, FailureCode)


# ── H. no execution, no discovery ─────────────────────────────────────────


def test_registry_exposes_no_execution_surface():
    """Metadata only: no execute, no router, no dynamic import."""
    registry = builtin_registry()
    for forbidden in ("execute", "run", "route", "invoke", "install", "register"):
        assert not hasattr(registry, forbidden), forbidden


def test_capability_ids_are_unique_and_seeded():
    ids = [c.capability_id for c in list_capabilities()]
    assert len(ids) == len(set(ids))
    assert 15 <= len(ids) <= 50
