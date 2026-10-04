# Moodify Capability Registry 0.1

> **Status:** implemented — runtime truth for *declarations*.
> **Schema:** `moodify.capabilities/0.1`
> **Code:** `moodify-core-package/src/moodify/capabilities/`
> **Date:** 2026-10-04
> **Companion to:** `MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md` (strategy) — this document describes what is **built**.

---

## Purpose

The registry is the canonical answer to *what can Moodify do?*

```text
What capability exists?
What is its stable ID?
What does it accept and produce?
Which providers can implement it?
What failures can it return?
Is it canonical, experimental, unavailable, or deferred?
```

Before this, Moodify had implementations, specialised registries and
provider-specific paths, but no single place to ask those questions.

The rule it exists to enforce:

```text
Models change. Capabilities persist.
```

`stem.separate` survives Demucs being replaced. `demucs.separate` does not.

**It executes nothing.** There is no `execute`, no router, no dynamic import,
no subprocess, no network call, and no model. It is metadata and discovery.

---

## Capability ID rules

Format: **`domain.operation`** — exactly two dot-separated segments.

```text
audio.decode     audio.analyze    audio.verify     audio.convert
stem.separate
pitch.analyze    pitch.correct
rhythm.analyze   harmony.analyze  structure.analyze
instrument.identify             lyrics.align
midi.transcribe  score.generate
melody.*         noise.reduce     timing.correct   clipping.repair
mix.render       master.render
delivery.export  metadata.read
```

A segment must match `[a-z][a-z0-9_]*` — lowercase ASCII, no leading digit or
underscore. Unknown field names are rejected (`extra="forbid"`).

**Rejected by construction:**

| Rejected | Why |
| --- | --- |
| `stem.separate.v1` | Versions are a *contract* revision, not a new capability |
| `stem.v2` | A version-like segment is refused even though it parses |
| `demucs.separate` | Provider identity belongs **below** the capability boundary |
| `Demucs.separate` | Not lowercase |
| `stem.separate.extra` | Exactly two segments |

> **Honest limit:** the format cannot detect a vendor name. `demucs.run` and
> `ffmpeg.convert` are *syntactically valid*. They are excluded because the
> registry does not declare them — an architectural decision, not a syntactic
> one. A test records this boundary explicitly rather than implying the
> validator covers it.

---

## Status vocabulary

Status describes **what is real in this branch**, from repository evidence.

| Status | Meaning |
| --- | --- |
| `CANONICAL` | Supported stable capability |
| `IMPLEMENTED_NOT_CANONICAL` | Code exists; no stable public contract |
| `PARTIAL` | Some behaviour exists; the capability is incomplete |
| `EXPERIMENTAL` | Prototype, not a production contract |
| `ABSENT` | Known domain with no implementation |
| `LEGACY` | Retained for compatibility, not future direction |
| `DEFERRED` | Intentionally not pursued now |

**Status is never inferred from a filename.** The audit that seeded this
registry found that a module with a promising name is not a capability:
`tempo_bpm` is declared and serialized with no producer, and `StructureContext`
has zero construction sites in production code. Both are recorded `PARTIAL`.

In the current seed, `LEGACY` and `DEFERRED` are defined but unused. That is
deliberate: status reports reality, and inventing a `LEGACY` classification to
exercise an enum would be a fabricated fact. "Not pursuing this" is expressed
by posture (`DEFER`), not by pretending the status differs.

---

## Strategic posture

`BUILD` · `INTEGRATE` · `DELEGATE` · `DEFER` — from ECOSYSTEM 001.

Posture is **architecture intent, not runtime availability.** Status and
posture are separate fields because they answer different questions:

```python
status = ABSENT              # nothing implements this today
strategic_posture = INTEGRATE  # and we intend to wrap an external engine
```

`timing.correct` is the clearest example: `ABSENT` + `DEFER` — nothing
implements it *and* we are deliberately not pursuing it.

---

## Provider metadata

Provider identity is separate from capability identity. The **references must
agree in both directions**: if a capability lists a provider, that provider
must list the capability. The registry refuses to build otherwise.

```text
provider_id · name · provider_type · capability_ids · execution_mode
status · code_license · weights_license · commercial_use
redistribution · runtime_requirements · notes
```

Provider status: `ACTIVE` · `CONNECTED_UNTESTED` · `EXPERIMENTAL` ·
`DECLARED_ONLY` · `UNAVAILABLE` · `DEPRECATED`.

A provider is **not** `ACTIVE` merely because a dependency name exists.

### Code licence vs weights licence

These are separate fields on purpose. This is the domain's most common trap:

```text
code_license:    MIT              ← what people check
weights_license: CC-BY-NC-SA-4.0  ← what actually governs the output
```

ECOSYSTEM 001 found at least two widely-used engines shipping permissive code
over **non-commercial weights**, and one with an unclear licence. The three
states are distinct and must not be collapsed:

| Value | Meaning |
| --- | --- |
| `"MIT"` / `"Apache-2.0"` / … | Declared licence |
| `"UNKNOWN"` | Weights exist; terms **unverified**. A risk, not a permission |
| `None` | The provider involves **no weights at all** — a system binary, a cloud API, a pure algorithm |

`commercial_use` and `redistribution` are explicit enums defaulting to
`UNKNOWN`. No legal enforcement engine is implied or provided.

---

## Failure vocabulary

A provider traceback is **not** the ecosystem contract.

```text
DEPENDENCY_MISSING      required runtime/model/binary/service absent
PROVIDER_UNAVAILABLE    known but unreachable or ineligible
INVALID_INPUT           violates the capability contract
UNSUPPORTED_FORMAT      outside the declared format set
RESOURCE_LIMIT          memory/disk/GPU/time budget exceeded
AUTH_REQUIRED           credentials absent or rejected
RATE_LIMITED            provider throttled the caller
EXECUTION_FAILED        provider ran and failed  (the catch-all floor)
QUALITY_GATE_FAILED     output produced, failed a declared gate
REVIEW_REQUIRED         uncertain; human authority required
NOT_IMPLEMENTED         declared capability with no implementation
TIMEOUT                 exceeded a caller deadline
INTEGRITY_ERROR         a digest or size check failed
CONFLICT                two sources of truth disagree
CANCELLED               abandoned by the caller or a single-flight lock
```

Each optional code is justified by existing repository behaviour rather than
added for symmetry — `CONFLICT` because `auditory/evidence/conflicts.py`
already models contradictory evidence; `INTEGRITY_ERROR` because content is
verified by sha256 throughout; `CANCELLED` because long runs are cancellable.

`Failure` carries `code`, `message`, `retryable`, and optionally `provider` and
`details`. `Failure.of(...)` derives `retryable` from a canonical table so the
two cannot drift:

```python
Failure.of(FailureCode.RATE_LIMITED, "slow down").retryable   # True
Failure.of(FailureCode.NOT_IMPLEMENTED, "no engine").retryable  # False
```

`NOT_IMPLEMENTED`, `INVALID_INPUT` and `UNSUPPORTED_FORMAT` are **not**
retryable: retrying an unchanged request that is deterministically invalid is
not a recovery strategy.

---

## Query API

```python
from moodify.capabilities import (
    list_capabilities, get_capability, has_capability,
    list_providers, get_provider, providers_for,
    registry_snapshot, registry_snapshot_json,
)

get_capability("stem.separate")
providers_for("stem.separate")
list_capabilities(status=CapabilityStatus.CANONICAL, domain="audio")
```

Two deliberate distinctions:

- `has_capability(x)` **never raises** — a malformed or non-string ID is simply
  not a member. Discovery predicates should read "not available" on a typo, not
  crash.
- `providers_for(x)` **raises** `CapabilityNotFound` for an undeclared
  capability, and returns `()` for a declared capability with no provider.
  "Not a capability" and "a capability nothing implements yet" are different
  answers, and conflating them would hide real gaps.

`CapabilityNotFound` and `ProviderNotFound` subclass `KeyError`, so callers can
use dict-style defensive access.

---

## Snapshot format

```python
{"schema": "moodify.capabilities/0.1", "capabilities": [...], "providers": [...]}
```

Capabilities and providers are sorted by ID and serialized through the
repository's canonical serializer. Deterministic in the strong sense: the same
declarations always produce the same bytes, so the snapshot can be hashed and
compared across builds. This is what Agent and CLI discovery will read.

`moodify.capabilities/0.1` is **not** the canonical contract `schema_version`
(`"1.0"`). They version different things.

---

## Layer boundaries

```text
Capability Registry  = what Moodify can conceptually do   ← this package
Sound Protocol       = how a capability request is expressed   (MSP 0.2 today)
Provider Router      = which implementation performs it        (not implemented)
Production Graph     = how capabilities are composed           (not implemented)
Project Model        = persistent production state             (not merged)
```

These layers are not merged, and this package does not reach into any of them.
It does not import `moodify.project` — that layer is implemented on
`codex/project-model-001` and is **not** on `main`; `project` appears only as a
conceptual `IOType`.

**The rule the Production Graph will inherit:** graph nodes reference
`capability_id`, never `provider_id`. A graph written against `stem.separate`
survives its provider being replaced.

---

## Relationship to `auditory/inventory.py`

`moodify-core-package/src/moodify/auditory/inventory.py` is **not** superseded
in the sense of being deleted — it is preserved (§35 of the task forbids broad
cleanup), and this document records its status precisely.

| | `auditory/inventory.py` | Capability Registry |
| --- | --- | --- |
| Scope | Auditory subsystem only | Whole system |
| Method | **Scans the package** and classifies modules | **Explicit static declarations** |
| Referenced by runtime | **No** — no import from `src/`, the desktop shell, `ops/` or tests | — |
| Accuracy | Its map names `capability_registry`, `transcription`, `score_engine`, `adapters`, `ports`, `storage` — **none of which exist on `main`** | Validated at construction |
| Role | Specialised, legacy audit tool | **Canonical general-purpose source of capability truth** |

The contrast is the point. `inventory.py` discovers capabilities by looking at
files, which is exactly the inference this registry exists to replace: it
assumes `module exists → capability exists`, and its staleness is the
predictable result. Its own header already concedes that low-confidence entries
"must not be silently trusted".

**No change was made to `inventory.py`.**

---

## Non-goals

Explicitly **not** implemented here, and not started:

```text
provider execution          provider routing            dynamic installation
CLI 2.0 capability commands Sound Protocol 0.3          Production Graph
Project Model integration   third-party provider registration
GPU / model downloads       network calls               license enforcement
GUI / desktop changes       Docker changes
```

Nothing in this package imports an engine, opens a socket, or reads the
filesystem to decide what exists.

---

## Seeded declarations

**21 capabilities, 9 providers.**

| Status | Count |
| --- | ---: |
| `CANONICAL` | 3 |
| `IMPLEMENTED_NOT_CANONICAL` | 4 |
| `PARTIAL` | 4 |
| `EXPERIMENTAL` | 4 |
| `ABSENT` | 6 |

Nine capabilities have **no provider at all** — `rhythm.analyze`,
`structure.analyze` and `pitch.analyze` (types without producers) plus the six
`ABSENT` ones. That is the registry doing its job: it makes the gaps a
first-class, queryable fact rather than an assumption.

Each declaration carries a `notes` field stating the evidence behind its
status, so a reader can re-check the classification instead of trusting it.
