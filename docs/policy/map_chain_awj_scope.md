# MAP-Chain AWJ Scope and Forbidden Files Policy v0.1

**Version**: 0.1.0
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015
**Effective**: 2026-06-05

## 1. Purpose

This policy defines file-level read/write/approve permissions for the Architect, Worker, and Judge roles within the MAP-Chain E-chain. It is designed to be machine-checkable by a Judge gate script.

## 2. Role Definitions

| Role | Symbol | Authority |
|------|--------|-----------|
| Architect | A | Owns formulas, schemas, thresholds, merge decisions. Required approval for core pipeline changes. |
| Worker | W | Can implement bounded AEPs within allowed files. Must not change core semantics. |
| Judge | J | Validates Worker output against schema, scope, tests, and evidence gates. |

## 3. MAP Layer File Permissions

### S — Scan

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_types.py` (ScanResult) | RW | R | R | Architect must approve field additions |
| `moodify-core-package/src/moodify/v01_pipeline.py` (scan_audio) | RW | R | R | Scan logic is Architect-owned |
| `moodify_runtime/metrics.py` (scan helpers) | RW | RW | R | Worker can add scan metrics |
| `moodify_runtime/tests/test_metrics.py` | R | RW | R | Worker can add tests |

### A — Analyze

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_types.py` (AudioMetrics) | RW | R | R | Contract stability |
| `moodify-core-package/src/moodify/v01_analyzer.py` | RW | RW | R | Worker can add band/metric computations |
| `moodify_runtime/metrics.py` | R | RW | R | Feature extraction surface |

### D — Diagnose

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_types.py` (DiagnosisReport) | RW | R | R | Problem taxonomy is Architect-owned |
| `moodify-core-package/src/moodify/v01_diagnostics.py` | RW | RW | R | Worker can add issue detection rules |
| `moodify_runtime/mrs_engine.py` (gate_decision) | RW | R | R | Gate semantics must not change |

### P — Process

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_pipeline.py` (process_audio) | RW | R | R | Orchestration is Architect-owned |
| `moodify-core-package/src/moodify/v01_presets.py` | RW | RW | R | Worker can add presets |
| `moodify_runtime/craft_chain.py` | RW | R | R | Craft semantics unchanged |
| `moodify_runtime/craft_selector.py` | RW | R | R | Selector policy unchanged |
| `moodify_runtime/craft_processes.py` | RW | R | R | Operation registry read-only |

### V — Validate

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_pipeline.py` (_quality_gate) | RW | R | R | Thresholds are Architect policy |
| `moodify_runtime/mrs_engine.py` | RW | R | RW | Judge validates MRS calibration |
| `moodify_runtime/over_dark.py` | R | R | RW | Judge checks over-dark detection |
| `moodify_runtime/mrs_calibration.py` | RW | R | RW | Judge validates calibration proposals |

### R — Report

| File | A | W | J | Notes |
|------|---|---|---|------|
| `schemas/map_chain_report.schema.json` | RW | R | RW | Schema stability is Judge-gated |
| `moodify-core-package/src/moodify/v01_pipeline.py` (_save_report, _save_pdf_report) | RW | RW | R | Worker can extend report fields |
| `moodify_runtime/report.py` | R | RW | R | Worker can add daily report sections |
| `moodify_runtime/pdf_report.py` | R | RW | R | Worker can add PDF sections |
| `moodify_runtime/pdf_templates.py` | R | RW | R | Theme/template surface |

### G — Generate

| File | A | W | J | Notes |
|------|---|---|---|------|
| `moodify-core-package/src/moodify/v01_types.py` (DeliveryBundle) | RW | R | R | Contract stability |
| `moodify-core-package/src/moodify/v01_exporter.py` | RW | RW | R | Worker can add export formats |
| `moodify_runtime/runner.py` | R | RW | R | Manifest/delivery surface |

## 4. Forbidden Files (No Worker or Unapproved Access)

| File | Reason |
|------|--------|
| Production deployment configs (`*.env`, `configs/production/*`) | Security boundary |
| `moodify_runtime/mrs_engine.py` (score_audio semantics) | Core scoring — Architect only |
| `moodify_runtime/operator_api.py` | Production API — regression risk |
| `moodify_runtime/supervisor.py` | Process supervision — safety critical |
| `moodify_runtime/scheduler.py` | Job scheduling — concurrency risk |
| `moodify_runtime/cloud_worker.py` | Infrastructure — deployment risk |
| Sealed E-chain docs (`docs/echain/*SEALED*`) | History is immutable |
| Other NEM's core files | Cross-NEM isolation |

## 5. Judge Gate Script Contract

A Judge gate script SHALL check:

```python
WORKER_ALLOWED_FILES = {
    # S layer
    "moodify_runtime/metrics.py",
    "moodify_runtime/tests/test_metrics.py",
    # A layer
    "moodify-core-package/src/moodify/v01_analyzer.py",
    # D layer
    "moodify-core-package/src/moodify/v01_diagnostics.py",
    # P layer
    "moodify-core-package/src/moodify/v01_presets.py",
    # R layer
    "moodify-core-package/src/moodify/v01_pipeline.py",  # _save_report only
    "moodify_runtime/report.py",
    "moodify_runtime/pdf_report.py",
    "moodify_runtime/pdf_templates.py",
    # G layer
    "moodify-core-package/src/moodify/v01_exporter.py",
    "moodify_runtime/runner.py",
    # Spec/docs surface
    "docs/spec/*",
    "schemas/*",
    "reports/echain_moodify_map_chain_015/*",
}

ARCHITECT_ONLY_FILES = {
    "moodify-core-package/src/moodify/v01_types.py",
    "moodify-core-package/src/moodify/v01_pipeline.py",  # orchestration logic
    "moodify_runtime/mrs_engine.py",
    "moodify_runtime/craft_chain.py",
    "moodify_runtime/craft_selector.py",
    "moodify_runtime/craft_processes.py",
    "schemas/map_chain_report.schema.json",
    "docs/spec/map_chain_interface_contract.md",
}

FORBIDDEN_FILES = {
    # Production
    "moodify_runtime/operator_api.py",
    "moodify_runtime/supervisor.py",
    "moodify_runtime/scheduler.py",
    "moodify_runtime/cloud_worker.py",
    # Sealed history
    # (pattern: docs/echain/*SEALED*)
}
```

A Worker AEP that modifies any file outside `WORKER_ALLOWED_FILES` or inside `ARCHITECT_ONLY_FILES` or `FORBIDDEN_FILES` SHALL be rejected by the Judge at `G_scope`.

## 6. Policy Updates

- Architect can update this policy at any time.
- Policy changes during Build NEM require Gate 2 review.
- Policy changes during System NEM require Gate 3 review.
- This policy itself is in `docs/policy/map_chain_awj_scope.md` (Worker-writable for updates, Judge-validated).
