# Moodify — Project Roadmap

## Strategic anchor — 2026-07-30

Moodify will evolve from the sealed Workspace v2 baseline into headless
music-processing infrastructure for music companies. Development remains
focused on audio production; creator communication, talent evaluation,
artistic positioning, signing, release, and artist operations are outside the
Moodify boundary and belong to the operating company.

Canonical definition:
`docs/strategy/MOODIFY_MUSIC_PROCESSING_INFRASTRUCTURE.md`

Cross-version engineering standard:
`docs/strategy/MOODIFY_ENGINEERING_THICKNESS_STANDARD.md`

Development constitution:
`docs/strategy/MOODIFY_CIVILIZATIONAL_DEVELOPMENT_MODEL.md`

## Annual release model

Moodify targets one formally sealed stable release per calendar year. Internal
experiments, alpha builds, betas, release candidates, and service packs may be
created as needed, but they do not replace the annual release gate.

```text
Q1 audit/foundation
-> Q2 build/instrument
-> Q3 validate/accumulate
-> Q4 harden/seal
-> Moodify YYYY Annual Stable
```

The default operating cadence is four focused hours per day. Each day advances
one atomic, independently reviewable task and reserves time for verification,
evidence, inheritance, and handoff. Delivery dates must not be protected by
weakening the annual stability, compatibility, or evidence gates.

## Permanent accumulation track

Every roadmap phase must produce three parallel outputs:

```text
production result + reproducible evidence + inherited capability
```

A phase is not complete merely because its feature set works. It must also
preserve failure cases, decision reasons, standard evolution, craft evidence,
and a reproducible starting point for the next phase. Code and model upgrades
must not silently break the readability or reproducibility of prior projects.

Mandatory cross-phase gates:

- `G-Result`: a concrete result exists;
- `G-Evidence`: the result can be audited and reproduced;
- `G-Boundary`: limitations and failure conditions are explicit;
- `G-Inheritance`: the work updates product history, failure knowledge,
  standards, or craft memory;
- `G-Succession`: another operator can continue from the recorded state.

## Post-MVP execution path

### Phase 1 — Prove the production result

Goal: prove that the current processing line produces reliable, audible, and
repeatable improvements on real production material.

- expand real-song, genre, vocal, and failure-case calibration sets;
- run loudness-matched professional listening tests;
- calibrate MRS and technical gates against human engineering judgment;
- measure pass rate, rework rate, processing time, cost, and failure recovery;
- require reproducible evidence bundles for every accepted production result.
- establish the first Product History, Failure/Boundary, Standard Evolution,
  and Craft Evidence ledgers using lightweight repository-native records;
- repair summary-to-source inconsistencies before using aggregate statistics;
- retain rejected candidates and human rejection reasons as first-class evidence.

Exit gate: the same ProductionSpec can be executed repeatedly within defined
quality tolerances, and professional reviewers prefer or approve the result at
a documented rate. Every accepted result has an evidence bundle and every
rejected result contributes a reusable failure or boundary record.

### Phase 2 — Stabilize the company-to-Moodify contract

Goal: remove informal human interpretation from the Moodify execution layer.

- define a versioned `ProductionSpec` and `ProductionResult` schema;
- map the existing `CreativeBrief` to `ProductionSpec` without breaking v2;
- formalize preserve, avoid, reference-dimension, platform, depth, budget, and
  acceptance constraints;
- make API and queue execution the primary integration path;
- keep the Operator Console limited to operations, validation, and incidents.

Exit gate: 荣景文川 can submit, inspect, approve, archive, and reproduce a job
through stable contracts without Moodify directly contacting the creator.

### Phase 3 — Deepen the audio production line

Goal: move from full-mix post-processing toward professional, controllable
music production processing.

- stem-aware diagnosis and processing;
- vocal, drum, bass, instrument, space, dynamics, mix-balance, and mastering
  craft chains;
- reference audio analysis by explicit dimensions rather than global imitation;
- multi-candidate search with side-effect and preservation checks;
- delivery profiles for release masters and required derivative formats.

Exit gate: multiple production classes can be completed under explicit quality
and preservation standards with traceable candidate selection.

### Phase 4 — Accumulate industrial craft memory

Goal: turn every company project into reusable production knowledge.

- persist input condition, target, craft chain, metric change, side effects,
  reviewer decision, and final selection;
- version craft records and separate evidence from recommendations;
- recommend treatment plans from comparable accepted cases;
- prevent unreviewed or low-confidence results from contaminating craft memory;
- establish rollback, audit, data-rights, and project-isolation rules.

Exit gate: accumulated evidence improves treatment selection or reduces rework
without weakening human artistic control.

### Phase 5 — Industrialize runtime and capacity

Goal: make the processing capability dependable as company infrastructure.

- batch and long-running jobs, scheduling, retries, circuit breaking, and
  disaster recovery;
- compute and storage cost accounting per job and candidate;
- engine and model replaceability behind stable contracts;
- security, rights isolation, retention, observability, and compatibility;
- deployment targets and service levels based on measured production demand.

Exit gate: the system meets agreed reliability, traceability, cost, and recovery
targets for sustained company production workloads.

## Roadmap exclusions

The following are not Moodify roadmap items: creator community, consumer
onboarding, talent scoring, signing recommendation, artist positioning,
distribution, promotion, fan operations, stage operations, or commercial artist
management. These may exist in 荣景文川 systems, but must integrate with
Moodify only through explicit production contracts.

## Current baseline — 2026-07-26

- **Release baseline**: `v2.0.0-mvp`
- **Workspace v2**: 34/34 steps complete and sealed
- **Acceptance**: 179/179 Workspace v2 tests passing
- **Product loop**: project → brief → diagnosis/design → processing → Judge →
  human approval → Final archive
- **Next work**: post-MVP calibration, real-listener evaluation, and deployment
  are follow-up programs; they do not reopen the sealed Workspace v2 MVP.

The dated roadmap below is retained as historical planning context. Its
`proposed` rows are not the source of truth for the v2 MVP baseline.

**Historical snapshot updated**: 2026-06-05
**Current Node**: ECHAIN-MOODIFY-DEEPSEEK-API-015 (E-Chain 014 SEALED ✅)
**Previous Node**: ECHAIN-MOODIFY-DATA-LOOP-014 (SEALED ✅)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6
**Verified Data Loop Tests**: 88 passing (29 collectors + 30 recommenders + 11 integration + 18 product)

## Current Status — 2026-06-05 (E-Chain 014 Complete ✅)

ECHAIN-MOODIFY-DATA-LOOP-014 is SEALED — all 54 MHPs delivered across 3 NEMs.

The data optimization loop system is production-ready:
- `python3 -m moodify_runtime.cli data-loop run` — full pipeline
- 4 optimization loops: runtime reliability, scoring calibration, craft/preset, operator report
- 88 tests, all green
- Product integration: operator dashboard, craft library, MRS calibration, release gate

Next E-Chain candidates:
1. DeepSeek v4 API integration (smallest gap — protocol is ready)
2. Multi-night learning store (trend analysis + statistical significance)

Goal:

```text
nightly result data -> continuous software optimization loops
```

Start from `docs/plan/MHP-795_WRITE_DATA_LOOP_RUNBOOK.md`.

Cost-mode constraint: generate `deepseek_tasks.jsonl` and send DeepSeek v4 one line per call. The model only returns fixed JSON decisions; scripts handle extraction and merging.

Reusable protocol: `docs/protocol/AEP_WORKER_PROTOCOL.md`.

The first learning loops are:

- Runtime Reliability Loop: turn fatal errors and missing artifacts into root-cause fix tasks.
- Scoring Calibration Loop: compare pseudo MRS, MRS Open, penalty flags, and human review.
- Craft/Preset Selection Loop: convert sample/preset outcomes into craft memory and selector policy updates.
- Operator Report Loop: produce PASS/HOLD/REWORK morning decisions and next MHP entries.

## Previous Execution Target — 2026-06-05 Night

Run ECHAIN-MOODIFY-NIGHT-RESULT-013 Probe Plan-6A (MHP-737 to MHP-742).

Goal:

```text
implemented mainline modules -> one-night reproducible evidence bundle
```

Start from `docs/plan/MHP-741_WRITE_TONIGHT_RUNBOOK.md`.

## Current Mainline Snapshot — 2026-06-04

The active development branch is `codex/mainline-cloud-dev-20260603`.

Code and tests have advanced beyond the older NEM-002 roadmap section. The branch includes runtime productionization, MRS hardening, preset/craft work, listening lab, cloud worker, operator OS, velocity infrastructure, acoustic CT, tidal modules, PDF report modules, and craft-22 modules.

Release hygiene still needs attention before treating this branch as the public `main` baseline:

- reconcile roadmap and E-Chain status files with the implemented code;
- preserve the Apache-2.0 licensing update from `origin/main`;
- keep generated audio/output artifacts out of git;
- merge or PR `codex/mainline-cloud-dev-20260603` into `main` only after the two `origin/main` compliance commits are retained.

---

## NEM-001: Studio OS Alpha (COMPLETE ✅)

### ✅ Build-6: Real Integration & Console Completion (COMPLETE)

| Step | MHP | Task | Status |
|------|-----|------|--------|
| E1 | 053 | Real Audio E2E (3 tests, 6.64s) | ✅ |
| E2 | 054 | Console Interaction Tests (7 tests, 8 views) | ✅ |
| V1 | 055 | Multi-Job Stability (5 tests, 10 jobs) | ✅ |
| V2 | 056 | Full Stack Smoke (7 tests, uvicorn+HTTP) | ✅ |
| S1 | 057 | Production Checklist (Dockerfile, systemd, backup) | ✅ |
| N1 | 058 | Next Cycle Entry → Validate-6 | ✅ |

**Build-6 results**: 129 tests, all green. 5 production artifacts delivered.

### ✅ Validate-6: Production Validation (COMPLETE)

| Step | MHP | Task | Status |
|------|-----|------|--------|
| E1 | 059 | Dev Server Deployment (Docker, systemd, nginx, deploy script) | ✅ |
| E2 | 060 | Validation Dataset (30 MP3s, 3 WAVs, 5 genres, 10 ground truth) | ✅ |
| V1 | 061 | Validation Run (5 samples, bug found: CLI templates) | ✅ |
| V2 | 062 | Failure Analysis (3 classes, 1 P0 fix, 1 P2 noted) | ✅ |
| S1 | 063 | Validation Report (7 sections, ADOPT recommendation) | ✅ |
| N1 | 064 | Gate Decision (ADOPT with conditions) | ✅ |

**Key finding**: Default command_templates had incorrect arg format. Fixed.

### ✅ Harden-6: Production Hardening (COMPLETE)

| Step | MHP | Task | Status |
|------|-----|------|--------|
| E1 | 065 | Fix Validation Issues (CLI templates fixed, fix_log.md) | ✅ |
| E2 | 066 | Production Refactor (compact, storage health, structured logging) | ✅ |
| V1 | 067 | Full Regression (129/129 pass, 0 regressions) | ✅ |
| V2 | 068 | Integration Audit (CLI↔API↔Console↔Runtime, 40 routes, 8 views) | ✅ |
| S1 | 069 | Finalize Manifest (README v0.2.0-alpha, CHANGELOG, X-CLP ~30) | ✅ |
| N1 | 070 | Next NEM Entry → NEM-MOODIFY-MRS-002 | ✅ |

**🎉 NEM-18 COMPLETE. Gate: ADOPT. Next: NEM-MOODIFY-MRS-002.**

---

## Completed Cycles

### Cycle 1: MHP-031→040 — Studio OS Alpha (2026-06-04)
### Cycle 2: MHP-041→046 — API Deepening (2026-06-04)
### Cycle 3: MHP-047→052 — Console & CLI Hardening (2026-06-04)
### Cycle 4: MHP-053→058 — Build-6 (2026-06-04)
### Cycle 5: MHP-059→064 — Validate-6 (2026-06-04)
### Cycle 6: MHP-065→070 — Harden-6 (2026-06-04)

---

## NEM-002: MRS Scoring Hardening (Build-6 ✅, Validate-6 ⏳)

| Step | MHP | Task | Status |
|------|-----|------|--------|
| E1 | 071 | Genre-Specific Threshold Config | ✅ completed |
| E2 | 072 | Graduated Over-Dark Detector (3-level) | ✅ completed |
| V1 | 073 | Pseudo-MRS Weight Calibration | ✅ completed |
| V2 | 074 | Gate Threshold Unit Tests (16 tests) | ✅ completed |
| S1 | 075 | MRS Calibration Guide | ✅ completed |
| N1 | 076 | Build-6 Next Entry → Validate-6 | ✅ completed |
| E1 | 077 | Calibration Dataset (50+ samples) | proposed |
| E2 | 078 | Calibration Pipeline Run | proposed |
| V1 | 079 | MRS Comparison (pseudo vs calibrated vs Open) | proposed |
| V2 | 080 | Gate Accuracy Analysis (FP/FN per genre) | proposed |
| S1 | 081 | Calibration Report | proposed |
| N1 | 082 | Gate Decision (ADOPT/HOLD/REBUILD) | proposed |
| E1 | 083 | Fix Calibration Issues | proposed |
| E2 | 084 | MRS Engine Refactor (score_audio entry point) | proposed |
| V1 | 085 | Full Regression (150+ tests) | proposed |
| V2 | 086 | Integration Audit (MRS↔Gate↔CLI↔API↔Console) | proposed |
| S1 | 087 | Finalize MRS Manifest + Version Bump | proposed |
| N1 | 088 | Next NEM Entry (RUNTIME-003 or PRESET-004) | proposed |

**Entry**: `docs/nem/NEM-MOODIFY-MRS-002.md` (18 MHP files: `docs/plan/MHP-07[1-8]_*.md`)
**Target**: 150+ tests, gate accuracy ≥85%, graduated over_dark, genre-specific thresholds
