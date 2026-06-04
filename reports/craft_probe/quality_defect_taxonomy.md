# Quality Defect Taxonomy — MHP-145

**Date**: 2026-06-04

## Preset Quality Defects

| Class | Symptom | Detection | Presets Affected | Severity |
|-------|---------|-----------|-----------------|----------|
| OVER_DARK | Bass energy accumulates in 20-300Hz | over_dark.py (FFT) | warm_vocal (piano worst) | P0 |
| OVER_BRIGHT | High shelf pushes 8k-20kHz too hot | pseudo_mrs peak_score | clean_master | P1 |
| TRANSIENT_SMEAR | Attack transients softened too much | crest_factor drop >30% | wide_space, warm_vocal | P1 |
| VOCAL_THINNING | Vocal presence gain removes body | RMS drop in 200-500Hz | Not systematically detected | P1 |
| STEREO_COLLAPSE | Width processing narrows image | crest_factor + stereo correlation | wide_space | P2 |
| LOUDNESS_WAR | Compression ratio too high → flat dynamics | crest_factor < 3.0 | dynamic_recovery category | P1 |
| DC_DRIFT | DC offset introduced by processing | analyze_wav_stdlib dc_offset | All (rare) | P3 |
| CLIPPING | Peak exceeds 0dBFS | peak > 0.999 | Any with high gain | P0 |

## Detection Coverage

| Defect | Detector Exists? | Automated? | Gate Integrated? |
|--------|-----------------|------------|-----------------|
| OVER_DARK | ✅ over_dark.py | ✅ FFT | ✅ decide_candidate_gate |
| OVER_BRIGHT | ❌ | — | ❌ |
| TRANSIENT_SMEAR | ⚠️ crest_factor computed but not gated | ❌ | ❌ |
| VOCAL_THINNING | ❌ | — | ❌ |
| STEREO_COLLAPSE | ❌ | — | ❌ |
| LOUDNESS_WAR | ⚠️ crest tracked but no gate | ❌ | ❌ |
| DC_DRIFT | ✅ dc_offset in metrics | ❌ | ❌ |
| CLIPPING | ✅ peak_score in pseudo_mrs | ❌ | ❌ |

Only 2 of 8 defect classes are gated. The rest are computed but not enforced.
