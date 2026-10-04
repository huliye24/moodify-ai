"""Deterministic provider selection over declared metadata.

The router answers one question::

    Given a capability and a policy, which declared providers are eligible,
    why, and in what deterministic order?

It is a **pure decision layer**. It does not run providers, spawn
subprocesses, call APIs, load models, touch the network, or perform DSP. It
does not probe whether a provider's runtime exists on this machine — see
"Limitations" in ``docs/ecosystem/MOODIFY_PROVIDER_ROUTER_0_1.md``. It decides
from declared metadata only, and it never mutates the registry it reads.

The load-bearing rule::

    Policy filters truth first; preference only ranks what remains.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moodify.compat import StrEnum

from .builtin import builtin_registry
from .failures import FailureCode
from .models import (
    Capability,
    CapabilityStatus,
    CommercialUse,
    Determinism,
    ExecutionMode,
    Provider,
    ProviderStatus,
    Redistribution,
)
from .policy import DeterminismPolicy, LocalityPreference, PrivacyPolicy, ProviderPolicy
from .registry import CapabilityRegistry


class RoutingReason(StrEnum):
    """Why a routing decision came out the way it did.

    Deliberately **not** the execution failure vocabulary: "this provider was
    excluded by policy" and "this provider crashed" are different facts, and
    collapsing them would make routing unexplainable.
    """

    # ── rejections ────────────────────────────────────────────────────────
    CAPABILITY_NOT_SUPPORTED = "CAPABILITY_NOT_SUPPORTED"
    CAPABILITY_HAS_NO_PROVIDER = "CAPABILITY_HAS_NO_PROVIDER"
    NO_ELIGIBLE_PROVIDER = "NO_ELIGIBLE_PROVIDER"
    CAPABILITY_STATUS_REJECTED = "CAPABILITY_STATUS_REJECTED"
    PROVIDER_STATUS_REJECTED = "PROVIDER_STATUS_REJECTED"
    PRIVACY_POLICY_REJECTED = "PRIVACY_POLICY_REJECTED"
    DETERMINISM_POLICY_REJECTED = "DETERMINISM_POLICY_REJECTED"
    COMMERCIAL_USE_REJECTED = "COMMERCIAL_USE_REJECTED"
    REDISTRIBUTION_REJECTED = "REDISTRIBUTION_REJECTED"
    EXPLICITLY_EXCLUDED = "EXPLICITLY_EXCLUDED"

    # ── selection ─────────────────────────────────────────────────────────
    SINGLE_ELIGIBLE_PROVIDER = "SINGLE_ELIGIBLE_PROVIDER"
    PREFERRED_PROVIDER = "PREFERRED_PROVIDER"
    LOCALITY_PREFERRED = "LOCALITY_PREFERRED"
    DETERMINISM_PREFERRED = "DETERMINISM_PREFERRED"
    TIE_BREAKER = "TIE_BREAKER"


#: Provider statuses that require an explicit policy opt-in.
_STATUS_OPT_IN: dict[ProviderStatus, str] = {
    ProviderStatus.EXPERIMENTAL: "allow_experimental",
    ProviderStatus.CONNECTED_UNTESTED: "allow_connected_untested",
    ProviderStatus.DECLARED_ONLY: "allow_declared_only",
}

#: Provider statuses that no opt-in can select. ``UNAVAILABLE`` is declared
#: unobtainable and ``DEPRECATED`` is declared superseded; neither is a
#: question of caller preference.
_STATUS_NEVER_SELECTABLE = frozenset(
    {ProviderStatus.UNAVAILABLE, ProviderStatus.DEPRECATED}
)

#: Capability statuses no provider can make executable. A provider declaration
#: never overrides capability truth.
_CAPABILITY_NOT_ROUTABLE = frozenset(
    {CapabilityStatus.ABSENT, CapabilityStatus.DEFERRED}
)


class RejectedProvider(BaseModel):
    """A provider that did not survive policy, with every reason it failed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str
    reasons: tuple[RoutingReason, ...]


class ProviderSelection(BaseModel):
    """The router's full answer, including why it is that answer.

    Explainability is part of the product: a caller that gets an unexpected
    provider needs to know which constraint or preference produced it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    capability_id: str
    policy: ProviderPolicy
    selected_provider_id: str | None = None
    reason: RoutingReason | None = None
    """Explains the *outcome*: why this provider won, or why none could be
    selected. One field rather than two, because a selection and a refusal are
    alternatives, never both."""

    eligible_provider_ids: tuple[str, ...] = ()
    ranking: tuple[str, ...] = ()
    rejected_providers: tuple[RejectedProvider, ...] = ()
    failure: FailureCode | None = None

    @property
    def selected(self) -> bool:
        """Whether a provider was selected. Callers must check this."""
        return self.selected_provider_id is not None


def _rejections(
    capability: Capability,
    provider: Provider,
    policy: ProviderPolicy,
) -> tuple[RoutingReason, ...]:
    """Every hard constraint *provider* violates for *capability*."""
    reasons: list[RoutingReason] = []

    if provider.provider_id in policy.excluded_provider_ids:
        reasons.append(RoutingReason.EXPLICITLY_EXCLUDED)

    # Defensive: the registry already refuses asymmetric declarations, so this
    # cannot happen through the public API. Checked anyway because the router
    # must not depend on a property it does not itself verify.
    if capability.capability_id not in provider.capability_ids:
        reasons.append(RoutingReason.CAPABILITY_NOT_SUPPORTED)

    if provider.status in _STATUS_NEVER_SELECTABLE:
        reasons.append(RoutingReason.PROVIDER_STATUS_REJECTED)
    elif provider.status in _STATUS_OPT_IN:
        if not getattr(policy, _STATUS_OPT_IN[provider.status]):
            reasons.append(RoutingReason.PROVIDER_STATUS_REJECTED)

    if policy.privacy is PrivacyPolicy.LOCAL_ONLY:
        if provider.execution_mode is not ExecutionMode.LOCAL:
            reasons.append(RoutingReason.PRIVACY_POLICY_REJECTED)
    elif policy.privacy is PrivacyPolicy.NO_CLOUD:
        if provider.execution_mode is ExecutionMode.CLOUD:
            reasons.append(RoutingReason.PRIVACY_POLICY_REJECTED)

    if policy.determinism is DeterminismPolicy.REQUIRE_DETERMINISTIC:
        if provider.determinism is not Determinism.DETERMINISTIC:
            reasons.append(RoutingReason.DETERMINISM_POLICY_REJECTED)

    # An explicit positive requirement is not satisfied by UNKNOWN. Not
    # knowing whether we may use something is not permission to use it.
    if policy.commercial_use_required and provider.commercial_use is not CommercialUse.ALLOWED:
        reasons.append(RoutingReason.COMMERCIAL_USE_REJECTED)
    if policy.redistribution_required and provider.redistribution is not Redistribution.ALLOWED:
        reasons.append(RoutingReason.REDISTRIBUTION_REJECTED)

    return tuple(reasons)


def _ranking_key(provider: Provider, policy: ProviderPolicy) -> tuple:
    """Deterministic sort key. Lower sorts first.

    Composition, in priority order:

    1. explicit ``preferred_provider_ids``, in the order the caller listed them
    2. ``locality_preference``
    3. ``PREFER_DETERMINISTIC``
    4. ``provider_id`` lexical order — the documented final tie-break

    Only property 4 breaks genuine ties, and it is total, so the ranking is
    stable for any input. No randomness, no clock, no hash order.
    """
    if provider.provider_id in policy.preferred_provider_ids:
        preference = (0, policy.preferred_provider_ids.index(provider.provider_id))
    else:
        preference = (1, 0)

    locality = 1
    if policy.locality_preference is LocalityPreference.PREFER_LOCAL:
        locality = 0 if provider.execution_mode is ExecutionMode.LOCAL else 1
    elif policy.locality_preference is LocalityPreference.PREFER_CLOUD:
        locality = 0 if provider.execution_mode is ExecutionMode.CLOUD else 1

    determinism = 1
    if policy.determinism is DeterminismPolicy.PREFER_DETERMINISTIC:
        determinism = 0 if provider.determinism is Determinism.DETERMINISTIC else 1

    return (preference, locality, determinism, provider.provider_id)


def _selected_reason(winner: Provider, ranked: list[Provider], policy: ProviderPolicy) -> RoutingReason:
    """Why the winner outranked the rest — or that there was nothing to outrank."""
    if len(ranked) == 1:
        return RoutingReason.SINGLE_ELIGIBLE_PROVIDER
    if winner.provider_id in policy.preferred_provider_ids:
        return RoutingReason.PREFERRED_PROVIDER

    key = _ranking_key(winner, policy)
    for other in ranked:
        if other is winner:
            continue
        other_key = _ranking_key(other, policy)
        if other_key[:2] == key[:2] and other_key[2] != key[2]:
            return RoutingReason.DETERMINISM_PREFERRED
        if other_key[0] == key[0] and other_key[1] != key[1]:
            return RoutingReason.LOCALITY_PREFERRED
    return RoutingReason.TIE_BREAKER


def eligible_providers(
    capability_id: str,
    policy: ProviderPolicy | None = None,
    *,
    registry: CapabilityRegistry | None = None,
) -> tuple[Provider, ...]:
    """Providers satisfying every hard constraint, in declared-ID order.

    Raises :class:`~moodify.capabilities.registry.CapabilityNotFound` if the
    capability itself is undeclared — that is a caller error, not a routing
    outcome.
    """
    registry = registry or builtin_registry()
    policy = policy or ProviderPolicy()
    capability = registry.get_capability(capability_id)

    if capability.status in _CAPABILITY_NOT_ROUTABLE:
        return ()

    return tuple(
        provider
        for provider in registry.providers_for(capability_id)
        if not _rejections(capability, provider, policy)
    )


def rank_providers(
    capability_id: str,
    policy: ProviderPolicy | None = None,
    *,
    registry: CapabilityRegistry | None = None,
) -> tuple[Provider, ...]:
    """Eligible providers in deterministic preference order. Best first."""
    registry = registry or builtin_registry()
    policy = policy or ProviderPolicy()
    eligible = list(eligible_providers(capability_id, policy, registry=registry))
    eligible.sort(key=lambda provider: _ranking_key(provider, policy))
    return tuple(eligible)


def select_provider(
    capability_id: str,
    policy: ProviderPolicy | None = None,
    *,
    registry: CapabilityRegistry | None = None,
) -> ProviderSelection:
    """Select one provider, or explain why none could be selected.

    Never returns ``None`` and never raises for "nothing eligible" — that is a
    legitimate ecosystem outcome and the caller needs the rejection reasons.
    Check :attr:`ProviderSelection.selected`.
    """
    registry = registry or builtin_registry()
    policy = policy or ProviderPolicy()
    capability = registry.get_capability(capability_id)

    declared = list(registry.providers_for(capability_id))
    rejected: list[RejectedProvider] = []

    if capability.status in _CAPABILITY_NOT_ROUTABLE:
        rejected = [
            RejectedProvider(
                provider_id=provider.provider_id,
                reasons=(RoutingReason.CAPABILITY_STATUS_REJECTED,),
            )
            for provider in declared
        ]
    else:
        for provider in declared:
            reasons = _rejections(capability, provider, policy)
            if reasons:
                rejected.append(
                    RejectedProvider(provider_id=provider.provider_id, reasons=reasons)
                )

    ranked = list(
        rank_providers(capability_id, policy, registry=registry)
    )
    eligible_ids = tuple(provider.provider_id for provider in ranked)

    if not ranked:
        # Three distinct refusal outcomes, each stated explicitly rather than
        # collapsed into "nothing found". The reason names the *active*
        # blocker: a capability that no provider implements is a provider gap
        # even when it is also declared absent, and saying so is more useful
        # than blaming the status.
        if not declared:
            # A capability with no provider at all is a first-class ecosystem
            # gap, not registry corruption — the registry permits it
            # deliberately, and this is the honest report of it.
            reason = RoutingReason.CAPABILITY_HAS_NO_PROVIDER
        elif capability.status in _CAPABILITY_NOT_ROUTABLE:
            reason = RoutingReason.CAPABILITY_STATUS_REJECTED
        else:
            reason = RoutingReason.NO_ELIGIBLE_PROVIDER
        return ProviderSelection(
            capability_id=capability_id,
            policy=policy,
            selected_provider_id=None,
            reason=reason,
            eligible_provider_ids=(),
            ranking=(),
            rejected_providers=tuple(rejected),
            failure=FailureCode.PROVIDER_UNAVAILABLE,
        )

    winner = ranked[0]
    return ProviderSelection(
        capability_id=capability_id,
        policy=policy,
        selected_provider_id=winner.provider_id,
        reason=_selected_reason(winner, ranked, policy),
        eligible_provider_ids=eligible_ids,
        ranking=eligible_ids,
        rejected_providers=tuple(rejected),
        failure=None,
    )
