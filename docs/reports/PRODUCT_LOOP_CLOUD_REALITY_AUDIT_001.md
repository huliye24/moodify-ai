# PRODUCT_LOOP_CLOUD_REALITY_AUDIT_001 — Phase C0 Reality and Authority Audit

**Task:** `MOODIFY_PRODUCT_REALIGNMENT_CLOUD_001` §5 (Phase C0)
**Date:** 2026-10-04
**Branch / base:** `cloud/product-loop-core-001` @ `1dd5b2e14cdc67e673c26a2aa62e556c12066b20` (`origin/main`)

**Status: STOP — awaiting human review before any production authority moves (§5, §14).**

No implementation was started. No file under `moodify-core-package/`, `protocol/`, or
`moodify-desktop/` was modified. This audit is the only deliverable of C0.

---

## 0. Two findings that change how this task must be executed

### 0.1 Three of the six delivery phases are already in flight on other branches

| In-flight PR | Lands | Overlaps |
|---|---|---|
| **#44** `moodify/project/{models,service,errors}.py`, extends `contracts/ids.py`, doc `docs/PROJECT_MODEL_0_1.md` | new Core package + contract doc | **§7 Phase C2 — Project Model v0.1** |
| **#42** `moodify/capabilities/{registry,models,builtin,failures}.py` | new Core package | **§10 Phase C5 — capability registry** |
| **#43** `capabilities/{policy,router}.py` (stacked on #42) | extends #42 | **§10 — provider selection** |
| **#41** `docs/ecosystem/*` capability map + provider manifest draft | docs only | **§6 Phase C1 (partial)** |

`moodify/project/` and `moodify/capabilities/` do **not** exist on `main`. If this track implements
§7 and §10 as written, it creates a second Project Model and a second capability registry —
directly against §3 ("there may be only one authority") and §15 ("do not create a second Core").

**Nothing in C0–C5 should be implemented for those two phases until this is resolved.** This is
`HUMAN_DECISION_REQUIRED #1`.

### 0.2 The parent direction document does not exist

§0 names `docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_001.md` as the parent. It is not in the repository
(`docs/tasks/` contains only the two desktop acceptance tasks). §4 anticipated this case for *Canon*
commits; it did not anticipate the parent being absent entirely. The Canon change
(`CANON_CHANGE = YES`) therefore has no upstream text to conform to. This is
`HUMAN_DECISION_REQUIRED #2`.

---

## AUTHORITY MAP

Who owns each fact **today**, on `main`.

### Canonical contracts (Core, single-writer, generated)

```text
moodify-core-package/src/moodify/contracts/*.py          ← the definitions
      │ scripts/generate_canonical_schemas.py             ← generator
      ▼
schemas/canonical/*.v1.schema.json                       ← generated, do-not-hand-edit
```

`protocol/schemas/README.md` states the ownership rule and records that four duplicate copies each of
the contribution/evidence/reputation schemas existed before 2026-10-03.

| Contract | Python model | Generated schema |
|---|---|---|
| `ProductionCase` | `contracts/production_case.py` | `production_case.v1.schema.json` |
| `MeasurementRecord` | `contracts/measurement_record.py` | `measurement_record.v1.schema.json` |
| `EvidenceArtifact` | `contracts/evidence_artifact.py` | `evidence_artifact.v1.schema.json` |
| `Rule` | `contracts/rule.py` | `rule.v1.schema.json` |
| `MachineFinding` | `contracts/machine_finding.py` | `machine_finding.v1.schema.json` |

Shared base `contracts/base.py`: `CanonicalModel` (`frozen=True`, `extra="forbid"`),
`SchemaVersion = Literal["1.0"]`, plus `utc_now`, `ensure_json_safe`, `freeze_json_value`.

### Production state — nine vocabularies, no shared constant

| # | Authority | Path | Vocabulary | Derived from |
|---|---|---|---|---|
| A | **Desktop case stage (live)** | `moodify-desktop/src/pipeline.js` | `IMPORTED, ANALYZED, DIAGNOSED, SEPARATED, STRUCTURED, READY_FOR_PLAN, PLANNED, RENDERED, VERIFIED, CHOSEN, EXPORTED` (11) | **disk artifacts, re-derived every read** |
| B | Desktop UI mirror | `moodify-desktop/renderer/app.js` | `analyze, diagnose, separate, structure, plan, finish` (6, lowercase) | consumes A's snapshot; **re-encodes the gates** |
| C | Cloud job lifecycle | `moodify-core-package/src/moodify/data_plane/control.py` | `CREATED, QUEUED, RUNNING, VERIFYING, RETRY_WAIT, READY, FAILED, CANCELED` (8) | stored DB field; self-declared "唯一 Job 生命周期权威" |
| D | Cloud stage progress | `…/data_plane/pipeline.py` | `ACQUIRE, VALIDATE, STEM, ANALYZE, JUDGE, INTERVENE, PROFILE, RENDER, VERIFY, REGISTER` (10) | execution progress |
| E | Node worker queue | `…/node/models.py`, `node/queue.py` | `QUEUED, RUNNING, SUCCEEDED, FAILED` (4) | SQL row |
| F | Reconstruction job | `…/reconstruction_job/contract.py` | `QUEUED … SOURCE_WINS, FAILED, CANCELLED` (11) | stored field |
| G | Case lifecycle / authority | `…/contracts/production_case.py` | `CREATED, ACTIVE, AWAITING_HUMAN, COMPLETED, FAILED, CANCELLED` + `SYSTEM, ALGORITHM, HUMAN_REQUIRED, HUMAN_APPROVED, HUMAN_REJECTED` | stored fields |
| H | Case outcome gate | `…/authority/pipeline.py` | `MACHINE_DECIDED` vs escalation | `case_manifest.json` + comparison guardrails |
| I | Legacy workflow engine | `…/orchestration/workflow_engine.py` | numeric `Phase 0…6`, `PhaseStatus` | classified LEGACY in `docs/canon/INTERNAL_SYSTEMS.md` |

**The Desktop shell calls exactly one of these for stage purposes: A.** `main.js` requires
`pipeline.js` and exposes it over IPC (`pipeline:snapshot|diagnose|diagnosis|note|context|readContext|setFinishMode`).
No Core Python state machine is invoked by the shell for stage derivation.

### CLI surface

Three installed entry points (`moodify-core-package/pyproject.toml`): `moodify`, `moodify-node`,
`moodify-reconstruction`. The legacy `moodify.cli` is **not installed** and is referenced by no
script, workflow or shell in the repo.

**No installed entry point has a "project" concept.** The nearest analogues are the case archive
(`<cases-root>/case_<id>/`) and the reconstruction job workspace. §8's suggested
`moodify project inspect <project>` therefore has **no existing naming convention to follow**; the
task's own instruction to "check existing CLI conventions" resolves to: *there is a `case`
convention and no `project` convention.*

### Provider abstraction — one real one, several partial ones

| Thing | Path | Nature |
|---|---|---|
| **The only true provider abstraction** | `moodify-desktop/src/backends/{index,local}.js` | `getBackend(mode)` over `{local, cloud}`; cloud is `implemented: false` and returns an explicit not-implemented error rather than falling back |
| Real Core registry | `…/mix_graph/providers/` | `base.NodeProvider`, `_PROVIDERS`, `get_provider()` — one per node type |
| Static shell list | `moodify-desktop/src/pipeline.js` `CAPABILITIES` | frozen `id/kind/core_command/stage` entries emitted into `context.json` |
| Registries with `missing_value_policy` | `auditory/measurement_registry.py`, `auditory/representation/feature_registry.py` | measurement/feature registries |
| Audit tool (**drifted**) | `auditory/inventory.py` | classifies modules into `docs/auditory_intelligence/current_capability_inventory.*`; its `CLASSIFICATION` map still names modules that no longer exist (`features`, `perception`, `score_engine`, `transcription`, `capability_registry`, `cli_v2`) |

**No product-level capability registry exists.** Status vocabularies live in docs
(`docs/REPOSITORY_STATUS.md`, `docs/evidence/runtime/05_MOODIFY_TRUTH_TABLE.*`) and in scattered
in-code markers (`mix_graph/schema.py STATUS="EXPERIMENTAL"`, `auditory/judgment.py
CALIBRATION_EXPERIMENTAL`, `mrs/benchmark.py "EXPERIMENTAL_RULE_BASED"`).

---

## DUPLICATE AUTHORITIES

Ordered by how likely each is to cause real divergence.

### D1 — `ProductionCase`: one model, three writers, two filenames

```text
contracts/production_case.py                 (the only definition)
  ← release.py                       → case.json
  ← data_factory/runner.py           → production_case.json
  ← reconstruction_job/engine.py     → production_case.json
```

Same record, three write paths, and two different filenames for it. A reader cannot know which file
to open without knowing which subsystem produced the case.

### D2 — Production ordering is **contradictory**, not merely differently named

```text
Desktop pipeline.js     ANALYZED → DIAGNOSED → SEPARATED → STRUCTURED
Core data_plane         STEM     → ANALYZE
```

The Desktop separates *after* diagnosing; the cloud plane separates *before* analysing. These cannot
both be the canonical order. Any read model must pick one and justify it — this is not a naming
reconciliation.

### D3 — Desktop stage derivation exists twice, in two vocabularies

`renderer/app.js` re-encodes the stage list and the gates (`stageUnlocked`, `stageLockReason`,
`enterPipeline`), with a comment stating "Mirrors src/pipeline.js gates()". 11 uppercase states vs 6
lowercase ids, two independently evolving gate implementations. §3 names `pipeline.js`; it does not
name this second encoding, which is the one most likely to be missed.

### D4 — Studio owns nine contracts as unvalidated JS object literals

```text
moodify.studio.meta/0.1, .selection/0.1                     moodify-desktop/src/studio.js
moodify.studio.pipeline/0.1, .diagnosis/0.1,
            .context/0.1, .plan/0.1                         moodify-desktop/src/pipeline.js
moodify.studio.export/0.1                                   moodify-desktop/src/main.js
moodify.studio.version-evidence/0.1                         moodify-desktop/src/backends/local.js
moodify.sound/0.2 (job submitted)                           moodify-desktop/src/backends/local.js
```

§3 says not to keep `pipeline.js` as a second long-term authority. The migration surface is nine
contracts across four files, not one file.

### D5 — Protocol version strings re-declared independently

`moodify.sound/0.1` and `/0.2` appear in `sound_protocol.py` **and** as a literal in
`auditory/protocol_report.py` **and** in a desktop test fixture. A change in one place does not
propagate.

### D6 — Contribution schemas: a dead file, a live inline dict, and an uninitialised validator

`contribution/schema/contribution.schema.json` is never really loaded (`_load_schema()` returns `{}`);
the live definition is an inline Python dict. `evidence.schema.json` is referenced by a validator
attribute that is **never assigned** — a latent `AttributeError` on the evidence path.
`reputation-evidence.schema.json` has no referrer.

### D7 — `"1.0"` is reused by unrelated records with no shared constant

`auditory/inventory.py`, `data_factory/*`, `authority/escalation.py`, `tools/temporal_texture/*`,
the golden case: all say `schema_version "1.0"`, none share a constant, and they are not the same
schema. Likewise `schema_version: 1` (integer) is repeated across five `ops/ear_batch/*` modules,
each defining its own shape.

### D8 — Canon documents contradict each other and the code

`docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md` restates `pipeline.js` (minus `IMPORTED`), while
`docs/canon/INTERNAL_SYSTEMS.md` gives a different cloud topology
(`Intake → Identify → Analyze → Stem → Judge → …`). The canon already disagrees with itself.

---

## SCHEMA INVENTORY

### Core canonical (versions, generated)

`schemas/canonical/{production_case,measurement_record,evidence_artifact,rule,machine_finding}.v1.schema.json`
— `schema_version` const `"1.0"`, no `$id`, generated from the Pydantic models.

### Core runtime-written records

| Identifier | Writer | Notes |
|---|---|---|
| `moodify.sound/0.1`, `/0.2` job JSON | `sound_protocol.py` | exact key sets per type; unknown keys rejected |
| `moodify.msp_report/0.2` | `auditory/protocol_report.py` | inline draft 2020-12 dict; validates `report.json` |
| `moodify.mix_graph/0.1` | `mix_graph/schema.py` + `graph.py` | hand-rolled validator; `STATUS = "EXPERIMENTAL"` |
| `moodify.mix_graph.evidence/0.1` | `mix_graph/session.py` | sidecar `*.evidence.json`, no validator |
| `moodify.ab_compare/0.1`, `…choice/0.1` | `ab_compare.py` | comparison artifact + append-only choice ledger |
| `era-diagnostic-v0.1` | `era_diagnostic/report.py` | + dataclass in `era_diagnostic/contract.py` |
| `local-cache-v1` | `auditory/execution/cache.py` | per-node `manifest.json` |
| measurement registry (`"1.0"`, `mfy-measurement-v1`) | `configs/measurement_registry_v1.yaml` | YAML, validated in code |
| `MFY-DATA-PROTOCOL-001` case layout (`"1.0"`) | `data_factory/runner.py` | spec frozen in `docs/contracts/DATA_PROTOCOL_V1.md` |
| scan manifest (unversioned) | `auditory/manifests.py` | no `schema_version` field |

### Studio (`moodify-desktop`)

The nine `moodify.studio.*` / `moodify.sound/0.2` literals listed in **D4**. The first three are
mirrored, non-normatively, in `docs/protocol/MOODIFY_STUDIO_CONTEXT_0_1.md`.

### Contribution

`mood://protocol/contribution/1.0.0` (live inline dict), plus two orphaned schema files — see **D6**.

### Other families

Treatment records (`"0.1.0"`, writer-script-defined, no JSON Schema, 30 documents in
`treatment_records/`), `ops/ear_batch/*` (`schema_version: 1` int, five modules), pilot manifests,
temporal-texture reports, `authority/scope_contract.py`, `authority/escalation.py`,
`moodify-music-package` 16-table SQLAlchemy model, `moodify_runtime/p11_commerce` dataclasses,
`shared-fixtures/{track,error}.json`, four `deliverables/releases/*/RELEASE_MANIFEST.json`, and the
MAMSE experimental family (`mamse-0NN-{manifest,evidence,*-features}-v1`).

**Version strings in use:** `"1.0"`, `"1.0.0"`, `"0.1.0"`, `1` (int), `"local-cache-v1"`,
`"era-diagnostic-v0.1"`, `"moodify.msp_report/0.2"`, `"moodify.sound/0.1|0.2"`,
`"moodify.mix_graph/0.1"`, `"moodify.ab_compare/0.1"`, `"mamse-0NN-*-v1"`.

---

## IMPLEMENTED CAPABILITIES

Status is evidence-based; nothing is promoted to SUPPORTED without a test or a reachable command.

| Capability id | Status | Evidence |
|---|---|---|
| `audio.ingest.decode` | SUPPORTED | every path uses it; `tests/auditory/test_decode_unicode_paths.py` |
| `audio.analyze.scan` | SUPPORTED (report schema EXPERIMENTAL) | `moodify analyze/demo`, `protocol process`; `tests/test_msp02_analysis.py`, `tests/test_release_api.py` |
| `audio.measure.loudness` | SUPPORTED | reached via analyze/compare; `tests/auditory/test_measurement_correctness.py` |
| `audio.compare.ab` (+ human choice ledger) | SUPPORTED | `moodify compare prepare/choose/show`; `tests/test_ab_compare.py` |
| `audio.compare.protocol02` | EXPERIMENTAL | only as a 0.2 job; `tests/test_msp02_compare.py` |
| `audio.verify.before_after` | SUPPORTED | `moodify finishing verify`; `tests/mix_graph/*` (golden test **skips**: `demo/input/example.mp3` absent from this worktree) |
| `audio.finish.mixgraph` | EXPERIMENTAL (`schema.py STATUS`) | `moodify finishing new/render`; `tests/mix_graph/*` |
| `audio.process.preset` | SUPPORTED | `protocol process`; desktop `studio:process`; desktop `test-studio.js` runs the **real CLI, no mocks** |
| `audio.export.deliver` | SUPPORTED | `moodify finishing export`; `tests/mix_graph/test_cli.py` |
| `diagnosis.v01.rules` | SUPPORTED | runs inside `process_audio`; `tests/test_v01_analyzer_diagnostics_exporter.py` |
| `diagnosis.deep18` | implemented, **unreachable from shell** | only legacy CLI; `tests/test_diagnosis.py` |
| `structure.separate.preview` | shell-local, preview grade only | `dsp_separate.py`; `test-pipeline.js` asserts `PREVIEW_NOT_MASTERING_GRADE` |
| `structure.separate.stems.cloud` | implemented, unreachable, needs paid key | `tests/stems/test_client.py` (mock transport) |
| `structure.transcribe.midi` | **absent in Core**; shell-local via external binary | no Core test |
| `structure.score.musicxml` | **absent in Core**; shell-local | discovery-only test |
| `plan.reconstruction.objective` | implemented, **isolated from shell** | 18 test files under `tests/reconstruction*` |
| `plan.studio.draft` | SUPPORTED (shell) | always `DRAFT_PLAN_NOT_EXECUTED`; `test-pipeline.js` |
| `plan.ai.decoder` (Codex) | shell feature | contract test only, no behavioural test |
| `eval.mrs.rulebased` | EXPERIMENTAL | `tests/mrs/*`; the FastAPI `process` route returns 501 by design |
| `eval.llm.threejudge` | implemented, **no tests, unreachable** | requires a DeepSeek key |
| `verify.listening.mushra` | EXPERIMENTAL, no entry point | `tests/listening/*` |
| `verify.identity_guard`, `diagnosis.era`, `intervention.primitives` | implemented + tested, only legacy CLI or no CLI | `tests/identity_guard/*`, `tests/era_diagnostic/*`, `tests/intervention/*` |
| `cloud.production.pipeline` | implemented + tested, cloud-side | fails without injected adapters (`SEPARATOR_UNAVAILABLE`, `RENDERER_UNAVAILABLE`) |
| `report.render.bundle` | SUPPORTED | `moodify report`/`demo`; `tests/ui/*` |

**What the Desktop shell actually invokes:** five Core commands — `release_cli demo` (analyze),
`ui.chart_export`, `finishing new`+`render`, `finishing export`, `compare show/prepare/choose`,
`protocol validate`+`process` — plus three non-Core tools (`dsp_separate.py`, external
`basic-pitch`, `midi_to_musicxml.py`). `pipeline:diagnose` and the research/evidence ledger never
touch Core.

**Large Core surface is implemented but unreachable from the shell:** `diagnosis/` (18-param),
`evaluation/` + `llm/` + `calibration/`, `mrs/`, `stems/`, `listening/`, `identity_guard/`,
`era_diagnostic/`, `intervention/`, all four `reconstruction*` packages (including their own CLI and
HTTP API), `data_plane/` + `node/` + `data_factory/`, and the legacy `orchestration/`.

---

## TARGET / ABSENT CAPABILITIES

| Capability | Status | Basis |
|---|---|---|
| `structure.separate.model` (Demucs / BS-RoFormer) | **TARGET** | `pyproject.toml` declares a `separation` extra; **no code imports it**; `docs/REPOSITORY_STATUS.md` marks 精细分离引擎 TARGET |
| `app.playback.render` (device-adaptive playback) | **TARGET** | no `playback/` package; proposed only in `docs/MOODIFY_CAPABILITY_FIRST_DESIGN.md` |
| `structure.transcribe.midi` / `structure.score.musicxml` in Core | **ABSENT** | shell-local only; §10's "only register supported execution when runtime evidence exists" therefore excludes them from a Core registry today |
| `structure.separate.stems.cloud` in a container | **UNAVAILABLE_IN_ENVIRONMENT** | requires a paid lalal.ai licence key; must not be registered as supported |
| `eval.llm.threejudge` | **UNAVAILABLE_IN_ENVIRONMENT** | requires a DeepSeek key |

§10's five-value vocabulary (`SUPPORTED`, `EXPERIMENTAL`, `TARGET`, `ABSENT`,
`UNAVAILABLE_IN_ENVIRONMENT`) maps cleanly onto this table — the vocabulary is sound and the data
to populate it already exists, scattered across docs and in-code markers.

---

## MIGRATION INPUTS

### Two incompatible case layouts already on disk

```text
Studio case            <cases-root>/case_<id>/
                       case.json, source_path.json, measurements.json, evidence.json,
                       judgment_rules.json, auditory_report.json, report.{json,md,html},
                       charts/, scan/, stems/, midi/, score/, studio/{pipeline,diagnosis,
                       context,plans,versions,selection,verification,export,finish_mode}.json

data-factory node      <output_root>/cases/<case_id>/
                       00_source, 01_source_scan, 02_plans, 03_candidates, 04_after_scan,
                       05_comparison, 06_human_review, 07_learning + production_case.json,
                       case_manifest.json
```

Both write a `ProductionCase`-shaped record under a different filename. A verified real instance of
the Studio layout exists (a 48 kHz stereo case produced by the shipped Windows build), which is the
best migration fixture available outside the repo.

### In-repo fixtures

- `examples/golden_case/` — `production_case.json`, `case_manifest.json`,
  `01_source_scan/scan_manifest.json`, `02_plans/plan_{A,B,C}.json`,
  `06_human_review/review.json`, `07_learning/training_record.json`
- `shared-fixtures/{track,error}.json`
- `moodify-core-package/migrations/`

### Migration risks

1. **`extra="forbid"`** on `CanonicalModel` means an old reader **rejects** any record carrying a new
   field. §7's "unknown future fields can be handled according to a documented compatibility rule" is
   currently answered *by rejection* — the compatibility rule does not exist yet.
2. **`SchemaVersion = Literal["1.0"]`** hard-codes a single valid version. There is no mechanism to
   accept `1.1` without editing the type.
3. **The `audio.verify.before_after` golden test skips** because `demo/input/example.mp3` is not in
   the repo. A green suite therefore does not currently exercise that path.
4. **`auditory/inventory.py` has drifted** — its classification map names modules that no longer
   exist, so it is not a trustworthy capability source.
5. Any read model that derives state from disk must reproduce `pipeline.js`'s behaviour on cases
   where artifacts were **deleted**; that behaviour is defined by re-derivation, and no Core
   equivalent exists to compare against.

---

## PROPOSED CONTRACT BOUNDARY

Proposed for review; **not implemented**.

```text
CORE OWNS (single writer, versioned, generated schemas)
  contracts/          existing five canonical v1 contracts (extend, do not replace)
  project/            Project Model: attempt/version layer  ← see §7 gap below
  graph/              Production Graph read model           ← derived, never stored as truth
  capability/         capability ids + status vocabulary     ← see HUMAN_DECISION #1
  verify/             technical verification facts
  compare/            comparison facts (exists as ab_compare.py — extend, do not replace)

DESKTOP CONSUMES (no independent authority)
  pipeline.js         becomes a thin client of the Core read model, or is deleted
  renderer/app.js     stops re-encoding gates; renders what Core reports
  studio/*.json       becomes a cache of Core-owned records, not a definition
```

### The §7 gap, precisely

`ProductionCase` already provides `case_id`, `source_id`, `evidence_ids`, `authority_state`
(including `AWAITING_HUMAN`) and `parent_case_id`. What §7 asks for and the canonical layer does
**not** have is the **attempt / version layer**:

```text
absent today   attempt_id / version_id, parent_version_id
               capability execution records, parameters, provider metadata
               per-attempt input/output hashes
               verification state, comparison references
               failure / recovery state
present today  case_id, source_id, evidence_ids, authority_state, parent_case_id
               schema_version, created_at (in CanonicalModel)
```

That layer is the substantive new contract work in C2 — and it is exactly what PR #44 also builds.

### §8 is a port with a parity proof, not a new design

Every invariant §8 lists **is already implemented and in production use in
`moodify-desktop/src/pipeline.js`**:

| §8 requirement | `pipeline.js` today |
|---|---|
| diagnosis follows real Core analysis | `inspect()` reads `report.json` + `studio/diagnosis.json` |
| Deep planning requires stems **and** MIDI | `deepReady = analyzed && diagnosed && separated && structured`; `structured = info.hasMidi` |
| MusicXML does not replace MIDI | `structured` keys off `.mid/.midi` only |
| Deep finishing requires a real plan artifact | `canFinishDeep = deepReady && f.planned` |
| Quick finishing requires explicit human opt-in | `studio/finish_mode.json` = `QUICK_STEREO_ONLY` |
| Quick does not unlock Deep planning | `canPlan = deepReady` |
| Deep takes precedence once prerequisites exist | gate ordering in `gates()` |
| deleting an artifact moves the project backward | state is re-derived from disk on every read |
| UI flags cannot advance canonical state | `recordStage()` output is explicitly never read as truth |

The remaining design question §8 must answer is **D2 — which ordering is canonical**, because
`pipeline.js` and `data_plane/pipeline.py` disagree and neither is obviously right.

---

## ROLLBACK PLAN

C0 changed nothing, so the current rollback is that there is nothing to roll back.

For the phases that follow, the proposed rollback posture (to be confirmed before C2):

1. **Additive only.** New Core packages (`project/`, `graph/`) must not modify or delete the
   existing canonical contracts; a change to `contracts/*` is a separate, reviewable PR.
2. **Dual-read before dual-write.** The read model is proven to agree with `pipeline.js` on the
   golden case **and** on a real shipped-build case before the shell is switched to it. `pipeline.js`
   is retained as the oracle until parity is demonstrated, per §3.
3. **No deletion until parity.** `pipeline.js` and `renderer/app.js`'s gate encoding are deleted only
   after the Core read model is proven, in a dedicated commit that is revertible on its own.
4. **Existing cases stay readable.** Every migration step must read a case produced by the *current*
   shipped build. If a step cannot, it is not ready.
5. **Version bump on any break.** Breaking a handed-off contract (§13) requires an explicit version
   change, a migration note and updated examples.

---

## HUMAN_DECISION_REQUIRED

### #1 — Adopt #41–#44 as the canonical baseline, or supersede them?

`moodify/project/` (#44) and `moodify/capabilities/` (#42/#43) are in flight and land exactly where
§7 and §10 would. Implementing C2/C5 as written creates two authorities for each.

Options, with consequences:

- **(a) Adopt and extend.** C2 reviews #44, supplies only the missing attempt/version layer; C5
  reviews #42/#43 and supplies the status vocabulary and evidence bar. Fastest, single authority,
  but this track inherits another track's design decisions.
- **(b) Supersede.** This track designs both and #44/#42/#43 are closed. Cleanest design ownership;
  discards work already done and risks two competing artefacts landing first.
- **(c) Merge the tracks.** One owner for §7 + §10, whichever track that is. Requires the parent
  coordination decision that does not exist today (see #2).

**No C2/C5 work will start until this is answered.**

### #2 — The parent direction document is missing

`docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_001.md` is referenced by §0 but absent from the repo. Which
is true: (a) it is meant to be committed first, (b) the reference is stale and this task *is* the
parent, or (c) it lives elsewhere and needs to be added?

### #3 — Which production ordering is canonical?

`pipeline.js` says `ANALYZE → … → SEPARATE`; `data_plane/pipeline.py` says `STEM → ANALYZE`. A read
model cannot be written until one is chosen. This is a product decision, not a naming one.

### #4 — Does the shipped shell remain the parity oracle, and for how long?

§3 says `pipeline.js` is migration input and oracle "until the Core read model is proven". The exit
condition is not defined. Proposal: parity is proven when the Core read model reproduces
`pipeline.js`'s stage and gate decisions for every case in `examples/golden_case/` plus the real
shipped-build case, and the shell has run against it for one release cycle.

### #5 — Scope of the Canon PR (§6)

`CANON_CHANGE = YES`, and §6 requires a dedicated reviewable PR. Given D8 (the canon already
contradicts itself in two documents), does the Canon PR *also* reconcile
`docs/canon/INTERNAL_SYSTEMS.md` against `docs/canon/STUDIO_PRODUCTION_PIPELINE_V3.md`, or is that
out of scope and deferred?

---

## NEXT

C0 is complete. Per §5 and §14, this track **stops here** for human review before moving production
authority.

Nothing in C1–C5 has been started. The next Cloud deliverable depends entirely on decision #1:
if (a) adopt-and-extend, the next deliverable is the C1 Canon proposal written *against* #44/#42/#43;
if (b) supersede, the next deliverable is a design document that first justifies the replacement.

**Cloud completion report fields intentionally not filled:** `PROJECT MODEL VERSION`,
`PRODUCTION GRAPH PARITY`, `CLI CONTRACT`, `DOCKER RESULT` — no implementation exists yet.
