# MAMSE-002 — Payload Size Report (T8/T9)

**Date:** 2026-08-11

## Policy

Dense CQT is a transient in-memory intermediate — never persisted for cases by default. Persisted artifacts: manifest JSON + `mamse002_logfreq_sketch.npz` (fixed-width frames × 30 features float32 + times) + evidence JSON.

## Measured (Aliyun 2C2G node, 188.52 s @ 48 kHz)

| Measure | Dense intermediate | Persisted sketch |
|---|---|---|
| 10 s | 1.5 MB | 110 KB |
| 45 s | 7.0 MB | 494 KB |
| Full 188.5 s | 29.1 MB | 2.07 MB |

Persisted sketch ≈ 14× smaller than the dense intermediate; growth linear in duration (frames × 30 features × 4 bytes).

## Comparison to MAMSE-001

| | MAMSE-001 (4× MR-STFT sketches) | MAMSE-002 (CQT sketch) |
|---|---|---|
| Full-track persisted | ~5.0 MB | ~2.1 MB |
| Peak RSS on node | 248 MB | 575 MB |
| Wall time full track | 34.9 s | 18.4 s (after one-time JIT) |

MAMSE-002 persists less but costs more RAM (dense CQT during processing) — consistent with the T9 guidance: run it conditionally, not in the default scan.

## Boundedness

- 30 features × frames is fixed; n_fft-independent.
- Dense CQT is released after sketch extraction (`CQTObservation` is transient; `save_case` writes sketch only).
- Upper bound for ≤ 4-min sources: ~4 MB persisted sketch; dense peak ~29 MB (observed max), far below the 1.5 GB MemoryHigh guard.
