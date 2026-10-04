# MOODIFY_PRODUCT_REALIGNMENT_001.md

> **Repository:** `huliye24/moodify-ai`
> **Owner:** PRODUCT / CANON / ARCHITECTURE
> **Human direction:** Adopt Production Loop V1 as the Creator-side product direction
> **Execution rule:** Preserve existing capability and move forward; do not roll back the current Studio
> **Change class:** Canon and architecture realignment

## 0. Human decision

Moodify will be adjusted and designed according to the current Production Loop definition:

```text
Detect
→ Separate
→ Transcribe
→ Edit
→ Mix
→ Verify
→ Compare
→ Human Decide
↺
```

Moodify is not primarily a one-shot preset processor. A song becomes a persistent, structured and verifiable production project.

The product must preserve all useful existing work and move it into this loop. This task is not authorization to throw away the current Studio, rewrite the Core, or replace working code with a speculative architecture.

```text
CANON_CHANGE = YES
```

## 1. Why this change is allowed

The earlier constraint was not that Moodify could never change. The constraint was:

```text
AI may not silently redefine the product.
```

The human owner has now made the product-direction decision explicitly. Therefore agents may execute the realignment, provided that the change is:

- recorded in Canon;
- separated from unsupported capability claims;
- migrated without creating duplicate authorities;
- verified against existing runtime behavior;
- reversible by clear commits and compatibility adapters;
- divided into reviewable phases rather than implemented as one large rewrite.

## 2. Canon change declaration

### Why

The current product presents a mostly linear Studio sequence and still carries historical one-shot processing paths. The intended product is a persistent production loop with explicit verification, comparison, human decision and revision.

### Evidence

- Existing Studio already implements artifact-derived state, diagnosis projection, decomposition gates, explicit quick-mode consent and plan artifacts.
- Existing Core already contains analysis, controlled processing, evidence, Mix Graph work, protocol jobs and experimental comparison/verification capabilities.
- Existing runtime evidence shows that the parts exist, but they are not yet assembled into one authoritative closed loop.
- The human owner has explicitly selected Production Loop V1 as the product direction.

### Authority surfaces affected

At minimum inspect and update consistently:

```text
AGENTS.md
docs/canon/CURRENT_CANON.md
docs/canon/PRODUCT_DEFINITION_V3.md
docs/canon/PRODUCT_BOUNDARY.md
docs/canon/AUTHORITY_ORDER.md
docs/canon/CURRENT_ARCHITECTURE.md
docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md
docs/canon/CANON_CHANGELOG.md
docs/REPOSITORY_STATUS.md
docs/protocol/**
```

Do not update every historical document. Mark superseded documents as historical or point them to the current authority.

### Migration

Move canonical production-state authority from Desktop-only stage logic toward one Core-owned Project Model and Production Graph, using the existing Desktop pipeline as validated reference semantics.

### Rollback

- keep changes in small commits and PRs;
- preserve current artifact readers during migration;
- do not delete the existing pipeline until the Core replacement passes parity tests;
- keep a compatibility adapter for existing case directories;
- if a migrated stage fails parity, route that stage back through the current implementation without changing project artifacts.

## 3. One product, two connected loops

The current Canon and Production Loop are not competing product identities. They describe two connected loops.

### Creator production loop

```text
Song
→ Detect
→ Separate
→ Transcribe / Structure
→ Plan
→ Edit
→ Mix / Master
→ Verify
→ Compare
→ Human Decide
→ Accept / Revise / Reject
```

### Delivery and listening loop

```text
Accepted Project Version
→ Publish to My Library
→ My Phone
→ Play
→ Feedback
→ Next Revision
```

The relationship is:

```text
Production Loop
      ↓ accepted version
Delivery Loop
      ↓ listening feedback
Production Loop
```

Therefore the first delivery story remains valid, but publication begins only from an accepted project version rather than an opaque output WAV.

## 4. Product definition

Moodify is:

> An Agent-native music production layer that converts a song into a persistent, structured, editable and verifiable production project. It detects, decomposes, transcribes, plans, edits, mixes, verifies and compares versions while preserving final artistic authority for a human.

Short form:

> 先听懂，后拆开；先拆开，后修改；修改之后再验证；验证之后，由人决定。

Product thesis remains:

> **Generated is not finished.**

Public project principle remains:

> **Fork the code. Join the process.**

This is one Moodify product, not a new product identity.

## 5. Interface roles

### Moodify CLI / Agent interface

The CLI is the primary execution interface for complex production operations.

It must be able to:

- create and inspect projects;
- request capabilities;
- execute graph nodes;
- read machine-readable state;
- generate plans;
- run processing and verification;
- compare versions;
- record human decisions supplied through an authorized interface;
- resume and recover work without GUI-only state.

### Moodify Studio

Studio is the Creator workspace and human review surface.

It must:

- show the persistent project;
- show production graph and actual artifact state;
- expose evidence and provenance;
- preview and play versions;
- provide loudness-matched A/B comparison;
- ask for Accept / Revise / Reject;
- show AI/CLI activity and failures;
- allow simple operations without requiring terminal knowledge.

Studio must not own a second production state machine or private DSP implementation.

### Moodify App

**Decided 2026-10-04: `apps/music-android` is the only canonical App. `apps/android` is retired.**

App is the Listener-side personal music node:

- receive accepted versions;
- maintain My Library;
- play reliably;
- later return feedback or revision requests.

App must not own a second production state machine or private sound logic — the same constraint §5
already places on Studio, for the same reason: the App is a client of Core contracts, not an author
of them.

> **Execution note (recorded with the decision).** The decision above is canonical. The physical
> removal of the `apps/android/` directory is a separate repository step and had **not** landed on
> `main` when this was written — the directory was still present. Until it lands, that directory is
> a migration leftover, not a competing product claim: no new work may depend on it, and no
> interface may be documented as living there. Stating this explicitly is deliberate; a canonical
> document that silently describes a tree that does not exist is the failure mode this audit track
> exists to remove.

### Moodify Core

Core owns:

- Project Model contracts;
- capability IDs and capability registry;
- Production Graph semantics;
- provider contracts and routing policy;
- artifact-derived state;
- audio analysis, DSP and processing;
- verification and comparison facts;
- evidence, provenance and version contracts.

### Cloud and Core are not competing authorities

The cloud is the **system core for the delivery and listening loop** — catalogue, delivery and
device-adaptive playback — and it is authoritative *for that loop*.

**Core and Protocol remain the cross-client shared authority.** Every interface consumes the same
Project Model, capability and evidence contracts: CLI, Agent, Studio, App and cloud services alike.
The two layers serve different loops, which is why they may legitimately have different internal
sequences; what they may not have is two different definitions of the same fact.

A client that needs a different contract must change the shared contract, not fork it. This is the
same rule §5 applies to Studio and App, and the rule §3 of the Cloud track states as "there may be
only one authority".

## 6. Canonical production loop

The target loop is:

```text
OBSERVE
   ↓
DECOMPOSE
   ↓
UNDERSTAND
   ↓
PLAN
   ↓
EDIT
   ↓
RENDER
   ↓
VERIFY
   ↓
COMPARE
   ↓
DECIDE
   ↓
ITERATE
```

User-facing stages may remain concise:

```text
检测 → 分解 → 结构 → 方案 → 修改 → 成品 → 验证 → 对比 → 决定
```

Do not expose internal complexity merely to make the product look advanced.

## 7. Deep and Quick paths

Both paths remain supported.

### Deep path

```text
Detect
→ Diagnose
→ Separate
→ Transcribe / Structure
→ Plan
→ Edit
→ Mix / Master
→ Verify
→ Compare
→ Human Decide
```

### Quick path

```text
Detect
→ Diagnose
→ explicit human choice: Quick stereo finishing
→ Process stereo
→ Verify
→ Compare
→ Human Decide
```

Rules:

- Quick requires explicit human opt-in.
- Quick must not pretend decomposition occurred.
- Quick must not unlock deep-plan semantics.
- Deep takes precedence once its prerequisites exist.
- Both paths must produce versioned evidence and reach Verify / Compare / Human Decide.
- Quick is a valid product path, not a hidden shortcut, but it must remain honestly labeled.

## 8. Persistent Project Model

A source song becomes a project, not a temporary WAV.

Target conceptual model:

```text
project/
├── project.json
├── source/
├── analysis/initial/
├── diagnosis/
├── stems/
├── transcription/
├── score/
├── structure/
├── plans/
├── edits/
├── renders/
├── verification/
├── comparison/
├── decisions/
├── provenance/
└── exports/
```

Before freezing exact folders or schema:

- inventory existing case/project layouts;
- identify current authoritative artifacts;
- design a versioned schema;
- provide migration for existing projects;
- avoid copying large audio when a content-addressed reference is sufficient;
- preserve the immutable source asset and its hash.

Project state must be derived from actual artifacts. UI state is never production truth.

## 9. Version is the unit of production

Each processing attempt creates a new immutable version or attempt record.

Minimum record:

```text
version_id
parent_version_id
source_asset_hash
capability_id
provider_id
provider_version
parameters
input artifact hashes
output artifact hashes
measurements
evidence
timestamp
execution status
verification status
human decision status
```

Required human decisions:

```text
ACCEPT
REVISE
REJECT
INCONCLUSIVE
```

A decision records reviewer, time, scope, version and supporting notes/evidence.

## 10. Initial analysis, verification and comparison

These are distinct capabilities.

### Initial analysis

```text
What is this source now?
```

### Verification

```text
Did the intended technical change occur?
Did an existing problem improve?
Did processing introduce a new problem?
Did the render remain inside defined safety and identity boundaries?
```

### Comparison

```text
What differs between source/version A and version B?
```

Comparison may include aligned audio, measurements, findings and notes, but cannot automatically declare the artistic winner.

Technical verification is evidence. Artistic preference remains human authority.

## 11. Capability and provider rules

Production Graph nodes reference provider-independent capability IDs:

```text
audio.analyze
audio.diagnose
stem.separate
midi.transcribe
score.generate
pitch.correct
timing.correct
noise.reduce
clipping.repair
mix.render
master.render
audio.verify
audio.compare
```

Provider identity belongs to execution policy and provenance, not node semantics.

Correct:

```text
capability_id = stem.separate
provider_id = moodify.preview_separator
```

Incorrect:

```text
graph_node = demucs.local
```

Do not add placeholder capability IDs to the public supported registry before an implementation and contract exist. Unimplemented target capabilities remain explicitly `TARGET` or `ABSENT`.

## 12. Production Graph authority migration

Current validated semantics in `moodify-desktop/src/pipeline.js` must not be discarded.

Migration sequence:

1. characterize current Desktop behavior with tests;
2. define Core contracts that express the same artifact-derived states and gates;
3. implement the Core Project/Graph read model without changing Desktop behavior;
4. run parity tests against representative existing cases;
5. make Desktop consume the Core read model through a compatibility adapter;
6. move capability execution requests behind Core/Protocol contracts;
7. remove duplicate Desktop authority only after parity is proven.

At no point may two implementations independently decide the canonical stage.

## 13. Preserve current functionality

This realignment must preserve:

- existing source import and case history;
- existing Detect and Core reports;
- diagnosis projection and evidence pointers;
- existing separation integration and its preview-grade label;
- MIDI and MusicXML artifacts where available;
- deep-path gates;
- explicit Quick opt-in;
- existing plan files;
- current finishing presets at the finishing stage;
- existing Mix Graph work and evidence;
- CLI use without Studio;
- Windows packaging and current release work;
- Linux/Docker work as distribution engineering;
- current external-runtime honesty.

Do not regress to “analyze → preset → opaque WAV.”

## 14. What must not be overclaimed

Until runtime evidence exists, do not claim:

- mastering-grade stem separation;
- ground-truth MIDI or score;
- implemented pitch/timing/arrangement editing;
- automatic artistic judgment;
- self-contained Windows or Linux runtime;
- working Publish to My Library;
- canonical App selection;
- complete Production Graph execution;
- production cloud execution.

The target product may be defined before every capability is implemented, but status must remain visible.

## 15. Product experience principles

The interface should communicate work, not architecture.

The primary project view should answer:

```text
What song is this?
What does Moodify know?
What is the current version?
What changed?
What evidence supports it?
What can happen next?
What requires me?
Can I hear A/B now?
Can I accept, revise or reject?
```

Avoid making users reason directly about:

- provider routing;
- internal state machines;
- filesystem layouts;
- Python environments;
- schema versions;
- orchestration implementation.

Advanced details remain inspectable for agents, maintainers and professional users, but they are not the default product story.

## 16. Implementation program

Do not implement this as one PR.

### Phase 0 — Reality inventory

- map current Project/case/artifact layouts;
- inventory Core, Protocol, Desktop and CLI authorities;
- identify duplicate or conflicting state machines;
- list implemented versus target capabilities;
- establish representative golden projects;
- record the current test and runtime baseline.

Deliverable:

```text
docs/reports/PRODUCT_REALIGNMENT_001_REALITY_AUDIT.md
```

### Phase 1 — Canon alignment

- update affected Canon files;
- reconcile Production Loop with Delivery Loop;
- define interface roles;
- record unresolved decisions;
- update Canon changelog;
- do not claim target capability as implemented.

Deliverable:

```text
Product Realignment Canon PR
```

### Phase 2 — Project Model v0.1

- define versioned project manifest and artifact references;
- preserve immutable source and hashes;
- represent attempts, versions, provenance and human decisions;
- create compatibility reader for existing case directories;
- add schema and migration tests.

Deliverable:

```text
Project Model v0.1 PR
```

### Phase 3 — Core Production Graph read model

- port existing validated stage derivation and gates into a Core-owned read model;
- preserve Desktop pipeline parity;
- expose machine-readable CLI/API output;
- make Desktop consume it;
- prove that deleting an artifact moves state backward honestly.

Deliverable:

```text
Production Graph Read Model PR
```

### Phase 4 — Version, Verify and Compare loop

- create immutable processing attempts;
- integrate final verification separately from initial analysis;
- add source/version A/B comparison;
- implement loudness-matched playback where technically valid;
- record Accept / Revise / Reject / Inconclusive;
- allow revision to create a child attempt.

Deliverable:

```text
Closed Production Loop v0.1 PR
```

### Phase 5 — Capability execution migration

- route existing analysis, separation, transcription, planning and finishing through capability contracts;
- add provider metadata and provenance;
- preserve direct CLI operation;
- migrate one capability at a time;
- retain compatibility fallback until each capability passes parity.

Deliverable:

```text
One reviewable PR per capability family
```

### Phase 6 — Edit/Repair expansion

Implement only evidence-supported capabilities, one at a time:

```text
pitch
timing
noise
clipping
arrangement
```

Each capability requires:

- contract;
- authorized scope;
- provider implementation;
- parameters;
- preview/reversibility;
- verification method;
- evidence;
- failure behavior;
- human review path.

Do not add empty buttons to simulate progress.

### Phase 7 — Delivery loop

After an accepted production version exists:

- define Track Package manifest;
- Publish to My Library;
- local Desktop-to-phone transport;
- Android receipt and local library;
- playback;
- later feedback-to-revision link.

This phase must respect the unresolved canonical Android client decision.

## 17. First implementation milestone

The first usable closed loop should use current working capability rather than wait for every future edit engine:

```text
Import source
→ Initial Detect / Diagnose
→ choose Deep when prerequisites exist, or explicit Quick
→ create a versioned processing attempt
→ render using current authorized finishing capability
→ Final Verify
→ aligned A/B Compare
→ Human Accept / Revise / Reject
→ persist the decision and version graph
```

This is not a retreat from the full product definition. It is the first complete vertical slice of that definition.

Deep separation/transcription/edit capabilities can enter the same loop as they become verified.

## 18. Success criteria

Product realignment succeeds when:

1. one project survives application restart and can be resumed;
2. source audio remains immutable and hash-addressed;
3. actual artifacts determine state;
4. the same project can be inspected through CLI and Studio;
5. a processing attempt records parameters and provenance;
6. final verification is distinct from initial analysis;
7. A/B is distinct from verification;
8. human Accept / Revise / Reject is persisted;
9. Revise creates a new child version rather than overwriting history;
10. Quick and Deep paths remain honest;
11. Desktop and CLI use the same Core authority;
12. existing cases remain readable;
13. Windows/Linux/Docker distribution work does not create different sound behavior;
14. no target capability is presented as implemented without evidence.

## 19. Required tests and evidence

Each phase must include:

- schema/contract tests;
- existing-case compatibility tests;
- artifact deletion/backward-state tests;
- CLI/Desktop parity tests;
- deterministic replay where the provider permits it;
- input/output hash recording;
- failure and recovery tests;
- migration and rollback evidence;
- human-review state tests;
- repository structure guard;
- `git diff --check`;
- relevant full regression suite.

For perceptual claims:

```text
HUMAN_REQUIRED
```

Machine evidence must not be converted into artistic approval.

## 20. Human decisions still required

This product direction does not automatically decide:

```text
1. exact Project Model schema freeze
2. exact Production Graph protocol version
3. which edit/repair capability is implemented first
4. provider selection and licensing for mastering-grade separation
5. default Quick versus Deep presentation in Studio
6. when an accepted version becomes publishable
7. public compatibility guarantees
```

Record each unresolved point as `HUMAN_DECISION_REQUIRED`; do not let an implementation PR decide it silently.

**Decided 2026-10-04 — the canonical App question is resolved and removed from the list above.**
`apps/music-android` is the only canonical App; `apps/android` is retired. See §5 for the decision
and for the execution note on the directory itself. It was taken off the list rather than left in
place because an item that stays on a "still required" list after being decided is precisely how
the ambiguity would return.

## 21. Forbidden implementation pattern

Do not:

- rewrite Core and Desktop simultaneously;
- create a new top-level product or second public identity;
- make Desktop filesystem heuristics and Core graph both authoritative;
- hardwire graph semantics to Demucs, LALAL, Basic Pitch or another vendor;
- implement empty UI stages without executable capability;
- delete current cases or migrate them destructively;
- make final verification reuse initial-analysis labels without version context;
- auto-select an A/B winner;
- auto-accept a final version;
- turn the Quick path into the invisible default;
- block all useful production until every deep capability exists;
- stop release engineering solely because the target architecture is incomplete.

## 22. Pull request sequence

Create small PRs in this order:

```text
PR 1 — Product realignment reality audit and Canon update
PR 2 — Project Model v0.1 contracts and compatibility reader
PR 3 — Core Production Graph read model and Desktop parity
PR 4 — Versioned render + Verify + Compare + Human Decision
PR 5+ — Existing capabilities migrated individually
PR N — Publish accepted version to My Library
```

No PR may claim the full Production Loop is implemented unless every required node has runtime evidence.

## 23. Required first report

Before implementation, return:

```text
CURRENT REALITY
AUTHORITY MAP
DUPLICATE AUTHORITY RISKS
EXISTING PROJECT/CASE SCHEMAS
IMPLEMENTED CAPABILITIES
TARGET/ABSENT CAPABILITIES
CANON FILES TO CHANGE
MIGRATION PLAN
ROLLBACK PLAN
GOLDEN PROJECT FIXTURES
PROPOSED PR SEQUENCE
HUMAN_DECISION_REQUIRED
```

Then stop for human review of the authority map and migration boundaries before changing runtime authority.

## 24. Final direction

Moodify should not shrink back to a one-shot processor merely because the full product requires staged implementation.

The correct strategy is:

```text
keep the full Production Loop as the product definition
        +
deliver it through complete vertical slices
        +
preserve every verified capability
        +
move authority carefully into Core
        +
keep final artistic authority human
```

The target is not fewer ambitions. The target is one coherent product whose existing and future capabilities all enter the same persistent, verifiable loop.
