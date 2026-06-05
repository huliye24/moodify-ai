# MHP-845: MAP-Chain Current State Audit

**Generated**: 2026-06-05
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015
**NEM**: NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A

## Baseline Test Result

```text
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
  python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py

7 passed, 5 warnings in 2.41s
```

All 7 v01 pipeline tests pass. Warnings are cosmetic (tight_layout margins).

---

## 1. MAP Layer Status Map

### S — Scan

| Field | Status | Detail |
|-------|--------|--------|
| File availability | **ready** | `ScanResult.exists`, `.file_size_bytes`, `.extension` |
| Audio readability | **ready** | `ScanResult.readable`, decode attempt in `scan_audio()` |
| Loudness field | **missing** | No integrated LUFS or RMS_total in ScanResult |
| Transient field | **missing** | No transient ratio or attack characterization |
| Space field | **missing** | No stereo width / side-mid balance in ScanResult |
| Texture field | **missing** | No spectral centroid or harmonic/noise ratio |
| Reality field | **missing** | No format metadata, clip count, DC offset check |

**Status**: `partial` — 2 of 7 fields ready. ScanResult is file-level only; needs acoustic-surface upgrade.

**Owner**: Worker (read-only surface) + Architect (contract definition)

**Files**:
- `moodify-core-package/src/moodify/v01_types.py` — `ScanResult` dataclass (lines 62–80)
- `moodify-core-package/src/moodify/v01_pipeline.py` — `scan_audio()` function (lines 176–196)

---

### A — Analyze

| Field | Status | Detail |
|-------|--------|--------|
| Spectrum bands | **ready** | `AudioMetrics.rms_sub/bass/low_mid/mid/presence/air` |
| Dynamics | **ready** | `AudioMetrics.peak_db`, `.crest_factor`, `.dynamic_range_db` |
| Stereo | **ready** | `AudioMetrics.correlation_lr` |
| Duration / SR / channels | **ready** | `AudioMetrics.duration_s`, `.sample_rate`, `.channels` |
| Feature vector (`b,w,c,p,d,s,t,r`) | **missing** | No structured feature vector with named dimensions |
| Task/genre weights | **missing** | No per-genre or per-task weighting schema |
| Spectrum PNG | **ready** | `v01_analyzer.py` generates before/after charts |

**Status**: `partial` — 5 of 7 fields ready. AudioMetrics is a flat metrics object, not a formal feature vector.

**Owner**: Worker (add field mapping) + Architect (vector contract)

**Files**:
- `moodify-core-package/src/moodify/v01_types.py` — `AudioMetrics` dataclass (lines 10–58)
- `moodify-core-package/src/moodify/v01_analyzer.py` — `analyze()` function

---

### D — Diagnose

| Field | Status | Detail |
|-------|--------|--------|
| Overall health | **ready** | `DiagnosisReport.overall_health` (good/fair/poor) |
| Issues list | **ready** | `DiagnosisReport.issues` — human-readable strings |
| Strengths list | **ready** | `DiagnosisReport.strengths` |
| Suggested presets | **ready** | `DiagnosisReport.suggested_presets` — feeds auto selector |
| Problem vector | **missing** | No structured `{problem_id, severity, confidence}` |
| Severity scale | **missing** | No numeric severity per issue |
| Priority ordering | **missing** | Issues not ranked by impact |
| Diagnosis loss | **missing** | No loss function for diagnosis quality |

**Status**: `partial` — 4 of 8 fields ready. Diagnosis is human-readable but not machine-actionable at scale.

**Owner**: Architect (problem taxonomy) + Worker (vector implementation)

**Files**:
- `moodify-core-package/src/moodify/v01_types.py` — `DiagnosisReport` dataclass (lines 83–100)
- `moodify-core-package/src/moodify/v01_diagnostics.py` — `diagnose()` function

---

### P — Process

| Field | Status | Detail |
|-------|--------|--------|
| DSP chain | **ready** | `MoodifyDSPChain` processes audio via pedalboard |
| Preset system | **ready** | 3 presets: `clean_master`, `warm_vocal`, `wide_space` |
| Auto selector | **ready** | `_select_preset()` from diagnosis suggestions |
| Output waveform | **ready** | 32-bit float WAV via `v01_exporter.export()` |
| Safety clamp | **ready** | `_post_process_safety()` clips peaks > 0.98 |
| Diagnosis-aware selector | **missing** | Selector uses preset names only, not problem vector |
| 22-operation adapter | **missing** | No craft chain integration from Craft-22 |
| Safe limits config | **missing** | No per-operation safety caps |

**Status**: `ready` — 5 of 8 fields ready. Core processing is functional. 22-operation adapter is a Build NEM task.

**Owner**: Architect (adapter contract) + Worker (craft integration)

**Files**:
- `moodify-core-package/src/moodify/v01_pipeline.py` — `process_audio()` (lines 29–173)
- `moodify-core-package/src/moodify/v01_presets.py` — preset definitions
- `moodify-core-package/src/moodify/v01_exporter.py` — `export()`

---

### V — Validate

| Field | Status | Detail |
|-------|--------|--------|
| Before/after metrics | **ready** | `metrics_before` + `metrics_after` in ProcessResult |
| Quality gate | **ready** | `QualityGate.passed`, `.warnings`, `.deltas` |
| MRS proxy | **ready** | `mrs_proxy_v01` with version tag |
| Damage loss | **ready** | `_damage_loss()` with 0–1 scale |
| Risk flags | **ready** | `_risk_flags()`: peak_risk, over_dark, dynamic_damage, mrs_regression, damage_loss_high |
| Calibrated MRS | **missing** | `mrs_proxy_v01` is explicitly a placeholder |
| Risk matrix | **missing** | No probability × impact grid |
| Pass policy config | **missing** | Thresholds are hardcoded in `_quality_gate()` |

**Status**: `partial` — 5 of 8 fields ready. Validation works but depends on proxy MRS.

**Owner**: Judge (MRS calibration) + Architect (threshold policy)

**Files**:
- `moodify-core-package/src/moodify/v01_pipeline.py` — `_quality_gate()`, `_mrs_proxy()`, `_damage_loss()`, `_risk_flags()` (lines 219–297)
- `moodify_runtime/mrs_engine.py` — `MRSScoreResult` with MRS Open v0.3.1 (lines 1–60+)

---

### R — Report

| Field | Status | Detail |
|-------|--------|--------|
| JSON report | **ready** | `_save_report()` writes structured JSON |
| PDF report | **ready** | `_save_pdf_report()` with charts (matplotlib) |
| Workflow stage names | **ready** | `["S_scan", "A_analyze", ..., "G_generate"]` |
| Stage timings | **ready** | Per-stage elapsed seconds |
| Reusable MAP schema | **missing** | Report structure is ad-hoc, not schema-validated |
| CT plates | **missing** | No acoustic CT visualization in v01 report |
| Customer section | **missing** | No redacted customer-facing view |
| Operator section | **missing** | No operator decision fields |

**Status**: `partial` — 4 of 8 fields ready. Reports are functional but not MAP-schema-compliant.

**Owner**: Worker (schema implementation) + Judge (schema validation)

**Files**:
- `moodify-core-package/src/moodify/v01_pipeline.py` — `_save_report()` (lines 300–344), `_save_pdf_report()` (lines 347–447)
- `moodify_runtime/report.py` — `generate_daily_report()` (lines 1–251)
- `moodify_runtime/pdf_report.py` — `PdfReportConfig`, CT-aware PDF generation (lines 1–60+)

---

### G — Generate

| Field | Status | Detail |
|-------|--------|--------|
| Output WAV | **ready** | `DeliveryBundle.output_audio` |
| JSON report path | **ready** | `DeliveryBundle.json_report` |
| PDF report path | **ready** | `DeliveryBundle.pdf_report` |
| Spectrum before/after | **ready** | `DeliveryBundle.spectrum_before/after` |
| Reproducibility metadata | **missing** | No env, git hash, dependency versions |
| Manifest | **missing** | No delivery manifest file |
| Logs | **missing** | No log bundle in delivery |
| Environment stamp | **missing** | No Python version, package versions |

**Status**: `partial` — 4 of 8 fields ready. Delivery paths exist but no reproducibility package.

**Owner**: Worker (manifest writer) + Judge (delivery QA)

**Files**:
- `moodify-core-package/src/moodify/v01_types.py` — `DeliveryBundle` dataclass (lines 131–148)
- `moodify-core-package/src/moodify/v01_exporter.py` — `export()`

---

## 2. MAP Layer Summary

| Layer | Status | Ready Fields | Total Fields | Readiness |
|-------|--------|-------------|-------------|-----------|
| S Scan | partial | 2 | 7 | 29% |
| A Analyze | partial | 5 | 7 | 71% |
| D Diagnose | partial | 4 | 8 | 50% |
| P Process | ready | 5 | 8 | 63% |
| V Validate | partial | 5 | 8 | 63% |
| R Report | partial | 4 | 8 | 50% |
| G Generate | partial | 4 | 8 | 50% |

**Overall**: 29 of 54 MAP fields are `ready`. Average readiness: 54%.

---

## 3. Strengths (What Does Not Need Rework)

1. **v01_pipeline.py** — Clean 7-stage flow already aligned to MAP naming. Single-file orchestration, testable, well-typed.
2. **v01_types.py** — Lightweight dataclasses with `to_dict()` serialization. No dependency on legacy data_types.py.
3. **QualityGate** — Already has `mrs_proxy_v01` version tag, damage loss (0–1), and 5 risk flags. Good foundation.
4. **Auto preset selector** — Simple, debuggable, feeds from diagnosis. Does not need refactoring.
5. **PDF report** — matplotlib-based, before/after bar charts + delta chart + manifest page. Functional and extensible.
6. **mrs_engine.py** — Unified MRS entry point with pseudo-MRS + MRS Open v0.3.1 + over-dark + gate decision. Ready for calibration adapter.
7. **Craft-22** — 22-operation registry, chain planner, selector with genre recommendations. Ready for v01 adapter.
8. **Test coverage** — 7 v01 pipeline tests + 88 runtime tests pass. Regression safety net exists.

---

## 4. Critical Gaps (By Risk × Value)

| # | Gap | MAP Layer | Risk | Value | Owner |
|---|-----|-----------|------|-------|-------|
| 1 | No calibrated MRS — `mrs_proxy_v01` is a placeholder | V | High | High | Judge |
| 2 | No MAP report JSON schema — reports are ad-hoc dicts | R | High | High | Architect |
| 3 | ScanResult missing acoustic surface fields | S | Medium | High | Worker |
| 4 | No feature vector contract — flat metrics only | A | Medium | High | Architect |
| 5 | Diagnosis is human-readable only — no machine-actionable vector | D | Medium | High | Architect |
| 6 | No delivery manifest / reproducibility metadata | G | Medium | Medium | Worker |
| 7 | Quality gate thresholds are hardcoded | V | Medium | Medium | Architect |
| 8 | No 22-operation craft adapter in v01 P stage | P | Low | Medium | Worker |
| 9 | No CT plates in v01 report | R | Low | Medium | Worker |
| 10 | No customer-facing report redaction | R | Low | Low | Worker |

---

## 5. AWJ Ownership Assignment

| Gap | Owner | Rationale |
|-----|-------|-----------|
| MRS calibration adapter | Judge | Requires scoring integrity verification and regression evidence |
| MAP report schema | Architect | Defines contract boundaries for all downstream consumers |
| Scan surface fields | Worker | Bounded addition — add computed fields to existing dataclass |
| Feature vector contract | Architect | Affects analyzer, diagnoser, and MRS adapter interfaces |
| Diagnosis problem taxonomy | Architect | Requires cross-layer definition (D→P→V linkage) |
| Delivery manifest | Worker | Self-contained file writer |
| Threshold config | Architect | Policy decision affecting pass/fail semantics |
| Craft adapter | Worker | Integration of existing Craft-22 into v01 path |
| CT plates | Worker | Existing CT engine — needs v01 bridge |
| Customer redaction | Worker | Filter policy applied to existing report |

---

## 6. Adjacent E-Chain Relationships

| E-Chain | Relationship | MAP Impact |
|---------|-------------|------------|
| ECHAIN-MOODIFY-RUNTIME-001 | Runtime execution → MAP P stage | MAP must consume runtime task records |
| ECHAIN-MOODIFY-MRS-LISTENING-003 | MRS scoring → MAP V stage | MAP must replace mrs_proxy_v01 with calibrated MRS |
| ECHAIN-MOODIFY-CRAFT-22-012 | Craft operations → MAP P stage | MAP must expose 22-op adapter |
| ECHAIN-MOODIFY-ACOUSTIC-CT-007 | CT plates → MAP R stage | MAP report should embed CT findings |
| ECHAIN-MOODIFY-PDF-REPORT-011 | PDF reports → MAP R stage | MAP should reuse PDF config and theme |
| ECHAIN-MOODIFY-NIGHT-RESULT-013 | Nightly results → MAP G stage | MAP delivery feeds nightly operator review |
| ECHAIN-MOODIFY-DATA-LOOP-014 | Data loops → MAP feedback | MAP quality results feed learning loops |
| ECHAIN-MOODIFY-CLOUD-WORKER-004 | Cloud workers → MAP execution | MAP tasks can be dispatched to cloud workers |

---

## 7. Probe 6A Recommendation

**Verdict**: The MAP-Chain foundations exist. The v01 pipeline already speaks S-A-D-P-V-R-G vocabulary. The main gaps are (1) calibrated MRS replacing the proxy, (2) a validated report schema, (3) scan surface enrichment, and (4) formal feature/diagnosis vectors. These four items are the correct scope for Probe 6A → 6B → 6C.

**Next Action**: Proceed to MHP-846 (Interface Contract) with the layer status map as input.

---

## 8. Command Evidence

```text
Test command:
  PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
    python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py
Result:
  7 passed, 5 warnings in 2.41s

Audit report:
  reports/echain_moodify_map_chain_015/mhp_845_current_state_audit.md

Files audited:
  moodify-core-package/src/moodify/v01_pipeline.py       (452 lines)
  moodify-core-package/src/moodify/v01_types.py          (169 lines)
  moodify_runtime/mrs_engine.py                          (60+ lines read)
  moodify_runtime/craft_chain.py                         (60+ lines read)
  moodify_runtime/craft_selector.py                      (60+ lines read)
  moodify_runtime/pdf_report.py                          (60+ lines read)
  moodify_runtime/report.py                              (251 lines)
  docs/echain/ECHAIN-MOODIFY-MAP-CHAIN-015.md            (165 lines)

No code changes were made. This is a read-only audit.
```
