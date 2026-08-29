# MFY-CR-P03 — Test Results

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`.

## Summary

```text
era_diagnostic (new)      = 61 passed / 0 failed (unit + synthetic matrix + negative controls)
full suite                = 767 passed / 5 skipped / 3 failed
baseline regression       = 692 passed / 5 skipped  (P01/P02 baseline: UNAFFECTED)
concurrent uncommitted    = 3 failed in tests/intervention/ (parallel session's in-progress
                            work — out of P03 scope, not touched)
ruff                      = all checks passed on moodify/era_diagnostic + tests/era_diagnostic
                            (4 pre-existing errors remain in concurrent uncommitted intervention/)
git diff --check          = clean
真机/instrumentation      = NOT_RUN (user instruction: skip device tests)
visual                    = SKIPPED (user instruction)
```

## New test coverage (tests/era_diagnostic/, 61 tests)

- **Unit (contract)**: status/confidence validation pairs, uncertainty reason
  vocabulary, measurement-refs evidence rule, round-trip serialization,
  deterministic JSON, policy enforcement (detector inputs ⊆ diagnostic
  eligible), global registry untouched.
- **Unit (engine)**: per-category verdicts for ED-01..ED-06, evidence rule
  (POSSIBLE needs >= 2 refs + ambiguity), finding ordering, no-RECONSTRUCT_NOW,
  unknown/missing metrics never yield POSSIBLE.
- **Synthetic matrix (V01-V12)**: low-pass ladder monotonic, hiss ladder
  monotonic (floor), clipping detection, mono not auto-defect, width observed
  not defect, phase perturbation raises risk, transcode NOT_SUPPORTED.
- **Negative controls (N01-N05)**: mono / dark mix / lo-fi / compressed
  aesthetic / narrow vintage — style never called a defect.
- **Repeatability**: identical inputs → identical findings and byte-identical
  JSON reports.

## Failure disposition (out of scope)

The 3 failures are in `tests/intervention/` — files created by a parallel
session (uncommitted, 补丁包71-line work). P03 does not modify or own them;
they are recorded here so the owning session can take them over. The P01/P02
baseline suite (692) is unaffected.
