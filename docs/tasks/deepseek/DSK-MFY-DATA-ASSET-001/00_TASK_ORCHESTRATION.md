# DSK-MFY-DATA-ASSET-001 — Unified Job Data Pipeline

**Task type:** P1 data-infrastructure milestone
**Predecessors:** `DSK-MFY-RUNTIME-INTEGRATION-001`
**Strategy anchor:** `docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md` — "Two Curves" +
Roadmap Anchor (2026-08-01): the data asset is the compounding side of the product.

## 1. Problem

The data asset is the product's compounding side, but today its raw material is
scattered across heterogeneous, partially non-machine-readable locations:

| Source | Location | Format |
|---|---|---|
| Treatment records | `treatment_records/*.json` | structured JSON (schema 0.1.0) |
| Listening review labels | `listening_test/**/*scorecard*.md` | **markdown tables (not machine-readable)** |
| Inspector metric comparisons | `inspector_reports/*/metrics_comparison.json` | structured JSON |
| Night metric records | `schemas/night_metric_record.schema.json` contract | structured JSON |
| Calibration runs | `calibration_reports/v0.1.0-alpha.1*/` | mixed |
| Runtime outputs | `data/moodify_runtime/` | mixed |
| Formal evidence packages | `artifacts/verification/**/golden_case/evidence/` | structured JSON (runtime-integration milestone) |

There is no unified store, no schema binding them, no dedup, and no way to
answer "what do we know about this song across all jobs" in one query.
Scattered files do not compound; a structured pipeline does.

## 2. Goal

Every job's structured output — acoustic scans, MRS scores, gate decisions,
review labels, craft records, evidence references — flows into **one schema'd,
append-only data store**. The store becomes the substrate for MRS calibration
credibility, craft-library compounding, and cross-generation measurement.

## 3. Phase Plan

| Phase | Deliverable | Status |
|---|---|---|
| A | Schema contract + pipeline library + backfill + golden record + tests | **this round** |
| B | Structured review intake (scorecard fill becomes machine labels by default) | next |
| C | Calibration convergence views (MRS vs human labels) + craft writeback from store | next |
| D | Job → record auto-emission at runtime completion (runner/cloud_worker hooks) | next |

## 4. Phase A Deliverables

### 4.1 Schema contract — `schemas/job_data_record.schema.json`

One `JobDataRecord` (JSON Schema draft 2020-12) with sections:

```text
record_id          unique identifier (source-type + hash or uuid)
record_type        treatment | listening | metrics_comparison | night_metric | evidence_package | job
schema_version     "1.0.0"
collected_at       ISO-8601
source_artifacts   map of source paths (provenance — required, never empty)
job                job_id, status
source_audio       song_id, path, sha256
scan               features: peak_db, rms_db, crest_factor, dynamic_range_db,
                   correlation_lr, mid_side_ratio_db, bands{}, spectral_centroid,
                   spectral_rolloff_95, spectral_flatness, loudness_lufs, duration_s
scores             mrs (nullable with not_available reason), supporting metrics
gates              status (PASS|FAIL|WARN), checks{}
review             per-preset listener labels: clarity, warmth, space,
                   harshness_control, plastic_feel_control, artifact_control,
                   target_fit (1-5), better_than_before, listener, volume_matched
craft              preset, chain, params{}
evidence           evidence_dir, manifest refs, output paths
```

Required fields: `record_id`, `record_type`, `schema_version`, `collected_at`,
`source_artifacts`. Nullable sections must be explicit (`null` + reason), never
omitted — matching the explicit-declaration discipline of the control spine.

### 4.2 Pipeline library — `moodify_runtime/data_asset.py`

- `validate_record(record) -> list[str]` — jsonschema validation, returns errors.
- Collectors (each returns a `JobDataRecord` dict or raises):
  - `collect_treatment_record(path)`
  - `collect_listening_scorecard(path)` — parses the markdown scorecard
    (song info table, per-preset sections, dimension scores, quick-fill line).
  - `collect_metrics_comparison(path)`
  - `collect_night_metric_record(path)`
  - `collect_evidence_package(path)` — binds an evidence package
    (case.json, evidence_manifest.json, execution/verification records).
- `DataAssetStore(root)` — append-only JSONL records, atomic appends, dedup by
  `record_id`, `load_record(record_id)`, `stats()`.
- `ingest_sources(store, sources, registry) -> stats` — idempotent backfill
  walker: re-running the backfill must not duplicate records.

### 4.3 Backfill script — `scripts/data_asset_backfill.py`

Walks the registered source locations, ingests every parseable record, prints
per-source counts, and writes `data/data_asset/manifest.json` (source path →
record_id map). Exit 0 only when every source type produced ≥ 1 record.

### 4.4 Golden record

The `DSK-MFY-RUNTIME-INTEGRATION-001` golden case
(`artifacts/verification/runtime_integration/golden_case/evidence/`) becomes
the first complete end-to-end job record: source identity, scan features,
gates, execution + verification evidence, output identity. MRS score is
explicitly `null` with `not_available` reason (the case predates MRS scoring).

### 4.5 Tests — `moodify_runtime/tests/test_data_asset.py`

1. schema accepts a well-formed record;
2. schema rejects missing required fields and implicit-null sections;
3. treatment-record collector produces a valid record;
4. scorecard collector parses preset, dimensions, better_than_before;
5. evidence-package collector binds manifest hashes consistently;
6. store append is atomic and dedups on re-append;
7. `load_record` round-trips;
8. backfill is idempotent (two runs → identical record counts);
9. golden evidence package validates against the schema.

## 5. Acceptance Criteria (Phase A)

- `job_data_record.schema.json` exists and validates every collected record.
- Every source type in §1 has ≥ 1 ingested record in `data/data_asset/`.
- Backfill is idempotent (documented by test).
- Golden case record is internally consistent (hashes agree with the package).
- All new tests pass; existing suites remain green.
- `docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md` anchor updated (done).

## 6. Non-Goals (Phase A)

- No auto-emission hooks in the runner/cloud_worker yet (Phase D).
- No MRS re-calibration or convergence views (Phase C).
- No changes to the scorecard markdown format (Phase B makes fill machine-first).
- No database migration; JSONL + manifest is the deliberate storage choice.

## 7. Data Discipline Rules

- Records are append-only; corrections are new records, never edits.
- `record_id` dedup is by content hash — re-ingesting the same source file is a
  no-op, ingesting a changed source file creates a new record.
- Missing measurements are explicit (`null` + reason), never fabricated.
- Provenance (`source_artifacts`) is required on every record.
