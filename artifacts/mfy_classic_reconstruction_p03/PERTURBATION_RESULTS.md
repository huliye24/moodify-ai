# MFY-CR-P03 — Perturbation Results

Real measurement chain (`compute_metrics` + `compute_stereo_metrics`) on
synthetic fixtures; engine verdicts measured during this execution.

## Low-pass ladder (ED-01)

| Perturbation | measured cutoff | rolloff-95 | verdict | confidence |
|---|---|---|---|---|
| clean | ~19.0 kHz | ~12.0 kHz | NOT_APPLICABLE | - |
| LP 18k | ~14.1 kHz | ~11.4 kHz | POSSIBLE_TECHNICAL_LIMITATION | LOW |
| LP 15k | ~14.1 kHz | ~11.2 kHz | POSSIBLE_TECHNICAL_LIMITATION | LOW |
| LP 12k | ~12.0 kHz | ~9.8 kHz | POSSIBLE_TECHNICAL_LIMITATION | LOW |
| LP 9k | ~10.0 kHz | ~7.8 kHz | POSSIBLE_TECHNICAL_LIMITATION | HIGH |

Monotone (severity 9k > 12k >= 15k >= 18k). Note the estimator's coarseness on
tonal content (18k/15k both read ~14 kHz) — recorded as a failure mode.

## Hiss ladder (ED-02)

| Perturbation | p10 frame RMS (floor) | verdict |
|---|---|---|
| clean | -120 dBFS | NOT_APPLICABLE |
| hiss -70 | -73.1 dBFS | NOT_APPLICABLE (quiet) |
| hiss -60 | -63.0 dBFS | POSSIBLE_TECHNICAL_LIMITATION (LOW) |
| hiss -50 | -53.1 dBFS | INSUFFICIENT_EVIDENCE (hiss fills quiet windows) |

Floor responds monotonically. The -50 step honestly reports
INSUFFICIENT_EVIDENCE: loud hiss removes the quiet reference — never HIGH.

## Clipping (ED-03)

Heavy clipping fixture: clipping_sample_ratio ~0.03, true peak at hard ceiling
→ POSSIBLE_TECHNICAL_LIMITATION (MEDIUM). Soft-compressed (no clip) → OBSERVED
or NOT_APPLICABLE.

## Stereo perturbations (ED-04)

| Perturbation | correlation | verdict |
|---|---|---|
| clean | 0.974 | NOT_APPLICABLE |
| mono fold-down | 1.0 | LIKELY_ARTISTIC_CHARACTER (LOW) |
| width 50 % | 0.993 | OBSERVED (narrow, undecidable collapse vs character) |
| width 30 % | 0.998 | OBSERVED (narrow) |
| phase flip 2-4 s | 0.126 | POSSIBLE_TECHNICAL_LIMITATION (LOW; neg_corr 0.247) |

## Transfer (ED-06)

No validated detector → NOT_SUPPORTED_IN_V0_1 on all fixtures (no fabrication).

## Repeatability

Identical inputs → byte-identical findings and JSON reports (seeded fixtures,
fixed `created_at`; asserted in `test_repeatability`).
