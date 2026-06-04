# Moodify — Project Roadmap

**Updated**: 2026-06-04
**Current Node**: NEM-MOODIFY-MRS-002 (active)
**Previous Node**: NEM-MOODIFY-STUDIO-OS-001 (ADOPT ✅)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

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

## NEM-002: MRS Scoring Hardening (⏳ NEXT)

| Step | MHP | Task | Status |
|------|-----|------|--------|
| E1 | 071 | Genre-Specific Threshold Config | proposed |
| E2 | 072 | Graduated Over-Dark Detector (3-level) | proposed |
| V1 | 073 | Pseudo-MRS Weight Calibration | proposed |
| V2 | 074 | Gate Threshold Unit Tests | proposed |
| S1 | 075 | MRS Calibration Guide | proposed |
| N1 | 076 | Build-6 Next Entry → Validate-6 | proposed |
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
