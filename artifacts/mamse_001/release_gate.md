# MAMSE-001 — Release Gate (T10)

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — R3 Case Proven. Not R6 Moodify Core; no canonical promotion.

## Gate evaluation

| Criterion | Assessment | Evidence |
|---|---|---|
| Can prove information gain | **No failure.** R3 resolves a 89 Hz dominant invisible at R0 (case 7b3f021, 375→89 Hz); fine/coarse onset times differ (R0 18.2 s vs R2 25.8 s vs R3 0.5 s in 9961e07); 82–318 conflicts/case preserved | `real_case_results.md` §2–3 |
| Memory cost uncontrolled | **No failure.** Peak RSS constant 248 MB (streaming), swap delta 0, on the 2C2G node | `benchmark.json` |
| Conflicts with S-axis authority | **No failure.** scales.py / build.py / feature_registry.py untouched; multiscale tests 15/15; full suite 341 passed (326 baseline + 15 new) | `test_results.md` |
| Real cases add no incremental evidence | **No failure.** Three operator-owned cases, all three show resolution-dependent structure | `real_case_results.md` |
| Creates new metric/band authority | **No failure.** Bands imported from canonical `feature_registry.BANDS`; no registry entries added; R features are EXPERIMENTAL descriptors only | `architecture.md`, `baseline_audit.md` Q1/Q6 |
| Breaks existing tests / release convergence | **No failure.** 341 passed, 5 skipped; ruff clean on changed scope; freeze manifest unaffected | `test_results.md` |

## Maturity levels

```text
R0 Theory        ✅ this package (spec + math section of the task docs)
R1 Operator      ✅ prototype + experimental implementation runs
R2 Verified      ✅ 8/8 synthetic gates + 15 tests
R3 Case Proven   ✅ 3 real cases with incremental evidence
R4 Product       ⏸ deferred — only after stable evidence contract over more cases
R5 Data Proven   ⏸ September dataset analysis
R6 Moodify Core  ❌ not requested; requires a separate future decision
```

## Outstanding (unresolved, non-blocking for EXPERIMENTAL)

1. `NARROWBAND_PERSISTENT_STRUCTURE` threshold (flatness < 0.15) is loose for dense AI productions — events span near-whole tracks. Calibration belongs to the September data phase.
2. Relative-flux silence guard is a pragmatic definition; a formal missing-value policy for flux over silent frames should be written before R4.
3. Execution-graph integration (cache/feature bus) deliberately deferred.
4. Node-side manifest git commit reads "unknown" (clean-check tree is not a git repo); local manifests record the real commit. Should be solved by deploying as a git checkout for production-scale runs.

## Boundaries honored

- No app navigation/UI buttons added (T9 emits data events only).
- No AI model dependency, no GPU requirement.
- No dense spectrogram persistence (payload report).
- No "AI quality score" produced (interpretation policy forbids cross-resolution averaging).
- Task prototype not copied into canonical namespace (implementation lives in `moodify_experimental`).
