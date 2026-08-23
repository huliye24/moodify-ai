# Era Diagnostic Report v0.1

**Source:** E:\moodify\moodify-core-package\era_cli_smoke.wav
**Era hint (metadata only, not a decision input):** 1987

> No reconstruction action was authorized by this diagnostic alone.

## ED-01 — NOT_APPLICABLE (confidence: -)

no bandwidth limitation observed (HF cutoff >= 16 kHz)

Evidence:
- estimated_high_frequency_cutoff_hz

Requires human review: no
Action: NONE_IN_P03

## ED-02 — NOT_APPLICABLE (confidence: -)

no elevated noise floor observed (p10 frame RMS ~-120.0 dBFS)

Evidence:
- estimated_noise_floor_dbfs

Requires human review: no
Action: NONE_IN_P03

## ED-03 — NOT_APPLICABLE (confidence: -)

no dynamic constraint/damage evidence (no clipping, normal dynamics)

Evidence:
- clipping_sample_ratio

Requires human review: no
Action: NONE_IN_P03

## ED-04 — NOT_APPLICABLE (confidence: -)

no stereo/phase limitation evidence (correlation 0.974)

Evidence:
- stereo_correlation

Requires human review: no
Action: NONE_IN_P03

## ED-05 — OBSERVED (confidence: LOW)

spectrally dense (flatness 0.017, core-mid 0.30); possible congestion observed — no defect claim in v0.1

Evidence:
- spectral_flatness
- core_mid_500_2000_hz

Ambiguity:
- dense arrangement is an artistic choice; congestion cannot be separated from arrangement density in v0.1

Requires human review: no
Action: NONE_IN_P03

## ED-06 — NOT_SUPPORTED_IN_V0_1 (confidence: -)

no validated transfer/encoding detector in v0.1; codec/transcode degradation is NOT_SUPPORTED

Evidence:
- sample_rate

Ambiguity:
- reliable block/codec artifact detection is deferred

Requires human review: no
Action: NONE_IN_P03

---
*Diagnosis only. It does not authorize processing.*