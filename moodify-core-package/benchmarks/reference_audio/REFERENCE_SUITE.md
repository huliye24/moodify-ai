# Moodify Reference Audio Suite

**Suite ID:** `MFY-REFERENCE-AUDIO-SUITE-001`
**Generated:** 2026-08-11, deterministic (seed 20260811, 48 kHz)
**Regenerate:** `python benchmarks/reference_audio/generate_reference_suite.py`
**Expected values:** `expected/expected_values.json` (scanned with MFY-WSE-SCAN-PROFILE-001)

## Purpose

Deterministic test audio for Gate 2 measurement validation: every fixture has a
known physical meaning, an expected value on key metrics, and a stable sha256.
A metric regression is defined as a scan result on this suite that moves outside
the documented tolerance.

## Fixtures

| Fixture | Purpose | sha256 (prefix) | Key expected behavior |
|---|---|---|---|
| silence.wav | e294409b36a8ac18… | measurement floor |  | rms_dbfs ≈ -240 (sentinel), integrated_lufs ≈ -70 |
| sine_1khz.wav | 8446efde7f308621… | tone reference |  | spectral_centroid = 1000 Hz, crest_factor = 3.01 dB, sample_peak = -6.02 dBFS |
| dual_tone.wav | 4cbb01e3484e99d9… | band separation |  | energy in 440 Hz + 3000 Hz bands, near-zero elsewhere |
| impulse.wav | 1f7a36b714a710b3… | peak / transient |  | sample_peak ≈ 0 dBFS, true_peak > 0 |
| clipped.wav | ef2bf88b2c2a15ed… | clipping detection |  | clipping_sample_count > 0, sample_peak = 0 dBFS |
| mono.wav | b278496685004e6f… | channel layout |  | channels = 1 |
| stereo_correlated.wav | 4cf5759919040c87… | phase integrity |  | stereo_correlation = 1.0 |
| stereo_phase_inverted.wav | 4d95360df83defd4… | phase risk |  | stereo_correlation = -1.0, negative_correlation_ratio = 1.0 |
| pink_noise.wav | 617aea8a11dc0548… | spectrum flatness |  | spectral_flatness ≈ 0.98 |
| dynamic_program.wav | e8e61feabb008ee6… | loudness range |  | integrated_lufs ≈ -12.6, loudness dynamics present |

## Validation rules (G2-03)

- **Exact-match metrics** (sample_rate, channels, duration, clipping_sample_count,
  invalid_sample_count, finite_sample_ratio): tolerance 0.
- **Continuous metrics**: tolerance 0 observed across machines
  (see [G4-04 cross-machine report](../../../artifacts/g4_04_cross_machine_001/CROSS_MACHINE_REPEATABILITY_REPORT.md));
  guard tolerance <= 1e-6 absolute for all suite fixtures.

## Usage

```text
1. python generate_reference_suite.py            # bit-reproducible fixtures
2. scan each fixture with MFY-WSE-SCAN-PROFILE-001
3. compare against expected/expected_values.json
4. any out-of-tolerance value = metric regression → stop production
```
