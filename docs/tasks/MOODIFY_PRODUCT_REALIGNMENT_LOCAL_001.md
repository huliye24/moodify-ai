# MOODIFY_PRODUCT_REALIGNMENT_LOCAL_001.md

> **Track:** Local / Studio and human-review experience
> **Executor:** Local AI on the owner's Windows computer
> **Parent direction:** `docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_001.md`
> **Dependency:** Versioned contracts delivered by the Cloud track
> **Rule:** Build the product experience on shared Core truth; do not create a second production authority.

## 0. Mission

Turn the Cloud/Core contracts into a usable Creator workspace on the owner's real Windows machine:

```text
Open Project
→ understand current state
→ invoke authorized next action
→ see progress and evidence
→ play versions
→ A/B compare
→ Accept / Revise / Reject
→ resume later
```

Local owns interaction, playback, real-device behavior and human-review evidence. It does not own canonical production-state rules or a second DSP implementation.

```text
CANON_CHANGE = YES
```

The parent Canon direction is authorized, but Local must consume the reviewed Cloud contract rather than defining its own competing schema.

## 1. Product role

Moodify Studio is the Creator workspace and human decision surface.

Its product questions are:

```text
What song/project is open?
What does Moodify know?
What version am I hearing?
What changed and why?
What evidence exists?
What can happen next?
What failed?
What requires me?
Can I compare now?
Do I accept, revise or reject?
```

The interface should hide routine internal complexity while keeping evidence and advanced details inspectable.

## 2. Ownership

Local track may own and edit:

```text
moodify-desktop/src/**
moodify-desktop/renderer/**
moodify-desktop/scripts/**
desktop packaging assets/configuration
Studio contract adapters
playback and A/B interaction
project navigation and history UX
progress/error/recovery presentation
human decision capture UI
Windows runtime detection and acceptance
local screenshots and manual-test reports outside Git
Studio tests
```

Local track must not independently own:

```text
Project Model schema
Production Graph semantics
capability registry authority
provider routing policy
Core DSP
verification fact computation
comparison fact computation
CLI contract
Docker execution contract
```

When a Core contract is missing, create a precise request for Cloud. Do not fill the gap with a permanent Desktop-only truth.

## 3. Shared-authority rule

Studio displays and requests Core state; it does not invent it.

Temporary compatibility code may read existing cases during migration, but it must be isolated behind one adapter with:

- a removal condition;
- contract version detection;
- tests against old cases;
- no independent advancement of canonical state;
- explicit fallback status when the Cloud contract is unavailable.

Do not create a second `pipeline-v4.js` state machine.

## 4. Branch and worktree

Use a dedicated Windows worktree.

Preferred branch:

```text
local/product-loop-studio-001
```

Before work:

```powershell
git fetch origin --prune
git status --short
git rev-parse origin/main
gh pr list --repo huliye24/moodify-ai --state open
```

Base on current `origin/main` plus only the reviewed Cloud contract commit required for the current checkpoint. If the contract PR is not merged, use a clearly documented stacked PR rather than copying its files.

Never edit the Cloud worktree or force-push its branch.

## 5. Phase L0 — Current Studio experience audit

Run the existing Studio on the owner's machine and document the real journey:

```text
launch
open/import song
Detect
Diagnose
Separate
Structure
Plan
Finish
playback/review
restart/resume
```

For every stage record:

- what the user sees;
- what actually executes;
- what artifact proves completion;
- what is blocked or missing;
- what error is shown;
- whether the user knows what to do next;
- whether a result can be heard;
- whether the state survives restart.

Use authorized audio only. Do not commit private files or screenshots.

Deliver:

```text
docs/reports/PRODUCT_LOOP_LOCAL_UX_AUDIT_001.md
```

Do not redesign before this evidence exists.

## 6. Phase L1 — Contract adapter

Consume the Cloud Project Model and Production Graph read model through one adapter.

Requirements:

- explicit contract/schema version;
- machine-readable validation errors;
- no direct duplication of graph gate logic;
- existing case compatibility through the approved migration reader;
- safe behavior when project data is incomplete or newer than the Studio;
- stable test fixtures supplied by Cloud;
- all sound-affecting actions requested through Core/Protocol capability contracts.

The adapter may translate Core data into view models. It may not change canonical meaning.

## 7. Phase L2 — Project workspace

Make a persistent project, not a temporary processing screen, the primary Studio container.

The workspace should show:

```text
project identity
source identity
current accepted version
active attempt/version
production-loop position
available next actions
blocked prerequisites
artifacts and evidence
history/version graph
human-review state
```

Preserve the existing left dock and useful views. Improve them rather than restarting the UI from scratch.

The stage view should present the loop clearly without exposing provider internals by default.

## 8. Phase L3 — Action and progress experience

For every executable capability:

- show the action before execution;
- show what inputs/version it will use;
- show whether it is Deep or Quick;
- request explicit consent where required;
- show progress without fabricating percentages;
- allow safe cancellation only if the backend supports it;
- preserve logs and partial evidence;
- show actionable failure and retry/recovery path;
- refresh state from actual artifacts after completion.

Do not mark a stage complete because the user clicked a button.

## 9. Phase L4 — Version review

Implement a version-oriented review surface.

Minimum experience:

```text
Source / Version A / Version B selector
version identity and parent
processing reason
parameters
provider and timestamp
verification summary
comparison facts
human notes
decision state
```

Version history must be immutable from normal review actions. A revision creates a new child attempt rather than overwriting the prior output.

## 10. Phase L5 — Playback and A/B

Studio owns the listening interaction, while Core owns comparison facts.

Required A/B behavior:

- clearly identify A and B;
- fast, reliable switching;
- preserve playback position when feasible;
- use the approved loudness-alignment contract rather than an ad hoc UI gain trick;
- expose original versus processed audio paths honestly;
- show technical deltas separately from preference;
- never highlight an automatic winner;
- report missing/corrupt audio explicitly;
- preserve channel count and sample-rate facts;
- work on real local audio and real output devices.

Automated tests cannot grant listening approval.

## 11. Phase L6 — Human decision and revision

Provide explicit actions:

```text
Accept
Revise
Reject
Inconclusive
```

Before recording a decision, show:

- exact version;
- verification state;
- unresolved failures/warnings;
- reviewer identity mechanism approved by the contract;
- optional human notes;
- scope of the decision.

`Revise` must create or request a child version with a human-authored objective. It must not mutate an accepted or rejected version.

Studio sends the decision through the Cloud-owned contract. It must not write an incompatible local-only decision format.

## 12. Phase L7 — Restart and recovery

Test real persistence:

- close during idle project view;
- reopen and resume;
- recover after failed external dependency;
- recover after interrupted processing where supported;
- handle a removed/moved artifact honestly;
- handle an older project schema through the migration reader;
- handle an unsupported newer schema without corruption;
- preserve source and completed versions.

UI state may be cached for convenience, but Core project artifacts remain authority.

## 13. Preserve Deep and Quick paths

### Deep

```text
Detect → Diagnose → Separate → Transcribe/Structure
→ Plan → Edit → Mix/Master → Verify → Compare → Decide
```

### Quick

```text
Detect → Diagnose → explicit Quick consent
→ Process stereo → Verify → Compare → Decide
```

Local UI rules:

- Quick consent must be attributable and reversible before execution;
- Quick is visibly labeled `快速（仅立体声）`;
- Deep is visibly labeled `深度完成`;
- Quick does not unlock Plan;
- missing prerequisites explain what is missing;
- Deep overrides the earlier Quick choice once its prerequisites exist;
- neither path ends at render; both proceed to Verify, Compare and Decide.

## 14. Local runtime and CLI integration

The owner's preference is CLI-first execution with GUI-assisted review.

Studio may:

- invoke stable CLI/Core contracts;
- show the embedded terminal;
- generate or display agent plans;
- display machine-readable progress/events;
- allow advanced users to continue through CLI.

Studio must not require manual terminal commands for the ordinary loop when a stable capability is available.

Do not expose secrets or send private audio to cloud providers without explicit authorization.

## 15. Windows and real-device acceptance

Local is responsible for:

- Windows installed build;
- portable build;
- icon, fonts and layout;
- file picker and Unicode paths;
- Python/Core/FFmpeg runtime discovery;
- node-pty and embedded terminal;
- Codex/agent runtime invocation;
- actual audio device playback;
- A/B transport behavior;
- application restart;
- install/uninstall evidence.

Use:

```text
docs/tasks/MOODIFY_DESKTOP_LOCAL_ACCEPTANCE_001.md
```

as the release acceptance baseline.

## 16. Local tests

At minimum:

- existing Studio contracts;
- existing pipeline and Studio tests;
- adapter contract-version tests;
- Cloud golden-project rendering tests;
- old case compatibility;
- incomplete/missing artifact behavior;
- Quick/Deep view parity with Core state;
- no GUI-only stage advancement;
- version selector and history tests;
- playback transport state tests where headless simulation is valid;
- human decision payload tests;
- restart/recovery tests;
- packaged runtime tree inspection;
- Windows Setup/Portable regression;
- repository structure guard;
- `git diff --check`.

Manual required:

```text
window/layout
real audio import
real audio playback
A/B switching
audible glitches
human Accept/Revise/Reject understanding
installer/portable/uninstall
```

## 17. Contract requests to Cloud

When blocked, return a structured request:

```text
CONTRACT VERSION
LOCAL USER STORY
MISSING FIELD / COMMAND / STATE
WHY CURRENT DATA IS INSUFFICIENT
EXPECTED MACHINE-READABLE EXAMPLE
COMPATIBILITY IMPACT
TEST CASE
URGENCY
```

Do not patch Core from the Local branch unless the work is explicitly reassigned and isolated in its own commit/PR.

## 18. Coordination checkpoints

Local must stop and report at:

```text
L0 — current Studio UX audit complete
L1 — Project/Graph adapter passes Cloud fixtures
L2 — persistent project workspace usable
L3 — version review and A/B usable
L4 — human decision and revision loop persists
L5 — restart/recovery passes
L6 — Windows packaged acceptance passes
```

Local may begin L0 immediately. L1 and later require the corresponding Cloud contract checkpoint.

## 19. Forbidden work

Do not:

- add a second project schema;
- add a second production graph or state machine;
- put DSP in renderer/main-process code;
- calculate authoritative verification in UI;
- invent diagnosis findings;
- auto-select an A/B winner;
- auto-accept a version;
- make UI click state production truth;
- bypass Deep prerequisites;
- silently turn Quick into the default;
- redesign all screens before testing the current experience;
- rewrite Core from the Local branch;
- upload private audio or credentials;
- remove existing features merely because the new loop is incomplete.

## 20. Required Local PR sequence

Prefer:

```text
Local PR 1 — Studio UX reality audit and contract adapter skeleton
Local PR 2 — Core Project/Graph view integration
Local PR 3 — Persistent project workspace and version history
Local PR 4 — Playback/A-B/version review
Local PR 5 — Human decision and revision loop
Local PR 6 — Restart/recovery and Windows packaged acceptance
```

Use stacked PRs only when the dependency is explicit. Retarget to `main` after upstream contracts merge and rerun verification.

No auto-merge.

## 21. Local completion report

Return:

```text
BASE SHA / BRANCH / COMMITS / PRS
CURRENT UX AUDIT
CLOUD CONTRACT VERSION CONSUMED
PROJECT WORKSPACE RESULT
STATE PARITY RESULT
VERSION REVIEW RESULT
PLAYBACK / A-B RESULT
HUMAN DECISION RESULT
RESTART / RECOVERY RESULT
WINDOWS PACKAGE RESULT
TESTS
MANUAL EVIDENCE PATH
CONTRACT REQUESTS TO CLOUD
KNOWN LIMITATIONS
HUMAN_CHECK_REQUIRED
```

Local completion means a human can understand, hear, compare and decide on a version using shared Core truth. It does not mean all target Edit capabilities or phone delivery are implemented.
