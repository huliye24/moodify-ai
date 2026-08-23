# MRS Metric Inputs

**Status:** Current inputs and research placeholders. This document does not define a validated perceptual model.

MRS research separates observable signal measurements from listening claims. Current implementation and repository analysis expose metrics in the following groups.

## Loudness

- **LUFS** — integrated loudness measurement where the relevant measurement path and dependency are available.
- **RMS** — signal-energy proxy used by analysis and selected fallbacks.
- **Peak level** — sample-peak information relevant to headroom and clipping checks.

## Dynamic

- **Dynamic range** — a representation of level variation over time.
- **Crest-factor-related measures** — peak-to-average relationships used by diagnosis.

## Spectral

- **Frequency distribution** — band-energy and spectral-shape observations.
- **Spectral centroid and related descriptors** — present in analysis or existing MRS feature extraction paths.

## Spatial

- **Stereo information** — left/right correlation and related spatial proxies.

## Use in MRS

These measures are input factors, not a complete definition of audio quality. The standalone MRS baseline accepts normalized factors (`loudness`, `dynamic`, `spectral`, `spatial`, and `artifact`) so that future benchmark protocols can define how raw measurements are normalized, weighted, and validated for a specific task.

No complete AI listening model, human-preference dataset, or validated mapping from these metrics to listener preference is asserted.
