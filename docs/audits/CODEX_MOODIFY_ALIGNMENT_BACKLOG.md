# Codex Moodify Product-Alignment Backlog

This backlog follows the independent audit. It is not an implementation authorization. Sizes are scope classes, not time estimates.

## P0 — Product definition violations

### P0-01 Enforce one canonical apply invariant

- **Problem:** CLI-v2 and app orchestrator apply audio without approval, required identity constraints, plan version or engine lock.
- **Evidence:** `cli_v2.main.cmd_run_execute`; runtime `unapproved_apply` returned exit 0/`completed`.
- **Risk:** Moodify can silently execute an artistic intervention.
- **Proposed change:** require canonical spec, approved plan digest, unchanged source hashes, supported plan schema and exact engine/capability digest before any executor call.
- **Affected:** `cli_v2`, domain approval/plan, Bridge spec, executor ports.
- **Tests:** one golden path plus negative tests for every conjunct; direct adapter bypass test.
- **Acceptance:** no public apply path reaches an engine without all invariant checks; failures are structured and fail-closed.
- **Dependency:** P0-02. **Scope:** XL.

### P0-02 Consolidate production case, spec, plan and decision identities

- **Problem:** Core project, Bridge case and Workspace models do not share a lifecycle or ID.
- **Evidence:** three plan/spec stores and incompatible schemas.
- **Risk:** approval and evidence can refer to different objects.
- **Proposed change:** versioned canonical case aggregate with immutable revisions and migration adapters.
- **Affected:** domain, Bridge ledger, CLI-v2 project store, runtime.
- **Tests:** serialization/migration, plan-digest binding, cross-surface ID trace.
- **Acceptance:** source → spec → analysis → plan → decision → run → verification is queryable by one stable case ID.
- **Dependency:** none. **Scope:** XL.

### P0-03 Make verification and evidence prerequisites of success

- **Problem:** execute reports `completed` before verification; empty evidence bundles can be written successfully.
- **Evidence:** runtime sequence and `app.evidence.aggregate_evidence` missing-source result.
- **Risk:** failed or unaudited assets appear complete.
- **Proposed change:** APPLIED/VERIFYING/VERIFIED/PACKAGED states; atomic evidence finalization; no `completed` alias before package seal.
- **Affected:** CLI-v2 run model, native renderer, evidence aggregator, stores.
- **Tests:** verification/evidence failure injection and interrupted-write recovery.
- **Acceptance:** missing/failed verification or evidence produces INCOMPLETE/FAILED only.
- **Dependency:** P0-02. **Scope:** L.

### P0-04 Compile identity constraints into plan and verification gates

- **Problem:** `OnePointSpec` constraints are not consumed by core planning; keyword conflict checks miss three of five required semantic probes.
- **Evidence:** serialized plan fields; static `detect_conflicts` pairs.
- **Risk:** desired change overrides identity.
- **Proposed change:** typed constraints, explicit conflict dispositions, measurable and human-only preservation criteria.
- **Affected:** Bridge schemas/services, planner, verification.
- **Tests:** all five required conflicts plus ambiguous/unmeasurable constraints.
- **Acceptance:** unresolved conflict blocks plan approval; every constraint has a verification disposition.
- **Dependency:** P0-02. **Scope:** XL.

### P0-05 Remove or gate public bypass paths

- **Problem:** `process`, `legacy-process`, direct DAW and `app.execute_plan` bypass canonical controls.
- **Evidence:** CLI dispatch and 16 passing v0.1/CLI tests.
- **Risk:** correct architecture can coexist with unsafe default behavior.
- **Proposed change:** route public mutations through application service; retain legacy as explicitly unsafe/manual compatibility mode until removed.
- **Affected:** `cli.py`, `v01_pipeline`, `app.orchestrator`, `cli_daw`.
- **Tests:** enumerate all CLI mutation commands and assert invariant middleware reached.
- **Acceptance:** no undocumented mutation endpoint; legacy invocation cannot claim verified production status.
- **Dependency:** P0-01. **Scope:** L.

## P1 — Trust and safety of production

### P1-01 Build a sealed evidence manifest

- **Problem:** plan, render, approval, measurement and spectral evidence are separate.
- **Evidence:** runtime output directory contains audio plus render JSON only.
- **Risk:** chain of custody cannot be proven.
- **Change:** content-address every artifact; include source/output/plan/decision/versions/environment/times/warnings and bundle status.
- **Modules:** evidence, spectral, delivery, Bridge PPE.
- **Tests:** tamper each referenced artifact; wrong-output and fabricated-approval cases.
- **Acceptance:** manifest validation detects every mutation/missing required member.
- **Dependency:** P0-02/03. **Scope:** L.

### P1-02 Add execution staging, idempotency and recovery

- **Problem:** same path is rejected but a new path duplicates a completed run; renderer writes into final directory.
- **Evidence:** retry_same_output exit 2; retry_new_output exit 0/new run ID.
- **Risk:** duplicates and partial assets after interruption.
- **Change:** idempotency key based on approved case revision; temp workspace; atomic promote; resumable failure record.
- **Modules:** run service, project store, engines.
- **Tests:** kill at each phase, retry same key, concurrent duplicate request.
- **Acceptance:** one logical execution per key and no partial final package.
- **Dependency:** P0-01. **Scope:** L.

### P1-03 Record and validate complete engine environment

- **Problem:** plans/evidence omit binary/package versions; shell availability differs from prior installation claims.
- **Evidence:** `render_evidence.json` only says `native`; shell cannot find SoX/Rubber Band; installed metadata says Moodify 0.1.0 while pyproject says 2.0.0.
- **Risk:** irreproducible or misidentified output.
- **Change:** capability digest, executable absolute path, version, build, plugin versions and environment fingerprint.
- **Modules:** adapters, version command, evidence.
- **Tests:** simulated version drift blocks apply.
- **Acceptance:** approved environment mismatch requires reapproval/revalidation.
- **Dependency:** P0-01. **Scope:** M.

### P1-04 Add production triage and stop dispositions

- **Problem:** no canonical model-origin/correctability/uncertainty/reject classification.
- **Evidence:** CLI plan creates gain plan for any imported asset.
- **Risk:** post-processing is implied to fix non-correctable work.
- **Change:** diagnosis disposition and eligibility gate.
- **Modules:** analysis domain, planner, case lifecycle.
- **Tests:** reject, manual-only, uncertain and assisted cases.
- **Acceptance:** ineligible cases cannot auto-plan/apply.
- **Dependency:** P0-02. **Scope:** L.

## P2 — Architecture separation

### P2-01 One executor port and adapter conformance suite

- **Problem:** duplicate adapter interfaces/evidence types and incomplete capability rejection.
- **Evidence:** `ports/processing.py`, `adapters/open_source_toolchain.py`, `cli_daw/adapters/*`.
- **Risk:** swapping engines changes semantics and evidence.
- **Change:** one product action vocabulary, capability validation and uniform execution evidence.
- **Modules:** ports/adapters/cli_daw.
- **Tests:** same action through native and test-double/SoX with identical approval/evidence contract.
- **Acceptance:** unsupported action fails before subprocess; no silent fallback/no-op.
- **Dependency:** canonical plan. **Scope:** L.

### P2-02 One analysis and verification protocol

- **Problem:** v0.1, science and app analysis outputs are incompatible.
- **Evidence:** separate packages and artifact schemas.
- **Risk:** planner and evidence select convenient metrics.
- **Change:** versioned before/after measurement schema and tolerances.
- **Modules:** analysis, spectral, v01, verification.
- **Tests:** cross-engine fixture and schema conformance.
- **Acceptance:** every plan criterion maps to a named measurement or explicit human review.
- **Dependency:** P0-04. **Scope:** XL.

## P3 — Agent and operational readiness

### P3-01 Complete the case lifecycle CLI/API

- **Problem:** no canonical submit-spec, analyze, inspect, approve/reject, status, recover or export commands.
- **Evidence:** CLI-v2 exposes only project/asset/plan/run.
- **Risk:** agents must mutate files or bypass human gates.
- **Change:** stable JSON request/response schemas and lifecycle commands.
- **Modules:** CLI-v2/application services.
- **Tests:** noninteractive ten-step agent contract and stable exit codes.
- **Acceptance:** full approved case trace without GUI or direct JSON edits.
- **Dependency:** P0-01/02/03. **Scope:** L.

### P3-02 Add concurrency and fleet-level operational tests

- **Problem:** no batch/idempotency/status/recovery proof.
- **Evidence:** single-source synthetic test only.
- **Risk:** production automation races or duplicates work.
- **Change:** job queue contract, locks, cancellation and observability.
- **Modules:** runtime, store, CLI/API.
- **Tests:** concurrent cases, cancellation, restart, Unicode paths.
- **Acceptance:** deterministic state transitions under concurrency.
- **Dependency:** P1-02. **Scope:** XL.

## P4 — Documentation and maintainability

### P4-01 Reconcile version, license and capability claims

- **Problem:** installed metadata, pyproject, README, Bridge license and handoffs disagree.
- **Evidence:** runtime Moodify 0.1.0 vs package declaration 2.0.0; unverified handoff claims.
- **Risk:** false user expectations and release ambiguity.
- **Change:** single build-version source; generated capability page; explicit package/license boundaries.
- **Modules:** packaging/docs/CI.
- **Tests:** release metadata and documented-command smoke tests.
- **Acceptance:** installed version and documented capabilities match tested build.
- **Dependency:** none. **Scope:** M.

### P4-02 Restore domain test importability and audit CI

- **Problem:** approval/audio-version/treatment-plan tests fail collection because public exports are missing; Bridge test environment is not runnable as configured.
- **Evidence:** `core_tests.xml`, `bridge_tests.xml`.
- **Risk:** critical models decay without enforcement evidence.
- **Change:** repair package exports/environment lock and add alignment invariant suite.
- **Modules:** `domain/__init__.py`, Bridge environment, CI.
- **Tests:** the currently failing collections plus P0 invariant tests.
- **Acceptance:** critical suite collects and passes in a clean documented environment.
- **Dependency:** none. **Scope:** M.
