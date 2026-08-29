# Moodify Metric Registry v1

**Registry ID:** `MFY-METRIC-REGISTRY-001`
**Version:** 1.0
**Date:** 2026-08-11
**Profile:** MFY-WSE-SCAN-PROFILE-001 (hash f0ff177d…)
**Reference suite:** [MFY-REFERENCE-AUDIO-SUITE-001](../../moodify-core-package/benchmarks/reference_audio/REFERENCE_SUITE.md)

## Tier rules

- **Tier A — Reference:** formal external definition, trusted implementation, deterministic fixture, documented tolerance. A regression here stops production.
- **Tier B — Stable Moodify:** frozen formula, unit, test vector, version, tolerance. Formula changes require a registry version bump.
- **Tier C — Experimental:** research-only; never a silent training feature.

## Tier A — Reference metrics

| Metric | Unit | Definition / method | Implementation | Fixture | Tolerance |
|---|---|---|---|---|---|
| integrated_lufs | LUFS | ITU-R BS.1770-4 (EBU R128 gated) | moodify.auditory.metrics | dynamic_program.wav, sine_1khz.wav | ±0.01 LUFS vs suite expectation |
| loudness_range_lu | LU | EBU 3342 (short-term) | moodify.auditory.metrics | dynamic_program.wav | ±0.01 LU |
| true_peak_dbfs | dBTP | ITU-R BS.1770 true-peak (4x oversample) | moodify.auditory.metrics | impulse.wav, clipped.wav | ±0.01 dBTP |
| sample_peak_dbfs | dBFS | direct sample peak | moodify.auditory.metrics | sine_1khz.wav | exact (-6.02 dBFS) |
| rms_dbfs | dBFS | frozen Moodify windowed RMS | moodify.auditory.metrics | sine_1khz.wav | ±0.01 dB |
| crest_factor_db | dB | peak − RMS | moodify.auditory.metrics | sine_1khz.wav (3.01 dB) | ±0.05 dB |
| plr_db | dB | peak-to-loudness ratio | moodify.auditory.metrics | dynamic_program.wav | ±0.05 dB |
| clipping_sample_count | count | sample ≥ 0.999 FS | moodify.auditory.metrics | clipped.wav (>0), sine_1khz.wav (=0) | exact sign |
| invalid_sample_count | count | non-finite samples | moodify.auditory.metrics | suite | = 0 |
| dc_offset_left / dc_offset_right | linear | per-channel mean | moodify.auditory.metrics | silence.wav | ≈ 0 (1e-6) |
| duration | s | decoded duration | moodify.auditory.probe | all fixtures | exact |
| sample_rate / channels | — | container properties | moodify.auditory.probe | all fixtures | exact |

## Tier B — Stable Moodify metrics

| Metric | Unit | Definition (frozen formula) | Fixture | Tolerance |
|---|---|---|---|---|
| spectral_centroid_hz | Hz | power-weighted mean frequency of STFT | sine_1khz.wav (=1000) | ±1 Hz |
| spectral_rolloff_85_hz / 95_hz | Hz | cumulative power percentile | dual_tone.wav | ±10 Hz |
| spectral_flatness | ratio | geometric/arithmetic mean of power spectrum | pink_noise.wav (≈0.98) | ±0.01 |
| spectral_flux | mag/frame | positive frame-to-frame spectral delta | dynamic_program.wav | ±0.1% |
| band_energy_* | linear-power | energy in fixed bands (sub 20-60, bass 60-120, low_mid 120-250, mid 250-500, core_mid 500-2000, presence 2000-5000, brilliance 5000-10000, air 10000-16000, ultrasonic 16000-24000) | dual_tone.wav | ±0.1% |
| band ratios (sub_20_60_hz … air_10000_16000_hz) | ratio | band energy / total energy | dual_tone.wav | ±1e-4 |
| mid_energy_ratio, side_energy_ratio, side_to_mid_db, stereo_width_proxy | ratio/dB | mid/side decomposition descriptors | stereo_correlated.wav / stereo_phase_inverted.wav | ±0.01 / ±0.1 dB |
| stereo_correlation | ratio | mid-side correlation | stereo_* fixtures (1.0 / -1.0) | ±1e-4 |
| negative_correlation_ratio | ratio | frames with strong anti-correlation | stereo_phase_inverted.wav (=1.0) | ±1e-4 |
| phase_risk_ratio | ratio | phase-risk frame fraction | stereo_phase_inverted.wav | ±1e-4 |
| estimated_high_frequency_cutoff_hz | Hz | 99.5% cumulative power point | sine_1khz.wav | ±100 Hz |
| estimated_noise_floor_dbfs | dBFS | P10 frame RMS estimate | silence.wav | ±3 dB |
| longest_silence_seconds | s | longest below-threshold run | sine_1khz.wav (=0) | exact |
| silence_ratio | ratio | below-threshold frame fraction | sine_1khz.wav (=0) | ±1e-4 |
| near_clipping_sample_count | count | samples ≥ 0.9 FS | suite | exact sign |
| finite_sample_ratio | ratio | valid samples / total | suite (=1.0) | exact |
| clipping_sample_ratio | ratio | clipped / total | clipped.wav | ±1e-6 |

## Tier C — Experimental

| Metric | Status | Rule |
|---|---|---|
| compound "quality" scores | EXPERIMENTAL | research-only; excluded from training features |
| subjective emotion/heuristic claims | EXPERIMENTAL | never a core training feature without evidence |

## Versioning

- Registry changes = new version + new scan profile hash. Historical rows are
  never re-interpreted under a new definition (freeze protocol §1.4).
- Cross-machine determinism (52/52 identical, 2026-08-11) is a registry-level
  invariant; a nonzero diff on the reference suite is a regression.
