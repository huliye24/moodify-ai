# Moodify — Project Roadmap

**Updated**: 2026-06-05
**Current Node**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042
**Previous Node**: NEM-MOODIFY-STUDIO-OS-001 (ADOPT ✅)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6
**Verified Mainline Tests**: 719 passing (607 runtime + 112 core)

## Current Learning Loop Target — 2026-06-05 Night

Run ECHAIN-MOODIFY-DATA-LOOP-014 Probe Plan-6A (MHP-791 to MHP-796).

Goal:

```text
nightly result data -> continuous software optimization loops
```

Start from `docs/plan/MHP-795_WRITE_DATA_LOOP_RUNBOOK.md`.

Cost-mode constraint: generate `deepseek_tasks.jsonl` and send DeepSeek v4 one line per call. The model only returns fixed JSON decisions; scripts handle extraction and merging.

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
