# AUDIT C — Reproducibility Comparison

**Task**: DSK-MFY-DAY2-CLOSURE-003  
**Date**: 2026-07-31

## Process Output — Byte-Identical

| Field | Original | Replay | Match |
|---|---|---|---|
| Output WAV SHA-256 | `475778a3...` | `475778a3...` | YES |
| Output WAV size | 34,429,484 | 34,429,484 | YES |
| Elapsed time | 164.8 s | 156 s | ~5% difference |

## Validation Report — Field-Identical

| Field | Original | Replay | Match |
|---|---|---|---|
| passed | false | false | YES |
| dynamic_range_db | -7.61 | -7.61 | YES |
| peak_db | 3.7 | 3.7 | YES |
| crest_factor | -0.87 | -0.87 | YES |
| correlation_lr | -0.062 | -0.062 | YES |
| air | 1.15 | 1.15 | YES |
| presence | 1.76 | 1.76 | YES |
| bass | -0.37 | -0.37 | YES |
| mrs_before | 1106.69 | 1106.69 | YES |
| mrs_after | 1131.51 | 1131.51 | YES |
| mrs_delta | 24.82 | 24.82 | YES |
| damage_loss | 0.208 | 0.208 | YES |
| risk_flags | ["dynamic_damage"] | ["dynamic_damage"] | YES |

All 13 validation fields identical. Process output is byte-identical.

## Inspector after_matched.wav — Quantization-Level Difference

| Field | Original | Replay |
|---|---|---|
| SHA-256 | `014e2ae8...` | `13400033...` |
| Size | 34,429,484 | 34,429,484 |
| RMS matched | -15.72 dB | -15.72 dB |
| Samples differing | 0 / 17,214,720 | 91 / 17,214,720 |
| Max difference | 0 | 1 PCM_16 LSB |
| Correlation | 1.0 | 1.0 |

The SHA-256 difference is explained by PCM_16 quantization: 91 samples at exact 0.5-LSB boundaries round in different directions. The audio content is identical to within 1 quantization level. Correlation between original and replay is 1.0000000000.

## Inspector Metrics Comparison

| Field | Original | Replay | Match |
|---|---|---|---|
| rms_delta_db | 5.89 | 5.89 | YES |
| peak_delta_db | 3.7 | 3.7 | YES |
| dynamic_range_delta_db | -7.61 | -7.65* | ~0.5% |
| after_gain_match_db | -5.89 | -5.89 | YES |
| warning_level | strong | strong | YES |

*Dynamic range delta differs slightly (-7.61 vs -7.65) because the manual metrics generator uses a simplified percentile-of-window-RMS computation. The process validation_report.json value (-7.61) is authoritative. This does not affect the technical gate result.

## Treatment Record Comparison

| Field | Original | Replay | Match |
|---|---|---|---|
| preset | warm_vocal | warm_vocal | YES |
| song_id | vs001_ai_vocal_20260731 | vs001_ai_vocal_20260731_replay | ID differs (intentional) |
| preset_params | 15 params | 15 params | YES |
| delta_features count | 11 | 11 | YES |
| dynamic_range_delta_db | -7.61 | -7.61 | YES |
| rms_delta_db | 5.89 | 5.89 | YES |
| human_feedback.status | pending | pending | YES |

## Known Non-Stable Fields (Expected Differences)

These fields are expected to differ between runs and do not indicate a reproducibility failure:

1. **metadata.json timestamps**: `generated_at` reflects current UTC time
2. **manifest.json timestamps**: `generated_at` and `pipeline.elapsed_s` vary
3. **Report PDF**: Binary layout differs (font rendering, timestamps)
4. **PNG plots**: Binary layout differs (matplotlib rendering, timestamps)
5. **after_matched.wav**: PCM_16 quantization rounding (±1 LSB on boundary values)

## Summary

The processing pipeline is fully reproducible at the byte level for the primary output WAV. All 13 validation metrics are identical. The only non-reproducible artifact (after_matched.wav) differs by 1 PCM_16 quantization level on 0.0005% of samples. The inspector spectrogram step is blocked by a 525 MB memory allocation requirement on this 8 GB machine.
