"""Era Diagnostic policy + versioned thresholds (MFY-CR-P03).

This is the *diagnostic eligibility layer* the task requires: it expresses
finer-grained permissions than the global measurement registry's
``judgment_eligible`` boolean, WITHOUT touching that registry.

Classes (see 03_VALIDATION_MATRIX.md):
    ELIGIBLE_FOR_DIAGNOSTIC  — metric may drive diagnostic status/confidence
    KEEP_DESCRIPTIVE_ONLY    — metric may appear in reports, never drives a decision
    ELIGIBLE_FOR_GUARDRAIL   — reserved; nothing in v0.1
    REJECT_OR_REWORK         — metric must not be used
"""

from __future__ import annotations

ERA_DIAGNOSTIC_POLICY_V1 = {
    "version": "era-diagnostic-policy-v1",
    "schema_version": "1.0",
    "metric_eligibility": {
        # ED-01 bandwidth
        "estimated_high_frequency_cutoff_hz": "ELIGIBLE_FOR_DIAGNOSTIC",
        "spectral_rolloff_95_hz": "ELIGIBLE_FOR_DIAGNOSTIC",
        "spectral_rolloff_85_hz": "KEEP_DESCRIPTIVE_ONLY",
        "spectral_centroid_hz": "KEEP_DESCRIPTIVE_ONLY",
        "presence_2000_5000_hz": "ELIGIBLE_FOR_DIAGNOSTIC",
        "air_10000_16000_hz": "KEEP_DESCRIPTIVE_ONLY",
        # ED-02 noise
        "estimated_noise_floor_dbfs": "ELIGIBLE_FOR_DIAGNOSTIC",
        "silence_ratio": "ELIGIBLE_FOR_DIAGNOSTIC",
        "longest_silence_seconds": "KEEP_DESCRIPTIVE_ONLY",
        "spectral_flatness": "ELIGIBLE_FOR_DIAGNOSTIC",
        # ED-03 dynamics
        "clipping_sample_ratio": "ELIGIBLE_FOR_DIAGNOSTIC",
        "clipping_sample_count": "KEEP_DESCRIPTIVE_ONLY",
        "true_peak_dbfs": "ELIGIBLE_FOR_DIAGNOSTIC",
        "loudness_range_lu": "ELIGIBLE_FOR_DIAGNOSTIC",
        "crest_factor_db": "ELIGIBLE_FOR_DIAGNOSTIC",
        "plr_db": "KEEP_DESCRIPTIVE_ONLY",
        # ED-04 stereo / phase
        "stereo_correlation": "ELIGIBLE_FOR_DIAGNOSTIC",
        "phase_risk_ratio": "ELIGIBLE_FOR_DIAGNOSTIC",
        "negative_correlation_ratio": "ELIGIBLE_FOR_DIAGNOSTIC",
        "stereo_width_proxy": "KEEP_DESCRIPTIVE_ONLY",
        "side_to_mid_db": "KEEP_DESCRIPTIVE_ONLY",
        # ED-06 transfer
        "sample_rate": "ELIGIBLE_FOR_DIAGNOSTIC",
        "channels": "KEEP_DESCRIPTIVE_ONLY",
        # ED-05 congestion (observational in v0.1)
        "sub_20_60_hz": "KEEP_DESCRIPTIVE_ONLY",
        "bass_60_120_hz": "KEEP_DESCRIPTIVE_ONLY",
        "low_mid_120_250_hz": "KEEP_DESCRIPTIVE_ONLY",
        "mid_250_500_hz": "KEEP_DESCRIPTIVE_ONLY",
        "core_mid_500_2000_hz": "ELIGIBLE_FOR_DIAGNOSTIC",
        "brilliance_5000_10000_hz": "KEEP_DESCRIPTIVE_ONLY",
    },
    "thresholds": {
        "bandwidth": {
            "clean_cutoff_hz": 16000.0,      # at/above this: no bandwidth limitation
            "strong_cutoff_hz": 12000.0,     # at/below this: strong bandwidth signal
            "severe_cutoff_hz": 10000.0,     # at/below this: HIGH confidence (synthetic-validated)
            "rolloff_95_corrob_ratio": 0.8,  # rolloff95 must sit below cutoff*ratio to corroborate
            "presence_band_min_ratio": 0.001,  # below this the source is likely dark by nature
        },
        "noise": {
            "elevated_floor_dbfs": -65.0,    # at/above this: floor is elevated
            "strong_floor_dbfs": -55.0,      # at/above this: strong noise signal
            "min_silence_ratio": 0.005,      # below this: no reliable quiet windows
        },
        "dynamic": {
            "clipping_ratio": 0.00005,       # at/above this: clipping observed
            "strong_clipping_ratio": 0.0005, # at/above this: heavy clipping
            "peak_ceiling_dbfs": -0.5,       # true peak at/above this corroborates clipping
            "peak_hard_ceiling_dbfs": -0.1,  # true peak at/above this: strong corroboration
            "low_lra_lu": 4.0,               # descriptive low-dynamics observation
            "low_crest_db": 6.0,             # descriptive low-dynamics observation
        },
        "stereo": {
            "mono_correlation": 0.999,       # at/above this: essentially mono
            "narrow_correlation": 0.98,      # at/above this: narrow stereo
            "phase_risk_ratio": 0.10,        # at/above this: phase risk elevated
            "negative_corr_ratio": 0.05,     # at/above this: antiphase content present
        },
        "congestion": {
            "peaky_flatness": 0.05,          # below this: spectrally peaky/dense
        },
        "transfer": {
            "low_sample_rate_hz": 44100,     # below this: possible downsampled source
        },
    },
}
