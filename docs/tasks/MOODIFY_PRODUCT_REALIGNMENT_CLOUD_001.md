# MOODIFY_PRODUCT_REALIGNMENT_CLOUD_001.md

> **Track:** Cloud / Core authority
> **Executor:** Cloud AI on Linux
> **Parent direction:** `docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_001.md`
> **Change class:** Canon migration design + Core implementation preparation
> **Rule:** Own shared contracts and headless execution; do not build a second Studio or make perceptual decisions.

## 0. Mission

Build the authoritative, platform-neutral foundation for the Moodify Production Loop:

```text
Project Model
→ Artifact-derived state
→ Production Graph read model
→ Capability contracts
→ Version / Evidence / Provenance
→ Verify / Compare facts
→ CLI and container execution
```

The Cloud track owns canonical machine-readable contracts. It must make the same project understandable and executable by CLI, agents, Linux containers and Studio without creating interface-specific sound logic.

```text
CANON_CHANGE = YES
```

Canon changes must follow the parent task and require human review before runtime authority moves.

## 1. Product direction

Creator-side loop:

```text
Detect
→ Separate
→ Transcribe / Structure
→ Plan
→ Edit
→ Mix / Master
→ Verify
→ Compare
→ Human Decide
→ Iterate
```

Cloud owns the facts and contracts behind this loop. It does not own the human experience of listening, A/B interaction or artistic approval.

## 2. Ownership

Cloud track may own and edit:

```text
moodify-core-package/**
protocol/**
docs/protocol/**
Core-owned schemas
Core-owned project/graph modules
CLI commands and machine-readable output
provider contracts and execution metadata
Dockerfile / docker-compose.yml / .dockerignore
Linux Core/CLI CI
Core tests and golden project fixtures
Canon files approved for this migration
```

Cloud track must not independently own:

```text
moodify-desktop renderer UX
Studio layout or interaction design
Windows installer acceptance
audio playback UX
human A/B decisions
Android client selection
Publish to My Library UI
```

If a Desktop change is required to demonstrate a contract, write a contract example or issue for the Local track rather than embedding new UI logic.

## 3. Shared-authority rule

There may be only one authority for:

- project schema;
- project version identity;
- production stage derivation;
- capability IDs;
- graph node state;
- evidence and provenance format;
- verification facts;
- comparison facts;
- execution status.

Cloud owns these contracts. Local consumes them.

Do not preserve `moodify-desktop/src/pipeline.js` as a second long-term authority. Treat its validated behavior as migration input and parity oracle until the Core read model is proven.

## 4. Branch and worktree

Use a dedicated Linux worktree.

Preferred branch:

```text
cloud/product-loop-core-001
```

Before work:

```bash
git fetch origin --prune
git status --short
git rev-parse origin/main
gh pr list --repo huliye24/moodify-ai --state open
```

Base on current `origin/main` unless the required parent Canon/task commit is still unmerged. If stacked work is unavoidable, document the exact dependency and temporary PR base.

Never edit the Local worktree or reuse its branch.

## 5. Phase C0 — Reality and authority audit

Before implementation, inventory:

- every existing case/project directory layout;
- every project/case manifest;
- every production state machine or stage derivation implementation;
- existing Mix Graph, protocol job, evidence and treatment-record schemas;
- CLI commands that create or mutate artifacts;
- Desktop pipeline semantics and tests;
- existing verification and comparison implementations;
- implemented, experimental, target and absent capabilities;
- migration risks for existing projects.

Deliver:

```text
docs/reports/PRODUCT_LOOP_CLOUD_REALITY_AUDIT_001.md
```

The report must include:

```text
AUTHORITY MAP
DUPLICATE AUTHORITIES
SCHEMA INVENTORY
IMPLEMENTED CAPABILITIES
TARGET / ABSENT CAPABILITIES
MIGRATION INPUTS
PROPOSED CONTRACT BOUNDARY
ROLLBACK PLAN
HUMAN_DECISION_REQUIRED
```

Stop for human review before moving production authority.

## 6. Phase C1 — Canon and contract proposal

Propose, but do not overclaim:

- Production Loop and Delivery Loop relationship;
- Core ownership of Project Model and Production Graph;
- CLI/Agent, Studio and App roles;
- initial analysis versus final verification;
- verification versus A/B comparison;
- human-decision authority;
- Quick and Deep path invariants;
- target capability status vocabulary.

Update Canon only in a dedicated reviewable PR with:

```text
why
evidence
affected authority files
migration
rollback
```

Do not mix broad runtime changes into the Canon PR.

## 7. Phase C2 — Project Model v0.1

Design a versioned, provider-neutral Project Model.

Minimum concepts:

```text
project_id
schema_version
immutable source asset + hash
artifact references
attempt_id / version_id
parent_version_id
capability execution records
parameters
provider metadata
input/output hashes
evidence references
verification state
comparison references
human decision reference
timestamps
failure/recovery state
```

Requirements:

- existing case directories remain readable;
- migration is non-destructive;
- source audio is never overwritten;
- missing artifacts move state backward honestly;
- large audio is referenced rather than copied without reason;
- schema validation is dependency-light and deterministic;
- unknown future fields can be handled according to a documented compatibility rule;
- CLI can inspect the full project without Electron.

Do not freeze the public schema until human review.

## 8. Phase C3 — Production Graph read model

Implement a Core-owned read model before building a general-purpose execution engine.

It must derive state from actual artifacts and preserve current invariants:

- diagnosis follows real Core analysis;
- Deep planning requires stems and MIDI;
- MusicXML does not replace MIDI;
- Deep finishing requires a real plan artifact;
- Quick finishing requires explicit human opt-in;
- Quick does not unlock Deep planning;
- Deep takes precedence once prerequisites exist;
- deleting an artifact moves the project backward;
- UI flags cannot advance canonical state.

Expose machine-readable CLI output, for example through a reviewed command such as:

```text
moodify project inspect <project>
```

Do not invent final command names without checking existing CLI conventions.

## 9. Phase C4 — Versions, verification and comparison facts

Add the headless contract for:

```text
rendered attempt
→ final verification
→ source/version comparison
→ pending human decision
```

Verification answers technical questions. Comparison describes differences. Neither chooses the artistic winner.

Required states include:

```text
REVIEW_REQUIRED
HUMAN_REQUIRED
INCONCLUSIVE
FAILED
```

Human decisions are recorded only when an authorized interface supplies reviewer, scope, time and evidence:

```text
ACCEPT
REVISE
REJECT
INCONCLUSIVE
```

Cloud AI must never generate `ACCEPT` by itself.

## 10. Phase C5 — Capability registry and provider contracts

Use provider-independent capability IDs.

The registry must distinguish:

```text
SUPPORTED
EXPERIMENTAL
TARGET
ABSENT
UNAVAILABLE_IN_ENVIRONMENT
```

Only register supported execution when runtime evidence exists.

Provider selection belongs to execution policy and provenance:

```text
capability_id = stem.separate
provider_id = moodify.preview_separator
```

Do not hardwire graph semantics to model or vendor names.

## 11. Phase C6 — CLI and Docker execution

Make the Project Model and current supported loop operable in a Linux container:

```text
read-only input mount
read-write project/output mount
non-root runtime
Core import
project inspect
supported processing attempt
verification
comparison facts
evidence persistence
explicit failure codes
```

Docker is headless CLI/Core execution, not Studio-in-a-container.

Preserve secrets and private audio boundaries. Do not bake audio, credentials or model weights into images.

Use the Linux/Docker release task as packaging guidance:

```text
docs/tasks/MOODIFY_LINUX_DOCKER_RELEASE_001.md
```

## 12. Cloud tests

At minimum:

- schema validation and compatibility;
- old-case reader tests;
- artifact deletion/backward-state tests;
- Quick/Deep gate parity against current Desktop tests;
- deterministic version identifiers where required;
- immutable attempt/no-overwrite tests;
- input/output hash tests;
- provenance round-trip;
- verification/compare separation;
- human-decision authorization and audit record tests;
- CLI JSON contract tests;
- Linux and Docker smoke tests;
- invalid-input and interrupted-execution recovery;
- repository structure guard;
- `git diff --check`;
- relevant Core regression suite.

Create small synthetic or explicitly authorized fixtures. Never commit private audio or heavy generated output.

## 13. Contract handoff to Local

For each contract milestone, provide:

```text
schema/version
example project
example CLI JSON
state transition table
error codes
compatibility notes
migration notes
test command
commit SHA
PR link
```

Local development may integrate only a committed contract version. Do not ask Local to parse unstable internal files.

Breaking a handed-off contract requires:

- explicit version change;
- migration note;
- updated examples;
- notification in the shared integration report.

## 14. Coordination checkpoints

Cloud must stop and hand off at:

```text
C0 — reality audit complete
C1 — Canon/authority proposal ready
C2 — Project Model contract ready
C3 — Production Graph read model parity proven
C4 — Verify/Compare/Human Decision contract ready
C5 — CLI/container vertical slice ready
```

Do not keep changing a contract while Local is integrating it without versioning the change.

## 15. Forbidden work

Do not:

- redesign Studio UI;
- implement GUI-only state;
- make cloud availability authoritative for local projects;
- introduce a new server, account system or object store;
- create a second Core or second DSP engine;
- rewrite all orchestration at once;
- promote experimental metrics to production truth;
- implement placeholder Edit buttons or fake providers;
- auto-accept versions;
- publish containers or releases without Phase B approval;
- merge Local and Cloud branches wholesale.

## 16. Required Cloud PR sequence

Prefer:

```text
Cloud PR 1 — Reality audit and Canon proposal
Cloud PR 2 — Project Model v0.1 contracts and compatibility reader
Cloud PR 3 — Core Production Graph read model
Cloud PR 4 — Version / Verify / Compare / Human Decision contracts
Cloud PR 5 — CLI and Docker vertical slice
Cloud PR 6+ — capability migrations, one family at a time
```

No auto-merge. Attach every PR and record dependency order.

## 17. Cloud completion report

Return:

```text
BASE SHA / BRANCH / COMMITS / PRS
AUTHORITY AUDIT
CANON CHANGE STATUS
PROJECT MODEL VERSION
PRODUCTION GRAPH PARITY
CLI CONTRACT
DOCKER RESULT
TESTS
MIGRATION / ROLLBACK
CONTRACT HANDOFF TO LOCAL
KNOWN LIMITATIONS
HUMAN_DECISION_REQUIRED
NEXT LOCAL CHECKPOINT
```

Cloud completion means a stable contract is ready for Local integration. It does not mean the product experience or human listening loop is complete.
