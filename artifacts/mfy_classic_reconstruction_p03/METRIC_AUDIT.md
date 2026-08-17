# MFY-CR-P03 — Metric Audit

Audited against the real code (P01/P02 baseline). Source of truth:
`configs/measurement_registry_v1.yaml` + `moodify/auditory/metrics.py` +
`moodify/auditory/stereo.py`.

## Candidate metrics

| Metric | Source | Unit | Deterministic | Judgment eligible (global) | Diagnostic eligibility (new layer) |
|---|---|---|---|---|---|
| estimated_high_frequency_cutoff_hz | metrics.py (cumulative 99.5%) | Hz | yes | **false** | ELIGIBLE_FOR_DIAGNOSTIC |
| spectral_rolloff_95_hz | metrics.py (STFT cumulative) | Hz | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| spectral_rolloff_85_hz | metrics.py | Hz | yes | false | KEEP_DESCRIPTIVE_ONLY |
| spectral_centroid_hz | metrics.py | Hz | yes | false | KEEP_DESCRIPTIVE_ONLY |
| presence_2000_5000_hz | metrics.py (band ratio) | ratio | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| air_10000_16000_hz | metrics.py (band ratio) | ratio | yes | false | KEEP_DESCRIPTIVE_ONLY |
| estimated_noise_floor_dbfs | metrics.py (p10 frame RMS) | dBFS | yes | **false** | ELIGIBLE_FOR_DIAGNOSTIC |
| silence_ratio | metrics.py (windowed RMS) | ratio | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| longest_silence_seconds | metrics.py | s | yes | false | KEEP_DESCRIPTIVE_ONLY |
| spectral_flatness | metrics.py (STFT) | ratio | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| clipping_sample_ratio | metrics.py (direct) | ratio | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| clipping_sample_count | metrics.py | samples | yes | true | KEEP_DESCRIPTIVE_ONLY |
| true_peak_dbfs | true_peak.py (4x oversample) | dBFS | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| loudness_range_lu | loudness.py (EBU 3342) | LU | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| crest_factor_db | metrics.py (derived) | dB | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| plr_db | metrics.py (derived) | dB | yes | false | KEEP_DESCRIPTIVE_ONLY |
| stereo_correlation | stereo.py (pearson) | ratio | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| phase_risk_ratio | stereo.py (windowed rule) | ratio | yes | true | ELIGIBLE_FOR_DIAGNOSTIC |
| negative_correlation_ratio | stereo.py (frame-wise) | ratio | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| stereo_width_proxy | stereo.py (derived) | ratio | yes | false | KEEP_DESCRIPTIVE_ONLY |
| side_to_mid_db | stereo.py (derived) | dB | yes | false | KEEP_DESCRIPTIVE_ONLY |
| core_mid_500_2000_hz | metrics.py (band ratio) | ratio | yes | false | ELIGIBLE_FOR_DIAGNOSTIC |
| sample_rate | ffprobe | Hz | yes | n/a | ELIGIBLE_FOR_DIAGNOSTIC |
| channels | ffprobe | ch | yes | n/a | KEEP_DESCRIPTIVE_ONLY |

## Known failure modes (from validation)

1. **estimated_hf_cutoff is coarse on tonal content**: with sparse tone fixtures
   the 99.5 % cumulative point jumps between tones (e.g. ~12 kHz regardless of an
   8-9 kHz low-pass). Bandwidth findings therefore rely on rolloff-95
   corroboration and are capped LOW/MEDIUM unless the cutoff is very low.
2. **estimated_noise_floor measures quiet frames, not true noise**: a loud hiss
   that fills all quiet windows yields INSUFFICIENT_EVIDENCE, not a confident
   noise finding (observed on the -50 dBFS ladder step). Conservative by design.
3. **stereo_correlation cannot separate intentional mono from mono transfer**:
   the engine classifies near-mono as LIKELY_ARTISTIC_CHARACTER with ambiguity,
   never as a defect.
4. **spectral_flatness conflates dense arrangement with spectral congestion**:
   ED-05 stays observational (OBSERVED, LOW) in v0.1.
5. **Delay-based decorrelation scatters high-frequency tones** (fixture lesson):
   correlation fixtures must use same-phase gain + music-only noise, not delay.

## Policy enforcement

- Every metric a detector reads is declared in `DETECTOR_INPUTS` and enforced
  to be ELIGIBLE_FOR_DIAGNOSTIC by `test_policy_enforcement`.
- `test_judgment_eligibility_untouched` asserts the global registry still has
  `judgment_eligible: false` for the two estimators.
