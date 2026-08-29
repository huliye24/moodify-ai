# MAMSE-002 — Geometry Contract (T2)

**Date:** 2026-08-11

## Identity

```text
operator_id        = MAMSE-002
operator_version   = mamse-002-v0.1
geometry_id        = log2-equal-temperament-24bpo-v0.1
fmin               = 32.70319566257483 Hz (C1)
bins_per_octave    = 24        (2 bins per semitone)
n_octaves          = 9         (C1 .. just below C10 ~16.7 kHz)
n_bins             = 216
hop_length         = 512
window             = hann
filter_scale       = 1.0
sparsity           = 0.01
Q factor           = filter_scale / (2^(1/24) - 1) ≈ 33.8
```

## Grid properties (verified by tests)

- `f[k+1]/f[k] = 2^(1/24)` — adjacent ratio constant to 1e-9.
- Octave = 24 bins; semitone = 2 bins.
- Nominal window support `ceil(Q·sr/f)` decreases with frequency (verified: low > A4 > high).
- All log-distance reporting uses explicit units: octave / semitone / cent / bin.

## Hash & cache lineage

- `CQTConfig.sha256()` — deterministic canonical-JSON hash of the full config incl. derived n_bins and Q.
- Cache key policy: `source_sha256 + operator_id + operator_version + geometry_id + config_sha256 + sample_rate` (T12 requirement; cache is caller-keyed so geometry identity is embedded by the caller).

## Authority boundary

- This geometry is v0.1 research baseline, **not** the final optimal parameter set (24 bpo is a starting point).
- No canonical `BANDS` modification; no new linear-Hz authority; chroma/MIDI are descriptors, not musical authority.
