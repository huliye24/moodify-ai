"""Provider Router 0.1 — eligibility, ranking, selection, explainability.

The router is a decision layer over declared metadata. These tests protect the
properties that make the decision trustworthy:

* a hard constraint can never be outvoted by a preference;
* "declared" never silently becomes "runnable";
* the same registry + capability + policy always yields the same answer;
* a refusal explains itself rather than returning nothing.

Most cases use synthetic registries so the semantics are pinned independently
of what the built-in registry happens to declare today. Nothing here touches a
network, a provider, or the filesystem.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
from pydantic import ValidationError

from moodify.capabilities import (
    Capability,
    CapabilityNotFound,
    CapabilityRegistry,
    CapabilityStatus,
    CommercialUse,
    Determinism,
    DeterminismPolicy,
    ExecutionMode,
    FailureCode,
    IOType,
    Locality,
    LocalityPreference,
    PrivacyPolicy,
    Provider,
    ProviderPolicy,
    ProviderStatus,
    ProviderType,
    Redistribution,
    RoutingReason,
    StrategicPosture,
    eligible_providers,
    get_provider,
    rank_providers,
    registry_snapshot_json,
    select_provider,
)

CAP = "stem.separate"


def _cap(capability_id: str, *, status=CapabilityStatus.CANONICAL, provider_ids=(), **over):
    payload = dict(
        capability_id=capability_id,
        title="T",
        description="D",
        domain=capability_id.split(".", 1)[0],
        status=status,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.STEM,),
        failure_codes=(FailureCode.EXECUTION_FAILED,),
        provider_ids=tuple(provider_ids),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
    )
    payload.update(over)
    return Capability(**payload)


def _prov(provider_id: str, capability_ids, **over):
    payload = dict(
        provider_id=provider_id,
        name=provider_id,
        provider_type=ProviderType.LIBRARY,
        capability_ids=tuple(capability_ids),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license="MIT",
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        determinism=Determinism.DETERMINISTIC,
    )
    payload.update(over)
    return Provider(**payload)


def build(capability_id=CAP, *, cap_status=CapabilityStatus.CANONICAL, providers=()):
    """Wire a capability to the given providers, symmetrically."""
    ids = tuple(p.provider_id for p in providers)
    cap = _cap(capability_id, status=cap_status, provider_ids=ids)
    return CapabilityRegistry([cap], list(providers))


def one(provider_id="prov.alpha", **over):
    return build(providers=[_prov(provider_id, (CAP,), **over)])


# ── 1. the simple case ────────────────────────────────────────────────────


def test_selects_the_only_provider():
    result = select_provider(CAP, registry=one())
    assert result.selected is True
    assert result.selected_provider_id == "prov.alpha"
    assert result.reason is RoutingReason.SINGLE_ELIGIBLE_PROVIDER
    assert result.failure is None
    assert result.rejected_providers == ()


def test_select_provider_raises_for_undeclared_capability():
    """An undeclared capability is a caller error, not a routing outcome."""
    with pytest.raises(CapabilityNotFound):
        select_provider("nope.nothing", registry=one())


# ── 2. determinism ────────────────────────────────────────────────────────


def test_tie_break_is_lexical_and_deterministic():
    registry = build(
        providers=[
            _prov("zeta.one", (CAP,)),
            _prov("alpha.two", (CAP,)),
            _prov("mid.three", (CAP,)),
        ]
    )
    result = select_provider(CAP, registry=registry)
    assert result.selected_provider_id == "alpha.two"
    assert result.reason is RoutingReason.TIE_BREAKER
    assert result.ranking == ("alpha.two", "mid.three", "zeta.one")


def test_repeated_selection_is_identical():
    registry = build(providers=[_prov("b.two", (CAP,)), _prov("a.one", (CAP,))])
    first = select_provider(CAP, registry=registry)
    for _ in range(5):
        assert select_provider(CAP, registry=registry) == first


def test_ranking_is_stable_regardless_of_declaration_order():
    forward = build(providers=[_prov("a.one", (CAP,)), _prov("b.two", (CAP,))])
    reverse = build(providers=[_prov("b.two", (CAP,)), _prov("a.one", (CAP,))])
    assert rank_providers(CAP, registry=forward) == rank_providers(CAP, registry=reverse)


# ── 3/4. preference and exclusion ─────────────────────────────────────────


def test_preferred_provider_wins_among_eligible():
    registry = build(providers=[_prov("a.one", (CAP,)), _prov("b.two", (CAP,))])
    policy = ProviderPolicy(preferred_provider_ids=("b.two",))
    result = select_provider(CAP, policy, registry=registry)
    assert result.selected_provider_id == "b.two"
    assert result.reason is RoutingReason.PREFERRED_PROVIDER


def test_preference_respects_the_order_given():
    registry = build(
        providers=[_prov("a.one", (CAP,)), _prov("b.two", (CAP,)), _prov("c.three", (CAP,))]
    )
    policy = ProviderPolicy(preferred_provider_ids=("c.three", "b.two"))
    assert select_provider(CAP, policy, registry=registry).selected_provider_id == "c.three"


def test_exclusion_overrides_preference():
    registry = build(providers=[_prov("a.one", (CAP,)), _prov("b.two", (CAP,))])
    policy = ProviderPolicy(
        preferred_provider_ids=("b.two",), excluded_provider_ids=("b.two",)
    )
    result = select_provider(CAP, policy, registry=registry)
    assert result.selected_provider_id == "a.one"
    rejected = {r.provider_id: r.reasons for r in result.rejected_providers}
    assert rejected["b.two"] == (RoutingReason.EXPLICITLY_EXCLUDED,)


def test_preference_cannot_override_a_hard_constraint():
    """The §14 example: preferred, but policy still wins."""
    registry = build(
        providers=[
            _prov("cloud.one", (CAP,), execution_mode=ExecutionMode.CLOUD),
            _prov("local.two", (CAP,)),
        ]
    )
    policy = ProviderPolicy(
        privacy=PrivacyPolicy.LOCAL_ONLY, preferred_provider_ids=("cloud.one",)
    )
    result = select_provider(CAP, policy, registry=registry)
    assert result.selected_provider_id == "local.two"
    assert result.selected_provider_id != "cloud.one"


# ── 5. privacy / locality ─────────────────────────────────────────────────


def test_local_only_rejects_cloud():
    registry = build(providers=[_prov("cloud.one", (CAP,), execution_mode=ExecutionMode.CLOUD)])
    result = select_provider(CAP, ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY), registry=registry)
    assert result.selected is False
    assert result.rejected_providers[0].reasons == (RoutingReason.PRIVACY_POLICY_REJECTED,)


def test_local_only_also_rejects_external_apps():
    registry = build(
        providers=[_prov("daw.one", (CAP,), execution_mode=ExecutionMode.EXTERNAL_APP)]
    )
    result = select_provider(CAP, ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY), registry=registry)
    assert result.selected is False


def test_no_cloud_allows_a_local_external_app():
    """A DAW on this machine is not "the cloud" — the distinction is real."""
    registry = build(
        providers=[_prov("daw.one", (CAP,), execution_mode=ExecutionMode.EXTERNAL_APP)]
    )
    result = select_provider(CAP, ProviderPolicy(privacy=PrivacyPolicy.NO_CLOUD), registry=registry)
    assert result.selected_provider_id == "daw.one"


def test_no_cloud_rejects_cloud_but_keeps_local():
    registry = build(
        providers=[
            _prov("cloud.one", (CAP,), execution_mode=ExecutionMode.CLOUD),
            _prov("local.two", (CAP,)),
        ]
    )
    result = select_provider(CAP, ProviderPolicy(privacy=PrivacyPolicy.NO_CLOUD), registry=registry)
    assert result.selected_provider_id == "local.two"


def test_cloud_allowed_is_not_cloud_preferred():
    """No preference means no preference — not an implicit cloud nudge."""
    registry = build(
        providers=[
            _prov("a.local", (CAP,)),
            _prov("b.cloud", (CAP,), execution_mode=ExecutionMode.CLOUD),
        ]
    )
    result = select_provider(CAP, ProviderPolicy(), registry=registry)
    assert result.selected_provider_id == "a.local"  # lexical, not locality-driven


def test_locality_preference_is_soft_and_ranks_not_filters():
    registry = build(
        providers=[
            _prov("a.cloud", (CAP,), execution_mode=ExecutionMode.CLOUD),
            _prov("z.local", (CAP,)),
        ]
    )
    result = select_provider(CAP, ProviderPolicy(locality_preference=LocalityPreference.PREFER_LOCAL), registry=registry)
    assert result.selected_provider_id == "z.local"
    assert result.reason is RoutingReason.LOCALITY_PREFERRED


# ── 6/7. licence constraints ──────────────────────────────────────────────


def test_commercial_use_required_rejects_restricted():
    registry = build(providers=[_prov("a.one", (CAP,), commercial_use=CommercialUse.RESTRICTED)])
    result = select_provider(CAP, ProviderPolicy(commercial_use_required=True), registry=registry)
    assert result.selected is False
    assert result.rejected_providers[0].reasons == (RoutingReason.COMMERCIAL_USE_REJECTED,)


def test_commercial_use_required_rejects_unknown():
    """Not knowing is not permission."""
    registry = build(providers=[_prov("a.one", (CAP,), commercial_use=CommercialUse.UNKNOWN)])
    result = select_provider(CAP, ProviderPolicy(commercial_use_required=True), registry=registry)
    assert result.selected is False


def test_redistribution_required_rejects_unknown():
    registry = build(providers=[_prov("a.one", (CAP,), redistribution=Redistribution.UNKNOWN)])
    result = select_provider(CAP, ProviderPolicy(redistribution_required=True), registry=registry)
    assert result.selected is False
    assert result.rejected_providers[0].reasons == (RoutingReason.REDISTRIBUTION_REJECTED,)


def test_licence_requirement_is_off_by_default():
    registry = build(providers=[_prov("a.one", (CAP,), commercial_use=CommercialUse.RESTRICTED)])
    assert select_provider(CAP, registry=registry).selected is True


# ── 8. determinism policy ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "declared", [Determinism.UNKNOWN, Determinism.NONDETERMINISTIC, Determinism.CONDITIONALLY_DETERMINISTIC]
)
def test_require_deterministic_rejects_anything_less(declared):
    registry = build(providers=[_prov("a.one", (CAP,), determinism=declared)])
    result = select_provider(CAP, ProviderPolicy(determinism=DeterminismPolicy.REQUIRE_DETERMINISTIC), registry=registry)
    assert result.selected is False
    assert result.rejected_providers[0].reasons == (RoutingReason.DETERMINISM_POLICY_REJECTED,)


def test_prefer_deterministic_ranks_but_keeps_the_rest():
    registry = build(
        providers=[
            _prov("a.unknown", (CAP,), determinism=Determinism.UNKNOWN),
            _prov("z.det", (CAP,), determinism=Determinism.DETERMINISTIC),
        ]
    )
    result = select_provider(CAP, ProviderPolicy(determinism=DeterminismPolicy.PREFER_DETERMINISTIC), registry=registry)
    assert result.selected_provider_id == "z.det"
    assert result.reason is RoutingReason.DETERMINISM_PREFERRED
    assert set(result.eligible_provider_ids) == {"a.unknown", "z.det"}


def test_unknown_determinism_is_not_promoted_to_deterministic():
    registry = build(providers=[_prov("a.one", (CAP,), determinism=Determinism.UNKNOWN)])
    assert select_provider(CAP, registry=registry).selected is True
    assert get_provider("ffmpeg.system").determinism is Determinism.DETERMINISTIC


# ── 9/10/11. provider status gates ────────────────────────────────────────


@pytest.mark.parametrize(
    "status",
    [
        ProviderStatus.DECLARED_ONLY,
        ProviderStatus.CONNECTED_UNTESTED,
        ProviderStatus.EXPERIMENTAL,
    ],
)
def test_non_active_statuses_require_opt_in(status):
    registry = build(providers=[_prov("a.one", (CAP,), status=status)])
    result = select_provider(CAP, registry=registry)
    assert result.selected is False
    assert result.rejected_providers[0].reasons == (RoutingReason.PROVIDER_STATUS_REJECTED,)


def test_declared_only_opt_in_then_selects():
    registry = build(providers=[_prov("a.one", (CAP,), status=ProviderStatus.DECLARED_ONLY)])
    policy = ProviderPolicy(allow_declared_only=True)
    assert select_provider(CAP, policy, registry=registry).selected is True


def test_connected_untested_opt_in_then_selects():
    registry = build(providers=[_prov("a.one", (CAP,), status=ProviderStatus.CONNECTED_UNTESTED)])
    policy = ProviderPolicy(allow_connected_untested=True)
    assert select_provider(CAP, policy, registry=registry).selected is True


def test_experimental_opt_in_then_selects():
    registry = build(providers=[_prov("a.one", (CAP,), status=ProviderStatus.EXPERIMENTAL)])
    policy = ProviderPolicy(allow_experimental=True)
    assert select_provider(CAP, policy, registry=registry).selected is True


def test_opt_ins_are_independent():
    """Allowing experimental must not quietly allow unverified connectivity."""
    registry = build(providers=[_prov("a.one", (CAP,), status=ProviderStatus.CONNECTED_UNTESTED)])
    assert select_provider(CAP, ProviderPolicy(allow_experimental=True), registry=registry).selected is False


@pytest.mark.parametrize("status", [ProviderStatus.UNAVAILABLE, ProviderStatus.DEPRECATED])
def test_unavailable_and_deprecated_are_never_selectable(status):
    """No opt-in exists for these: the declaration says the provider is not a
    candidate, which is not a question of caller preference."""
    registry = build(providers=[_prov("a.one", (CAP,), status=status)])
    policy = ProviderPolicy(
        allow_experimental=True, allow_connected_untested=True, allow_declared_only=True
    )
    assert select_provider(CAP, policy, registry=registry).selected is False


# ── 10. capability status gates ───────────────────────────────────────────


@pytest.mark.parametrize("cap_status", [CapabilityStatus.ABSENT, CapabilityStatus.DEFERRED])
def test_non_routable_capability_status_wins_over_provider_metadata(cap_status):
    """A provider declaration must not make a non-existent capability executable."""
    registry = build(cap_status=cap_status, providers=[_prov("a.one", (CAP,))])
    result = select_provider(CAP, registry=registry)
    assert result.selected is False
    assert result.reason is RoutingReason.CAPABILITY_STATUS_REJECTED
    assert result.rejected_providers[0].reasons == (RoutingReason.CAPABILITY_STATUS_REJECTED,)


@pytest.mark.parametrize(
    "cap_status",
    [
        CapabilityStatus.CANONICAL,
        CapabilityStatus.IMPLEMENTED_NOT_CANONICAL,
        CapabilityStatus.PARTIAL,
        CapabilityStatus.EXPERIMENTAL,
        CapabilityStatus.LEGACY,
    ],
)
def test_routable_capability_statuses_are_not_blocked(cap_status):
    registry = build(cap_status=cap_status, providers=[_prov("a.one", (CAP,))])
    assert select_provider(CAP, registry=registry).selected is True


# ── 12/13. refusals ───────────────────────────────────────────────────────


def test_capability_with_zero_providers_is_an_honest_gap():
    registry = build(providers=[])
    result = select_provider(CAP, registry=registry)
    assert result.selected is False
    assert result.failure is FailureCode.PROVIDER_UNAVAILABLE
    assert result.reason is RoutingReason.CAPABILITY_HAS_NO_PROVIDER
    assert result.rejected_providers == ()


def test_all_providers_rejected_reports_the_reason():
    registry = build(
        providers=[
            _prov("cloud.one", (CAP,), execution_mode=ExecutionMode.CLOUD),
            _prov("cloud.two", (CAP,), execution_mode=ExecutionMode.CLOUD),
        ]
    )
    result = select_provider(CAP, ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY), registry=registry)
    assert result.selected is False
    assert result.failure is FailureCode.PROVIDER_UNAVAILABLE
    assert result.reason is RoutingReason.NO_ELIGIBLE_PROVIDER
    assert {r.provider_id for r in result.rejected_providers} == {"cloud.one", "cloud.two"}


def test_unavailable_failure_is_an_execution_vocabulary_code():
    """Routing refusal is reported in the shared failure vocabulary so callers
    have one thing to branch on, while routing *reasons* stay separate."""
    result = select_provider(CAP, registry=build(providers=[]))
    assert result.failure is FailureCode.PROVIDER_UNAVAILABLE


# ── 14/15. explainability ─────────────────────────────────────────────────


def test_result_carries_every_rejected_provider_with_reasons():
    registry = build(
        providers=[
            _prov("a.one", (CAP,), status=ProviderStatus.DECLARED_ONLY),
            _prov("b.two", (CAP,), execution_mode=ExecutionMode.CLOUD),
            _prov("c.three", (CAP,)),
        ]
    )
    policy = ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY, excluded_provider_ids=("c.three",))
    result = select_provider(CAP, policy, registry=registry)
    by_id = {r.provider_id: r.reasons for r in result.rejected_providers}
    assert RoutingReason.PROVIDER_STATUS_REJECTED in by_id["a.one"]
    assert RoutingReason.PRIVACY_POLICY_REJECTED in by_id["b.two"]
    assert by_id["c.three"] == (RoutingReason.EXPLICITLY_EXCLUDED,)
    assert result.selected is False


def test_rejected_provider_can_have_several_reasons():
    registry = build(
        providers=[
            _prov(
                "a.one",
                (CAP,),
                execution_mode=ExecutionMode.CLOUD,
                status=ProviderStatus.DECLARED_ONLY,
            )
        ]
    )
    policy = ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY)
    reason_set = set(select_provider(CAP, policy, registry=registry).rejected_providers[0].reasons)
    assert reason_set == {
        RoutingReason.PROVIDER_STATUS_REJECTED,
        RoutingReason.PRIVACY_POLICY_REJECTED,
    }


def test_result_echoes_the_policy_that_produced_it():
    policy = ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY)
    result = select_provider(CAP, policy, registry=one())
    assert result.policy == policy
    assert result.capability_id == CAP


# ── 16. purity ────────────────────────────────────────────────────────────


def test_selection_does_not_mutate_the_registry():
    before = registry_snapshot_json()
    registry = build(providers=[_prov("a.one", (CAP,)), _prov("b.two", (CAP,))])
    for policy in (
        ProviderPolicy(),
        ProviderPolicy(privacy=PrivacyPolicy.LOCAL_ONLY),
        ProviderPolicy(excluded_provider_ids=("a.one",)),
    ):
        select_provider(CAP, policy, registry=registry)
        eligible_providers(CAP, policy, registry=registry)
        rank_providers(CAP, policy, registry=registry)
    assert registry.snapshot_json() == registry.snapshot_json()
    assert registry_snapshot_json() == before


def test_policy_is_frozen_and_strict():
    policy = ProviderPolicy()
    with pytest.raises(ValidationError):
        policy.privacy = PrivacyPolicy.LOCAL_ONLY
    with pytest.raises(ValidationError):
        ProviderPolicy(surprise=True)


def test_policy_rejects_malformed_and_duplicate_provider_ids():
    with pytest.raises(ValidationError):
        ProviderPolicy(preferred_provider_ids=("NotAnID",))
    with pytest.raises(ValidationError):
        ProviderPolicy(excluded_provider_ids=("a.one", "a.one"))


# ── 32/33. no execution, no runtime imports ───────────────────────────────


def test_router_exposes_no_execution_surface():
    import moodify.capabilities.router as router

    for forbidden in ("execute", "run", "spawn", "invoke", "install", "probe", "ping"):
        assert not hasattr(router, forbidden), forbidden


def test_importing_the_router_pulls_no_engine():
    """Fresh interpreter: importing the decision layer must not load an engine.

    ``httpx`` is included because an HTTP client in this import chain would be
    a proxy for provider execution leaking into the pure layer.
    """
    code = (
        "import sys; import moodify.capabilities.router;"
        "bad=[m for m in ('demucs','basic_pitch','music21','torch','tensorflow','httpx') "
        "if m in sys.modules];"
        "print(','.join(bad))"
    )
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)}
    completed = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == ""


# ── built-in registry integration ─────────────────────────────────────────


def test_default_policy_selects_nothing_for_preview_separation():
    """The shipped separator is EXPERIMENTAL — it must not become the silent
    production default merely because it is local and self-contained."""
    result = select_provider("stem.separate")
    assert result.selected is False
    assert result.failure is FailureCode.PROVIDER_UNAVAILABLE


def test_preview_separation_becomes_eligible_only_when_asked_for():
    result = select_provider("stem.separate", ProviderPolicy(allow_experimental=True))
    assert result.selected_provider_id == "moodify.preview_separation"


def test_local_only_plus_opt_in_excludes_the_cloud_path():
    policy = ProviderPolicy(
        privacy=PrivacyPolicy.LOCAL_ONLY,
        allow_experimental=True,
        allow_connected_untested=True,
    )
    result = select_provider("stem.separate", policy)
    assert result.selected_provider_id == "moodify.preview_separation"
    rejected = {r.provider_id: set(r.reasons) for r in result.rejected_providers}
    assert RoutingReason.PRIVACY_POLICY_REJECTED in rejected["lalal.cloud"]


def test_canonical_analysis_is_selectable_with_the_default_policy():
    result = select_provider("audio.analyze")
    assert result.selected_provider_id == "moodify.auditory"
    assert result.failure is None


def test_zero_provider_capability_in_the_builtin_registry():
    result = select_provider("lyrics.align")
    assert result.selected is False
    assert result.reason is RoutingReason.CAPABILITY_HAS_NO_PROVIDER
