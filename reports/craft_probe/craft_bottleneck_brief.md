# Craft Bottleneck Brief — MHP-147

**Date**: 2026-06-04

## Top 5 Bottlenecks

### 1. No Preset Safety Gate (P0)
- presets can be added/changed without automated safety validation
- safe_air exists but has zero tests
- Fix: PresetSafetyGate (MHP-165) that runs batch validation before adopting a preset

### 2. No Cross-Preset Comparison (P0)
- each sample tested with only 1 preset
- can't rank presets per sample or per genre
- Fix: PresetExperimentRunner (MHP-163) that processes 1 sample through N presets

### 3. No Over-Bright Detection (P1)
- over_dark detects bass accumulation but no symmetric detector for treble excess
- Fix: over_bright probe (MHP-149)

### 4. Craft Records Not Searchable (P2)
- 13 records in JSONL, accessible only via API
- no genre/preset/adoption_status filter in Console
- Fix: Craft CLI (MHP-167) + Console views (MHP-169)

### 5. No Preset Versioning (P1)
- preset parameters change, but no version history
- can't answer "what parameters produced this craft record?"
- Fix: Preset Versioning Spec (MHP-181)

## Risk Summary

| Risk | Likelihood | Severity |
|------|-----------|----------|
| Untested preset causes audio damage in prod | Medium | High |
| Preset regression from parameter change | Medium | Medium |
| Craft library becomes unmanageable at scale | Low | Medium |
