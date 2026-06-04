# Changelog

## v0.1.0-alpha.4 (2026-06-04) — Studio OS Alpha

### MHP-031 → 040: Industrial Operator System

- **MHP-031**: Operator Job data model (Job/Candidate/Score/Gate/Delivery), JSONL storage, 13 tests
- **MHP-032**: Job-to-runtime adapter (plan/run/show-plan), CLI + 10 tests
- **MHP-033**: Report bundle system (summary.md, *.jsonl, manifest.csv), 4 tests
- **MHP-034**: Delivery records with gate validation and override flow
- **MHP-035**: FastAPI server (45 routes) + industrial Operator Console HTML
- **MHP-036**: Studio Back Office (Client/Project/Order/StaffNote), JSONL storage
- **MHP-037**: Craft Library writeback from delivered candidates
- **MHP-038**: Cloud GPU Scheduler (Request→Lease→Run→Cost)
- **MHP-039**: MRS Calibration Lab (sample sets, reviews, audits, thresholds)
- **MHP-040**: End-to-end Studio OS Alpha integration test + runbook

### MHP-041 → 046: 6-Step Plan Cycle — API Deepening

- **MHP-041**: Wired studio/scheduler/calibration endpoints (25+ → 45 routes, 0 stubs)
- **MHP-042**: Real runtime integration — run_operator_job hardened with queue checks, timestamps, `--live` flag
- **MHP-043**: API Test Suite — 42 FastAPI TestClient tests across 5 test files
- **MHP-044**: API Contract Verification — 12 contract tests ensuring Console JS ↔ API alignment
- **MHP-045**: ARCHITECTURE.md rewrite, module dependency graph, CHANGELOG, README update
- **MHP-046**: Next cycle plan generation (MHP-047→052)

### Stats
- **Tests**: 38 → 95
- **Modules**: 8 → 17
- **API Routes**: 0 → 45
- **Plan files**: 10 → 16

## v0.1.0-alpha.3 (2026-06-03)

- MHP-025: API v01 alignment
- MHP-024: Treatment records system
- 20 v01 tests, 104 total tests (including legacy)

## v0.1.0-alpha.2 (2026-06-02)

- v01 mainline: analyzer, diagnostics, presets, pipeline, exporter
- CLI: analyze, process, presets
- Baseline test audio

## v0.1.0-alpha.1 (2026-06-01)

- Initial v01 architecture
- DSP chain with 3 presets × 15 parameters
- Legacy system preservation
