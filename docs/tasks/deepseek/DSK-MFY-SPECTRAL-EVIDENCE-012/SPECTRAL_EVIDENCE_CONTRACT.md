# SPECTRAL_EVIDENCE_CONTRACT — v0.1

**Status:** Frozen before code.

## Input Model

```yaml
case_id: string
title: string
tracks:
  - track_id: string
    role: full_mix | vocals | drums | bass | piano | guitar | other
    before:
      path: absolute_or_relative
    after:
      path: absolute_or_relative
```

- `role` is explicit; never inferred from filename.
- `before` and `after` must both exist and be readable WAV/FLAC.
- Missing stem → that track is skipped with WARN in manifest.

## Analysis Parameters (fixed per run)

```yaml
sample_rate: 22050  # or native
n_fft: 2048
hop_length: 512
window: hann
channels: mono  # or left/right separately; never arbitrary
amplitude_scale: dB
db_range: 80  # symmetric around 0 dB
loudness_match: false  # separate run for matched comparison
```

Before/after use identical parameters. Difference = after - before (dB domain).

## Output Evidence per Track

```
{track_id}_before.png
{track_id}_after.png
{track_id}_difference.png
{track_id}_metrics.json
```

## Difference Semantics
- Positive value → after has more energy in that bin
- Negative value → after has less
- NOT a quality judgment
- Colorbar must label "Δ dB (after − before)"
