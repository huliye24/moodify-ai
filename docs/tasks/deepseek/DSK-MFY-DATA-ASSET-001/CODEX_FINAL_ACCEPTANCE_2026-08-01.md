# DSK-MFY-DATA-ASSET-001 — Codex Final Acceptance

**Decision:** ACCEPTED_AFTER_CODEX_FINISH
**Date:** 2026-08-01
**Acceptance owner:** Codex

## Outcome

Phase A of the unified job data pipeline is complete: every job's structured
output now flows into one schema'd, append-only store at
`data/data_asset/records/` instead of scattered files. The store holds
**104 records** across four source types (27 treatment, 42 listening, 34
metrics comparison, 1 evidence package), all validated against the new
`schemas/job_data_record.schema.json` contract, with content-derived
`record_id` dedup and explicit-null semantics for missing measurements.

This acceptance does **not** claim runtime auto-emission (Phase D), MRS
calibration convergence views (Phase C), or machine-first scorecard intake
(Phase B).

## Deliverables

1. **Schema contract** — `schemas/job_data_record.schema.json` (JSON Schema
   draft 2020-12): identity (record_id, record_type, schema_version,
   collected_at, source_artifacts — required), job, source_audio, scan,
   scores (required; `mrs: null` + `mrs_not_available` for absence), gates,
   review, craft, evidence. `additionalProperties: false` fail-closed.
2. **Pipeline library** — `moodify_runtime/data_asset.py`:
   - `validate_record()` — jsonschema validation returning violations;
   - collectors: `collect_treatment_record`, `collect_listening_scorecard`
     (markdown parser: song info table, per-preset sections, 7 dimensions,
     better_than_before, notes), `collect_metrics_comparison`,
     `collect_night_metric_record`, `collect_evidence_package` (binds
     evidence-manifest hashes + execution/verification/gate records);
   - `DataAssetStore` — append-only JSONL per record_type, atomic appends
     (tmp + fsync + replace), dedup by record_id, `load_record`, `stats`;
   - `ingest_sources` — idempotent backfill walker with skip semantics for
     non-target files.
3. **Backfill script** — `scripts/data_asset_backfill.py`: walks all
   registered source locations, prints per-source counts, writes
   `data/data_asset/manifest.json` (record_id → source path), exits non-zero
   when a populated source type has zero records in the store.
4. **Golden record** — the DSK-MFY-RUNTIME-INTEGRATION-001 golden case
   (`MFY-CASE-5030DEA8F22D`) is the first complete end-to-end job record:
   source identity, scan features, gates PASS, engine identity, verification
   PASS, output hash — all consistent with the evidence manifest.
5. **Tests** — `moodify_runtime/tests/test_data_asset.py`: **15 passed**
   (schema accept/reject incl. required `scores` and unknown record types,
   all collectors, real evidence package built through the
   production-control service, store append/dedup/round-trip, backfill
   idempotency, golden package validation).
6. **Strategy doc** — `docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md`:
   data-asset anchor added to Roadmap Anchor (2026-08-01).

## Backfill Results (2026-08-01)

```text
         treatment: 28 files, 27 ingested, 0 errors   (1 non-record skipped)
         listening: 17 files, 42 ingested, 0 errors   (templates produce 0)
metrics_comparison: 34 files, 34 ingested, 0 errors
      night_metric: 0 files  — no night_metric_record.json currently on disk
  evidence_package: 1 files, 1 ingested, 0 errors    (golden case)
             total: 104 records
```

Idempotency proven: a second backfill run ingests **0** new records.

## Data Discipline Compliance

- Append-only: corrections are new records, never edits.
- Dedup by content-derived record_id; re-ingesting the same source is a no-op.
- Missing measurements explicit: `mrs: null` + reason on every record that
  predates MRS scoring.
- Provenance (`source_artifacts`) present on every record; evidence records
  list all package files.
- `source_audio` attached only when the audio file actually exists — never a
  fabricated hash.

## Regression

- New tests: 15 passed.
- Full `moodify_runtime` suite: **936 passed, 10 skipped**.
- New files lint-clean (ruff).
- Backfill re-run: 0 new records, exit 0.

## Known Limitations / Next Phases

- `night_metric` source currently has 0 files on disk (the data-loop runner's
  output dir holds a snapshot, not a `night_metric_record.json`); the
  collector and registry entry exist and activate when such files appear.
- No auto-emission hooks in runner/cloud_worker yet (Phase D).
- No MRS-vs-human calibration convergence views (Phase C).
- Scorecard intake remains markdown-parsed, not machine-first (Phase B).

## Acceptance Evidence

- `data/data_asset/records/*.jsonl` — 104 validated records
- `data/data_asset/manifest.json` — source→record_id map
- `schemas/job_data_record.schema.json` — the contract
- `moodify_runtime/data_asset.py` + `moodify_runtime/tests/test_data_asset.py`
- `scripts/data_asset_backfill.py`
- `docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md` (Two Curves + anchor)
- `docs/tasks/deepseek/DSK-MFY-DATA-ASSET-001/00_TASK_ORCHESTRATION.md`
