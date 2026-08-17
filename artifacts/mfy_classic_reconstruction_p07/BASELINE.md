# P07 Baseline — Reconstruction Data Factory v0.1 (2026-08-17)

## Series state (verified)

| Pkg | Status |
|---|---|
| P01 Baseline Convergence | P01_COMPLETE (branch codex/moodify-classic-reconstruction-001, 692 passed) |
| P02 Constitution | P02_COMPLETE |
| P03 Era Diagnostic | P03_COMPLETE (era_diagnostic module) |
| P04 Reconstruction Objective | **MISSING** (no package, no module) — P06 blocked by this |
| P05 Identity Guard | P05_COMPLETE (identity guard v0.1, commit 36f2a721) |
| P06 Golden Reconstruction | SKIPPED per user (P04 missing + real-material + listening blocked) |
| **P07 Data Factory** | **THIS PACKAGE** |

## This package

Builds the Reconstruction Learning Factory on the existing Data Factory
authority (ProductionCase / Measurement Record / Evidence Artifact — reused,
not duplicated). Delivers the learning-record schema, outcome taxonomy,
rights/consent gate (training defaults NO), serial idempotent batch executor
with failure preservation, machine-human agreement analysis, and Gate A
pipeline-stability verification on a synthetic stand-in corpus.

Real 10-track corpus requires human-provided authorized material
(see PILOT_CORPUS_MANIFEST.md).
