# MFY-CR-P05 — Baseline

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`
(P01 baseline + P02 constitution + P03 era-diagnostic b7e44d0b).

## New implementation

```text
moodify-core-package/src/moodify/identity_guard/
  __init__.py      — public API (guard_candidate, rank_candidates, policy, contract)
  contract.py      — GuardState, IdentityDimension, IdentityDelta, IdentityVerdict,
                     DIMENSION_CAPABILITY (PROXY / MEASURABLE / NOT_MEASURABLE honesty)
  thresholds.py    — IDENTITY_GUARD_POLICY_V1 (per-dimension budgets, PROVISIONAL)
  guard.py         — six-dimension source-vs-candidate guard with veto semantics
  ranking.py       — Identity Gate ranking (REJECT/HR never auto-approved; SOURCE eligible)

moodify-core-package/src/moodify/cli.py
  + identity-guard subcommand (--source --candidate --out-dir [--ids])

moodify-core-package/tests/identity_guard/
  conftest.py                — clean fixture (with bass content) + 7 overprocessing candidates
  test_guard.py              — model, veto, missing measurements, synthetic overprocessing (26)
  test_ranking.py            — Identity Gate ranking rules (6)
```

## Design constraints honored

- No single identity score: multi-dimensional deltas only (veto, no averaging).
- IG-01 vocal/mid = PROXY (stereo-level proxies, honest label); IG-03 reverb =
  NOT_MEASURABLE_V0_1 (no validated detector, forces human ears when anything changes).
- No automatic stems, no device code, no Android, no payment/encryption.
- IdentityGuard is a derived result of existing Evidence/Comparison — no second
  Evidence authority.
- Reconstruction Master is defined hardware-neutral; device adaptation is
  downstream (documented, no code).
