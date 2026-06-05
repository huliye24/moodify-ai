# MHP-852: Feature Vector Weighting Brief

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B: Vector Definitions / E2
**Depends on**: MHP-845 (Current State Audit), MHP-851 (Scan Vector Gap)
**Protocol**: AWJ Stack + E-Chain 54

## Context

`AudioMetrics` is a flat bag of 10 scalar fields plus a 6-band spectrum. MAP requires a named feature vector `f = [b, w, c, p, d, s, t, r]` with per-task/genre weights. This brief defines the mapping.

## Feature Vector Definition

### v0.1 (Current): Flat Metrics

```text
AudioMetrics = {
  spectrum: {sub_bass, bass, low_mid, mid, presence, air},  # 6 band dB values
  dynamics: {peak_db, crest_factor, dynamic_range_db},       # 3 scalars
  stereo: {correlation_lr},                                   # 1 scalar
  duration_s, sample_rate, channels                           # 3 metadata
}
```
Total: 6 + 3 + 1 + 3 = 13 fields, 10 meaningful scalars.

### v0.2 (MAP Target): Named Feature Vector

```text
f = [bass_balance, warmth, clarity, presence_energy, density,
     stereo_width, transient_energy, reality_index]
```

| Dimension | Symbol | Formula (from current fields) | Range | Interpretation |
|-----------|--------|------------------------------|-------|----------------|
| Bass Balance | `b` | `tanh((rms_bass + 15) / 10)` | 0–1 | Too little → thin; too much → boomy |
| Warmth | `w` | `tanh((rms_low_mid + 10) / 10)` | 0–1 | Low-mid presence; vocal body |
| Clarity | `c` | `tanh((rms_mid + 10) / 10)` | 0–1 | Mid-range intelligibility |
| Presence Energy | `p` | `tanh((rms_presence + 15) / 12)` | 0–1 | Vocal presence and articulation |
| Density | `d` | `1.0 - min(1.0, crest_factor / 12.0)` | 0–1 | How "full" the waveform feels |
| Stereo Width | `s` | `1.0 - abs(correlation_lr)` | 0–1 | Mono=0, wide=1 |
| Transient Energy | `t` | `tanh((peak_db - rms_total - 6) / 8)` | 0–1 | Attack and punch |
| Reality Index | `r` | `1.0 - abs(dynamic_range_db - 12) / 18` | 0–1 | Naturalness of dynamics |

All features clamped to `[0, 1]` via `tanh` or linear clamp.

## Per-Genre Weights (Draft v0.2)

Each genre assigns an 8-element weight vector `w_g`:

| Genre | b | w | c | p | d | s | t | r |
|-------|---|---|---|---|---|---|---|---|
| **vocal** | 0.7 | 1.0 | 1.0 | 1.0 | 0.6 | 0.5 | 0.5 | 0.8 |
| **piano** | 0.8 | 0.8 | 0.9 | 0.6 | 0.5 | 0.3 | 0.9 | 1.0 |
| **electronic** | 1.0 | 0.6 | 0.7 | 0.8 | 0.9 | 0.9 | 0.7 | 0.4 |
| **orchestral** | 0.8 | 0.8 | 0.7 | 0.5 | 0.4 | 0.7 | 0.6 | 1.0 |
| **default** | 0.8 | 0.8 | 0.8 | 0.8 | 0.7 | 0.6 | 0.7 | 0.8 |

Weighted feature distance: `d(a, b) = sqrt(sum(w_g[i] * (f_a[i] - f_b[i])^2 for i in 0..7))`

## Implementation

| Component | Build MHP | Owner |
|-----------|-----------|-------|
| `compute_feature_vector(metrics: AudioMetrics) -> FeatureVector` | MHP-865 | Worker |
| `load_genre_weights(genre: str) -> dict` | MHP-865 | Worker |
| `yaml` config for genre weights | MHP-865 | Worker |
| `FeatureVector` dataclass in `v01_types.py` | MHP-863 | Architect approval |

## Acceptance Criteria

- [x] All 8 feature dimensions defined with formulas based on existing AudioMetrics fields.
- [x] Per-genre weights defined for 5 genre classes.
- [x] Weighted distance formula specified.
- [x] Build NEM task (MHP-865) is the implementation boundary.
