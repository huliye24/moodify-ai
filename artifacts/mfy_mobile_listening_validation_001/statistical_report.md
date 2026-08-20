# Statistical Report — MFY_MOBILE_LISTENING_VALIDATION_001 (2026-08-17)

## Status: DATA_PENDING (human listening sessions skipped per user instruction)

The statistics engine is fully implemented and self-tested on SYNTHETIC data.
No human judgments exist in this package — `identity_judgments.json` is empty
and will never be auto-filled by DeepSeek.

## Engine self-test (synthetic data, engine correctness only — NOT results)

| Test | Input | Expected | Observed |
|---|---|---|---|
| clear preference | n=100, prefer=80, threshold 0.55 | PASS, p<0.05, h>0.5 | PASS (p<0.001) |
| no preference | n=100, prefer=52 | fail | fail (p>0.05) |
| no data | n=0 | DATA_PENDING | DATA_PENDING |
| insufficient | n=60, prefer=30 | INSUFFICIENT (return to 71) | INSUFFICIENT |

## Protocol (frozen before any session)

- frozen_sha256: `f2fd3a8268b37ec8...` (full value in preregistered_protocol.json)
- Candidates frozen from 71: `mfy-intervention-v1` (dc_offset_fix, clip_peak_repair)
- Endpoints reported SEPARATELY: preference / identity_kept / difference_audible
- Thresholds: level match ≤ 0.5 dB, switch latency ≤ 100 ms, alpha 0.05,
  preference threshold 0.55 (missing it → return to 71, never lower)
- Samples: legitimate (SELECTED expected), negative control (BYPASSED),
  placebo bypass (replayed input)
- Session plan generated (seed 20260817, 3 sessions, blinded labels)

## When human sessions run (future)

Each judgment records reviewer / scope / time / device route / evidence ref.
The three endpoints are reported with effect size (Cohen's h), Wilson 95% CI,
exact binomial p-value and verdict PASS / INSUFFICIENT / DATA_PENDING.
