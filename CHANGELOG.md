# Changelog

## v0.2.0-alpha (2026-06-04) — NEM-18: Studio OS Alpha Complete

### NEM-18 Protocol: Build-6 + Validate-6 + Harden-6

#### Build-6: Real Integration & Console Completion
- MHP-053: Real audio E2E tests (3 @pytest.mark.slow, 6.67s)
- MHP-054: Console interaction tests (8 views, 7 tests)
- MHP-055: Multi-job stability (5 tests, 10 concurrent jobs)
- MHP-056: Full stack smoke (7 tests, live uvicorn + HTTP)
- MHP-057: Production artifacts (Dockerfile, systemd, nginx, backup.sh, checklist)
- MHP-058: Next cycle entry → Validate-6

#### Validate-6: Production Validation
- MHP-059: Dev server deployment config (Docker, systemd, nginx, deploy.sh)
- MHP-060: Validation dataset (30 MP3s, 5 genres, 10 ground truth labels)
- MHP-061: Validation run (5 samples, found CLI template bug)
- MHP-062: Failure analysis (3 classes, 1 P0 fixed, 1 P2 documented)
- MHP-063: Validation report (ADOPT recommendation)
- MHP-064: Gate decision → ADOPT with conditions

#### Harden-6: Production Hardening
- MHP-065: Fix validation issues (CLI template fix in config.py, fix_log.md)
- MHP-066: Production refactor (compact_operator_jobs, check_storage_health, structured logging)
- MHP-067: Full regression (129/129 pass, 0 regressions)
- MHP-068: Integration audit (CLI↔API↔Console↔Runtime alignment, 40 routes, 8 views)
- MHP-069: Finalize manifest (README v0.2.0-alpha, CHANGELOG, X-CLP ~30)
- MHP-070: Next NEM entry (NEM-MOODIFY-MRS-002 recommended)

### Bug Fixes
- Default command_templates in config.py used incorrect CLI arg format
- test_sequential_job_lifecycle_loop used project_label as job_id
- test_console_interaction had wrong import path

### Architecture
- 17 modules, 40 API routes, 8 Console views, 40+ CLI subcommands
- 6 subsystems: Operator Console, Studio, Scheduler, Calibration, Craft, Runtime
- All data paths flow through RuntimeConfig (0 hardcoded paths in production code)

### Tests
- 129 total: 119 unit + 3 real audio + 7 full stack smoke
- 100% pass rate, 19 test files

---

## v0.1.0-alpha.4 (2026-06-04) — Studio OS Alpha Foundation

- MHP-031→040: 6 subsystems built, 107 tests, 45 CLI commands
- MHP-041→046: API deepening, real runtime integration
- MHP-047→052: Console hardening, CLI parity, edge cases
- Direction pivot: consumer app → industrial operator console
- NEM-MOODIFY-STUDIO-OS-001 master document

---

## v0.1.0-alpha.3 (2026-06-03) — Moodify v01 Mainline

- v01 pipeline: analyze → diagnose → process → export
- 3 DSP presets (warm_vocal, clean_master, wide_space)
- MRS (Moodify Reality Score) integration

---

## v0.1.0-alpha.2 (2026-05-30) — Runtime & CLI

- Treatment records, CLI analyze/process commands
- MRS Open v0.3.1 benchmark integration

---

## v0.1.0-alpha.1 (2026-05-28) — Protocol Design

- AEP-NEM protocol specification v0.1
- AEP Standard v0.1 (Atomic Engineering Package)
- NEM Node Evolution Molecule v0.1
