# MFY-CR-P05 — Test Results

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`.

## Summary

```text
identity_guard (new) = 26 passed / 0 failed (model + veto + overprocessing + ranking)
full suite           = 816 passed / 5 skipped / 0 failed
p03 era_diagnostic   = included and green (regression)
ruff                 = all checks passed (src/moodify/identity_guard + tests/identity_guard)
git diff --check     = clean
真机/instrumentation = NOT_RUN (user instruction)
visual               = SKIPPED (user instruction)
```

## Coverage

- **Model**: six dimensions always present and ordered; source-vs-source PASS;
  no single identity score; capability labels honest (PROXY / MEASURABLE /
  NOT_MEASURABLE); deterministic serialization.
- **Veto semantics**: REJECT cannot be averaged away; vocal proxy drift →
  HUMAN_REQUIRED (never REJECT); mono→wide rejected by mono guard; new
  clipping rejected.
- **Missing measurements**: missing dimension metrics → NOT_MEASURABLE, no
  crash, no fabrication.
- **Synthetic overprocessing** (real measurement chain, seeded fixtures):
  over_bright → HUMAN_REQUIRED; over_bass / over_compressed / over_wide /
  over_loud → REJECT; minimal (+0.5 dB) → PASS; balanced (+1 dB) → PASS.
- **Ranking (Identity Gate)**: REJECT never position 1 even with highest
  objective progress; REJECT/HUMAN_REQUIRED never auto-approvable; SOURCE
  always eligible; technical improvement cannot override identity failure.

## CLI smoke

`moodify identity-guard --source src.json --candidate cand.json` produced
overall REJECT with per-dimension deltas and wrote `identity_guard.v0.1.json`
(verified end-to-end).
