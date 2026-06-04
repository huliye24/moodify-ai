# Sample Class Coverage Audit — MHP-146

**Date**: 2026-06-04

## Genre Coverage

| Genre | Samples in Dataset | Presets Tested Per Sample | Total Test Points |
|-------|-------------------|--------------------------|-------------------|
| electronic | 13 | 1 (clean_master) | 13 |
| piano | 15 | 1 (warm_vocal) | 15 |
| vocal | 16 | 1 (warm_vocal) | 16 |
| rock | 11 | 1 (wide_space) | 11 |
| ambient | 6 | 1 (wide_space) | 6 |
| **Total** | **61** | **1 per genre** | **61** |

## Coverage Gap

Every sample is tested with exactly ONE preset (the genre-default). No cross-preset comparison exists. This means we can't answer: "Does warm_vocal or clean_master work better for this specific piano track?"

## What's Missing for Craft Memory

| Capability | Status |
|------------|--------|
| Per-sample preset comparison | ❌ |
| Per-preset genre breakdown | ❌ |
| Preset failure signature per genre | ❌ |
| Craft record with before/after audio | ❌ |
