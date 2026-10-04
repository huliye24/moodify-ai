# Moodify Provider Manifest — DRAFT 001

```text
██████  DRAFT  ██████
This is an EXPLORATORY sketch. It is NOT canonical.
It is NOT a schema. Nothing validates against it.
Sound Protocol 0.3 (or a later task) owns the real definition.
Do not implement against this file.
```

> **Why it exists:** to make sure today's architecture does not foreclose
> third-party providers later. It is a design sketch, not a commitment.
> **Date:** 2026-10-04 · **Companion to:** `MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md` §11

---

## Purpose

A provider manifest is how an external engine declares *what capability it
implements* and *what it needs to run*, without Moodify hard-coding knowledge of
it. If this manifest is right, then adding a provider is a package drop, not a
Core change.

**Non-goals:** it does not rank quality, does not define audio formats, does not
describe internal parameters, and does not grant trust. Certification
(`…ECOSYSTEM_MAP_001.md` §10) is a separate, earned status.

---

## Sketch

```yaml
# ── DRAFT — not a schema, not canonical ──────────────────────────────
provider: demucs.local
manifest_version: 1
display_name: "Demucs (local)"

capabilities:
  - id: stem.separate
    contract: stem.separate/1          # which contract revision it implements
    targets: [vocals, drums, bass, other]

runtime:
  mode: local                          # local | cloud | external_app
  kind: python
  entry: "demucs.separate:main"        # or a CLI path / a module call
  python: ">=3.10"
  gpu: optional                        # required | optional | none
  weights:
    required: true
    source: huggingface
    # weights are NOT bundled; fetched at install time, never committed

license:
  code: MIT
  weights: MIT                         # MAY differ from code — always declare both
  commercial_use: allowed              # allowed | restricted | unknown
  redistribution: allowed              # of the weights, separately from the code
  note: "Code and weights are MIT as of v4.1.0; verify per release."

inputs:
  - kind: audio
    formats: [wav, flac, mp3, m4a, aiff]
    min_channels: 1
    max_channels: 2

outputs:
  - kind: stems
    naming: "{source}__{target}.wav"
    manifest: true                     # emits a per-run manifest
    preserves: [sample_rate, channel_count, duration]

determinism:
  claim: deterministic                 # deterministic | seeded | nondeterministic
  scope: "same version + same input + same params"

errors:
  # provider-native -> Moodify failure vocabulary
  "FileNotFoundError": DEPENDENCY_MISSING
  "out of memory": RESOURCE_LIMIT
  "torch.cuda.OutOfMemoryError": RESOURCE_LIMIT
  "*": EXECUTION_FAILED

certification:
  level: DRAFT                         # EXPERIMENTAL | COMPATIBLE | VERIFIED
  tests: tests/contract_stem_separate.py
```

---

## Field notes and the decisions behind them

### `capabilities[].id` — the whole point

The provider declares a **capability ID**, never the reverse. Moodify never asks
"is Demucs installed?"; it asks "who can do `stem.separate`?". This is what makes
`provider.route` (§5 of the map) possible at all.

`contract: stem.separate/1` is the versioned interface. A provider implementing
`stem.separate/1` keeps working when `/2` arrives; it simply stops being
*preferred* until it updates. Breaking changes become a new contract, not a
breaking change to callers.

### `license` — deliberately split into `code` and `weights`

This is the field most likely to be wrong by omission, and the domain's most
common trap:

```text
code: MIT          ← what people check
weights: CC BY-NC-SA 4.0   ← what actually governs the output
```

During this research, at least two widely-used engines were found with
permissive code and **non-commercial weights** (madmom's pretrained models;
Open-Unmix's UMXL). A manifest that declares only `license: BSD` is not merely
incomplete — it is actively misleading. `commercial_use` and `redistribution`
must therefore be explicit enums, and `unknown` must be an *allowed but loudly
visible* value rather than a default that reads as permission.

### `runtime.weights.source` — never bundled

Weights are fetched at install time and never committed. The repository already
follows this instinct (Demucs is a declared extra with weights never downloaded;
`.venv-basic-pitch/` is gitignored). Encoding it in the manifest prevents a
future provider from quietly adding hundreds of megabytes to the repo.

### `errors` — provider errors mapped into the vocabulary

The mapping is required, not optional. `"*": EXECUTION_FAILED` is the floor so
that **nothing escapes unmapped**. This is the manifest-level expression of the
principle HOTFIX 000 established in code: a missing dependency must surface as
`DEPENDENCY_MISSING`, not as a raw traceback. Provider-native detail stays
attached as developer information; it never becomes the contract.

### `determinism.claim` — a promise with consequences

Providers that cannot honour `deterministic` are still admissible, but the claim
must be declared so the Production Graph can decide whether a result is
reproducible and whether cached derived data may be reused. A provider that
claims determinism and is not is a *correctness* bug, not a quality issue.

### `certification.level` — self-declared, separately verified

The manifest states the level the provider *believes* it has; the level is
granted by Moodify's contract tests. Self-declaration without verification is
what the certification concept exists to prevent — the field is here so that the
gap between claim and grant is visible.

---

## Open questions this draft does not answer

1. **Package format.** Python entry point? Container image? Signed binary?
   Unresolved, and probably needs more than one answer.
2. **Trust and provenance of the provider itself.** Who signed this manifest?
   A provider that lies about determinism or licence is a supply-chain problem
   the current sketch cannot detect.
3. **Parameter schemas.** `stem.separate` needs provider-specific parameters;
   how they are declared, validated and namespaced so they never leak into
   canonical project state (§9 anti-lock-in rule 2) is undecided.
4. **Version negotiation.** What happens when a provider implements a contract
   revision Moodify no longer ships?
5. **Cloud credential handling.** `runtime.mode: cloud` needs a credential
   reference model that never stores secrets in the manifest.
6. **Whether this should be one manifest or two** — provider identity vs
   capability binding. A single provider may implement many capabilities with
   different certification levels each.

---

## What this draft explicitly does not do

- It does **not** add a dependency, a directory, a schema file, or a validator.
- It does **not** modify `moodify.project`, the contracts package, or Sound
  Protocol.
- It does **not** authorise implementing `moodify provider install`.

It exists so that when that work is scheduled, the constraints are already
written down.
