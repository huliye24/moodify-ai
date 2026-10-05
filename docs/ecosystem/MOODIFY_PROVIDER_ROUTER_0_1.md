# Moodify Provider Router 0.1

> **Status:** implemented — deterministic selection over declared metadata.
> **Code:** `moodify-core-package/src/moodify/capabilities/{router,policy}.py`
> **Date:** 2026-10-04
> **Depends on:** Capability Registry 0.1 (`moodify.capabilities/0.1`)
> **Companion to:** `MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md` (strategy), `MOODIFY_CAPABILITY_REGISTRY_0_1.md` (what exists)

---

## Purpose

The registry answers *what can Moodify do*. The router answers:

> Given a capability and a policy, which declared providers are eligible, why,
> and in what deterministic order?

It is a **pure decision layer**. It does not run providers, spawn subprocesses,
call APIs, load models, touch the network, download weights, or perform DSP.
It does not probe whether a provider's runtime actually exists on this machine
(see **Limitations**). It decides from declared metadata only, and it never
mutates the registry it reads.

---

## The load-bearing rule

```text
Policy filters truth first; preference only ranks what remains.
```

Everything below follows from that sentence.

---

## Hard constraints vs preferences

The distinction is the design. A **hard constraint eliminates** a provider and
can never be outvoted. A **soft preference only orders** whatever survives.

| Hard constraints (eliminate) | Soft preferences (rank) |
| --- | --- |
| `privacy` | `locality_preference` |
| `determinism = REQUIRE_DETERMINISTIC` | `determinism = PREFER_DETERMINISTIC` |
| `commercial_use_required` | `preferred_provider_ids` |
| `redistribution_required` | |
| `excluded_provider_ids` | |
| `allow_*` status opt-ins (their *absence* eliminates) | |
| provider status gate | |
| capability status gate | |

The consequence that matters:

```python
ProviderPolicy(privacy=LOCAL_ONLY, preferred_provider_ids=["lalal.cloud"])
```

**must not** select `lalal.cloud`. Preference is not authority to violate
policy, and a policy that can be silently overridden is not a policy.

---

## Policy fields

```python
ProviderPolicy(
    # hard
    privacy: PrivacyPolicy = ANY           # ANY | NO_CLOUD | LOCAL_ONLY
    determinism: DeterminismPolicy = ANY   # ANY | PREFER_DETERMINISTIC | REQUIRE_DETERMINISTIC
    commercial_use_required: bool = False
    redistribution_required: bool = False
    allow_experimental: bool = False
    allow_connected_untested: bool = False
    allow_declared_only: bool = False
    # soft
    locality_preference: LocalityPreference = ANY   # ANY | PREFER_LOCAL | PREFER_CLOUD
    preferred_provider_ids: tuple[str, ...] = ()
    # exclusion
    excluded_provider_ids: tuple[str, ...] = ()
)
```

**The default is deliberately conservative**: `ACTIVE` providers only, no
relaxations. Every relaxation must be asked for by name.

### `privacy` — the three values are not synonyms

| Value | Rejects | Rationale |
| --- | --- | --- |
| `ANY` | nothing | |
| `NO_CLOUD` | `execution_mode = CLOUD` | Work must not leave for a remote service. A **local application is fine** — a DAW on this machine is not "the cloud". |
| `LOCAL_ONLY` | `CLOUD` **and** `EXTERNAL_APP` | Work must run here. |

`NO_CLOUD` permitting `EXTERNAL_APP` is a real distinction, not an oversight:
"don't upload my audio" and "don't hand my audio to another program" are
different requests, and collapsing them would make the stronger one
unexpressible.

`privacy=ANY` is **not** `PREFER_CLOUD`. Cloud is never preferred implicitly.

### Soft preferences never eliminate

`locality_preference = PREFER_LOCAL` ranks local providers first but still
returns cloud providers behind them. Only `privacy` eliminates.

---

## Eligibility rules

A provider is eligible when it violates **no** hard constraint:

| Constraint | Rejection reason |
| --- | --- |
| listed in `excluded_provider_ids` | `EXPLICITLY_EXCLUDED` |
| does not declare the capability | `CAPABILITY_NOT_SUPPORTED` (defensive) |
| status `UNAVAILABLE` / `DEPRECATED` | `PROVIDER_STATUS_REJECTED` — **no opt-in exists** |
| status `EXPERIMENTAL` without `allow_experimental` | `PROVIDER_STATUS_REJECTED` |
| status `CONNECTED_UNTESTED` without `allow_connected_untested` | `PROVIDER_STATUS_REJECTED` |
| status `DECLARED_ONLY` without `allow_declared_only` | `PROVIDER_STATUS_REJECTED` |
| violates `privacy` | `PRIVACY_POLICY_REJECTED` |
| not `DETERMINISTIC` under `REQUIRE_DETERMINISTIC` | `DETERMINISM_POLICY_REJECTED` |
| `commercial_use != ALLOWED` when required | `COMMERCIAL_USE_REJECTED` |
| `redistribution != ALLOWED` when required | `REDISTRIBUTION_REJECTED` |

**An explicit positive requirement is never satisfied by `UNKNOWN`.** Not
knowing whether we may commercially use something is not permission to use it.

### Provider status semantics

```text
ACTIVE               eligible by default
EXPERIMENTAL         requires allow_experimental
CONNECTED_UNTESTED   requires allow_connected_untested
DECLARED_ONLY        requires allow_declared_only
UNAVAILABLE          never selectable
DEPRECATED           never selectable
```

`UNKNOWN` is not in that list because status is never `UNKNOWN` — the registry
requires an explicit status. But the same principle applies to the *metadata*
the router filters on: unknown determinism, unknown commercial use and unknown
redistribution are all treated as **not satisfying** an explicit requirement.

**`UNAVAILABLE` and `DEPRECATED` have no opt-in** because the declaration says
the provider is not a candidate. That is not a question of caller preference,
and offering a flag for it would make "the provider is gone" overridable.

### Capability status gate

A provider declaration **never** overrides capability truth.

```text
ABSENT / DEFERRED   → no provider can make it executable
everything else     → governed by the provider status gate
```

`LEGACY` is deliberately routable: the capability is real, merely not the
future direction.

> **Integrity note:** the registry's own construction rejects asymmetric
> capability/provider declarations, so "declarations disagree" cannot reach the
> router through the public API. The router still checks
> `CAPABILITY_NOT_SUPPORTED` defensively, because a decision layer must not
> depend on a property it does not itself verify.

---

## Ranking

Eligible providers are sorted by a single explicit tuple key:

```text
1. preferred_provider_ids, in the order the caller listed them
2. locality_preference
3. PREFER_DETERMINISTIC
4. provider_id — lexical order, the documented final tie-break
```

Only step 4 breaks genuine ties, and it is **total**, so the ranking is stable
for any input.

Forbidden as ordering inputs, and absent by construction: randomness, the
current time, hash iteration order, network health, filesystem order.

Same registry + same capability + same policy ⇒ same ranking, always.

### Why `provider_id` is the tie-break

It is arbitrary but *explicit, documented, and total*. An arbitrary rule that
everyone can see beats a principled rule that occasionally falls through to
undefined behaviour.

---

## Explainability

The router never returns a bare winner. Every result carries its reasoning:

```python
ProviderSelection(
    capability_id, policy,
    selected_provider_id,          # or None
    reason,                        # why this outcome
    eligible_provider_ids,         # what survived
    ranking,                       # full deterministic order
    rejected_providers,            # every loser, with every reason
    failure,                       # PROVIDER_UNAVAILABLE when nothing selected
)
```

`reason` explains **the outcome** — why the winner won, or why nothing could be
selected. One field rather than two, because a selection and a refusal are
alternatives, never both.

### Reason vocabulary

Rejections:

```text
CAPABILITY_NOT_SUPPORTED
CAPABILITY_HAS_NO_PROVIDER
CAPABILITY_STATUS_REJECTED
PROVIDER_STATUS_REJECTED
PRIVACY_POLICY_REJECTED
DETERMINISM_POLICY_REJECTED
COMMERCIAL_USE_REJECTED
REDISTRIBUTION_REJECTED
EXPLICITLY_EXCLUDED
```

Selections and refusals:

```text
SINGLE_ELIGIBLE_PROVIDER     only one candidate; no ranking was needed
PREFERRED_PROVIDER           won on explicit preference
LOCALITY_PREFERRED           won on locality preference
DETERMINISM_PREFERRED        won on determinism preference
TIE_BREAKER                  won on lexical order
NO_ELIGIBLE_PROVIDER         providers exist; policy eliminated all of them
```

**Routing reasons are deliberately not execution failure codes.** "Excluded by
policy" and "crashed" are different facts, and collapsing them would make
routing unexplainable. The one shared vocabulary item is the *outcome*
`FailureCode.PROVIDER_UNAVAILABLE`, so a caller has a single failure code to
branch on while the reasons stay precise.

A rejected provider carries **all** its reasons, not just the first — a
provider can be simultaneously undeclared-by-policy and licence-restricted, and
knowing both is what lets a caller decide which constraint to relax.

---

## No-provider behavior

The router **never** returns `None` silently and never raises for "nothing
eligible" — that is a legitimate ecosystem outcome, not an error, and the
caller needs the rejection reasons. Check `result.selected`.

Three refusal outcomes, each naming the **active** blocker:

| Situation | `reason` | `rejected_providers` |
| --- | --- | --- |
| Capability declares no providers at all | `CAPABILITY_HAS_NO_PROVIDER` | empty |
| Capability is `ABSENT`/`DEFERRED` but providers exist | `CAPABILITY_STATUS_REJECTED` | each with `CAPABILITY_STATUS_REJECTED` |
| Providers exist; policy eliminated all | `NO_ELIGIBLE_PROVIDER` | each with its reasons |

All three set `failure = PROVIDER_UNAVAILABLE`.

A capability with zero providers is a **first-class ecosystem gap**, not
registry corruption. The registry permits it deliberately; the router reports
it honestly. For example, `lyrics.align` is declared and has no provider —
that is the truth about the ecosystem, and it should be queryable rather than
represented as an error.

---

## Layer boundaries

```text
Capability Registry  = what Moodify can conceptually do       ← implemented
Provider Router      = which declared provider is eligible     ← this document
Provider Runtime     = actually running it                     (not implemented)
Response-time probe  = can this machine run it right now       (not implemented)
```

The router sits **before** runtime availability:

```text
declared metadata → router eligibility → runtime probe → execution
```

It does not import Project Model, does not write project state, and does not
parse Sound Protocol requests. Sound Protocol 0.3 will eventually carry a
policy over the wire; this layer defines the *semantics* that serialization
will encode.

---

## Limitations

Honest boundaries of Router 0.1:

1. **Eligibility is not availability.** The router decides from declarations.
   A selected provider may still fail to run on this machine — the runtime,
   the weights or the credentials may be absent. Proving otherwise is a future
   *doctor* / runtime-probe layer, deliberately not built here.
2. **No health checks.** No ping, no executable check, no import probe, no
   credential test. Adding any of those would turn a pure decision layer into
   an I/O layer.
3. **No cost or latency model.** Policy has no cost dimension yet; ranking
   cannot prefer a cheaper provider.
4. **Per-provider determinism is newly modelled.** `Capability.determinism`
   describes the capability as declared; `Provider.determinism` describes this
   implementation. Registry 0.2 may want richer per-environment claims
   (version-pinned determinism, for example).
5. **No capability-status policy yet.** `EXPERIMENTAL`, `PARTIAL` and
   `IMPLEMENTED_NOT_CANONICAL` capabilities are routable; only `ABSENT` and
   `DEFERRED` are gated. Whether callers should be able to require
   `CANONICAL`-only is an open question.
6. **Single capability per call.** No multi-step composition — that is the
   Production Graph's job.

---

## Non-goals

Explicitly **not** implemented here, and not started:

```text
provider execution          dynamic provider loading     provider installation
Demucs / LALAL / Basic Pitch / music21 / FFmpeg execution
network access              GPU scheduling               model download
license enforcement         billing                      provider marketplace
CLI 2.0                     Sound Protocol 0.3           Production Graph
Project Model integration   GUI / desktop / Docker
```

---

## Worked examples against the built-in registry

```python
# Default policy selects nothing for separation: both paths are non-ACTIVE.
>>> select_provider("stem.separate").selected
False            # failure=PROVIDER_UNAVAILABLE, reason=NO_ELIGIBLE_PROVIDER

# The local preview separator requires an explicit opt-in.
>>> select_provider("stem.separate", ProviderPolicy(allow_experimental=True))
selected_provider_id='moodify.preview_separation'
reason=SINGLE_ELIGIBLE_PROVIDER

# Relaxing connectivity brings the cloud path in; both are eligible and the
# lexical tie-break decides.
>>> select_provider("stem.separate",
...     ProviderPolicy(allow_experimental=True, allow_connected_untested=True))
selected_provider_id='lalal.cloud'   reason=TIE_BREAKER

# A privacy constraint removes it again regardless of preference.
>>> p = ProviderPolicy(privacy=LOCAL_ONLY, allow_experimental=True,
...                    allow_connected_untested=True)
>>> select_provider("stem.separate", p).selected_provider_id
'moodify.preview_separation'

# Canonical measurement needs no opt-in at all.
>>> select_provider("audio.analyze").selected_provider_id
'moodify.auditory'

# A first-class gap, reported as such.
>>> select_provider("lyrics.align").reason
CAPABILITY_HAS_NO_PROVIDER
```

**The preview separator does not become the silent default merely because it
is local and self-contained.** It is `EXPERIMENTAL`, and the conservative
default says so.
