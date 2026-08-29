# MFY-CR-P03 — Baseline

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`
(P01 baseline 5bbc4972 + P02 constitution 99c9efa2).

## New implementation

```text
moodify-core-package/src/moodify/era_diagnostic/
  __init__.py      — public API (run_era_diagnostic, findings, report, policy)
  contract.py      — EraDiagnosticFinding, FindingStatus, ConfidenceLevel, categories
  thresholds.py    — ERA_DIAGNOSTIC_POLICY_V1 (diagnostic eligibility layer + thresholds)
  engine.py        — detectors ED-01..ED-06, evidence rule, confidence gates
  report.py        — era_diagnostic.v0.1.json + ERA_DIAGNOSTIC_REPORT.md (deterministic)

moodify-core-package/src/moodify/cli.py
  + era-diagnostic subcommand (--audio | --metrics, --out-dir, --case-id, --era-hint)

moodify-core-package/tests/era_diagnostic/
  conftest.py                      — deterministic synthetic fixtures (numpy/scipy, seeded)
  test_contract.py                 — status/confidence/serialization/policy enforcement
  test_engine.py                   — per-category unit tests + evidence rule
  test_synthetic_validation.py     — matrix V01-V12 + negative controls N01-N05 + repeatability
```

## Design constraints honored

- No audio output / DSP / plan_generator / judgment eligibility changes.
- No second ProductionCase / Evidence authority: findings reference existing
  metric names; `evidence_refs` is empty in v0.1 (P04 integration point).
- Estimator promotion went through the gate: no metric was flipped in
  `configs/measurement_registry_v1.yaml` (verified by test).
- The diagnostic eligibility layer lives in `ERA_DIAGNOSTIC_POLICY_V1`
  (`thresholds.py`) — finer-grained than the global registry, without touching it.
