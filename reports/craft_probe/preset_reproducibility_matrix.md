# Preset Reproducibility Matrix — MHP-157

**Date**: 2026-06-04

## Test: Same input × same preset × 2 runs

| Sample | Preset | Run 1 pseudo_delta | Run 2 pseudo_delta | Identical? |
|--------|--------|--------------------|--------------------|------------|
| piano | warm_vocal | -24.15 | -24.15 | ✅ Yes — deterministic DSP |
| electronic | clean_master | -3.81 | -3.81 | ✅ Yes |
| vocal | warm_vocal | -31.97 | -31.97 | ✅ Yes |

DSP processing is deterministic (fixed parameters, no randomness). Reproducibility = 100% for identical inputs.

## Caveat

If preset parameters are changed between runs, output differs. This is expected — versioning (MHP-181) tracks parameter changes.
