# MFY-CR-P05 — Identity Dimensions

Six-dimensional protection (no identity score). Capability label per
dimension: MEASURABLE / PROXY / PARTIAL / NOT_MEASURABLE.

| Dimension | Capability | Metrics (source vs candidate delta) | What it protects |
|---|---|---|---|
| IG-01 Vocal/Mid | **PROXY** | mid_energy_ratio, presence_2000_5000_hz, core_mid_500_2000_hz, spectral_centroid_hz | singer presence, mid character |
| IG-02 Dynamics | **MEASURABLE** | loudness_range_lu, crest_factor_db, plr_db | attack, punch, macro/micro dynamics |
| IG-03 Reverb/Space | **NOT_MEASURABLE** | (none validated in v0.1) | room/plate/hall tail, era spatial signature |
| IG-04 Stereo | **MEASURABLE** | stereo_correlation, stereo_width_proxy, side_to_mid_db + mono guard | mono identity, narrow character, panning |
| IG-05 Low-end | **MEASURABLE** | sub_20_60_hz, bass_60_120_hz band ratios | bass tone, kick/bass balance |
| IG-06 Loudness/Density | **MEASURABLE** | integrated_lufs, clipping_sample_ratio | loudness relationships, density, breathing room |

## Honesty rules

- IG-01 is explicitly NOT a vocal identity model — it is a mid-band proxy set.
  Drift beyond budget → HUMAN_REQUIRED, never REJECT, never "singer changed".
- IG-03 has no validated decay/late-energy detector in v0.1 → always
  NOT_MEASURABLE; because it is a critical dimension, ANY other dimension
  showing change escalates the overall verdict to HUMAN_REQUIRED.
- Mono/narrow source widening is guarded as identity damage
  (mono → wide is never a default improvement).
