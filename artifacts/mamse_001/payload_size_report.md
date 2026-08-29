# MAMSE-001 — Payload Size Report (T4/T8)

**Date:** 2026-08-11

## Design

Sketch payload = frames × 17 features (9 core + 8 canonical bands), float32 + frame-center float64. Independent of FFT bin count. Dense spectrograms are never persisted for cases; visualization/diagnosis would regenerate on demand.

## Measured (Aliyun node, 188.52 s track @ 48 kHz)

| Measure | Per-R payload (compressed NPZ incl. centers) |
|---|---|
| R0 (69,117 frames) | ~1.26 MB |
| R1 (17,670 frames) | ~328 KB |
| R2 (4,415 frames) | ~82 KB |
| R3 (1,101 frames) | ~20 KB |
| **Whole case** | **~5.03 MB** (manifest + NPZ + cross evidence + events) |

## Dense-spectrogram counterfactual

R3 alone: 16,385 rfft bins × 1,101 frames × 8 bytes ≈ 144 MB float64 (or 72 MB float32). The four-resolution dense set would exceed 200 MB. The sketch replaces this with ~5 MB per full-length case — a ~40× reduction at R3, bounded by frames × features.

## Growth law

`payload ≈ 17 × (duration / hop_R + 1) × 4 bytes + centers`. Linear in duration, constant in n_fft. R0 dominates the budget (highest frame density).

## Boundedness policy

- Case artifacts always include manifest + cross evidence + events JSON (small, machine-readable).
- NPZ stores sketch rows only; no per-resolution dense planes.
- A per-case upper bound (e.g. 8 MB for ≤ 4-min sources) is enforced by construction: max frames for 240 s @ R0 hop 128 = ~90,000 → ~6.1 MB sketch; no unbounded arrays exist in the code path.
