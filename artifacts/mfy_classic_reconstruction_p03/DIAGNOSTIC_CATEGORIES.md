# MFY-CR-P03 — Diagnostic Categories

Implemented in `moodify/era_diagnostic/engine.py`, contract in `contract.py`.

## Decision model

Every finding carries status + confidence:

```text
status: OBSERVED | POSSIBLE_TECHNICAL_LIMITATION | LIKELY_ARTISTIC_CHARACTER
        | INSUFFICIENT_EVIDENCE | NOT_APPLICABLE | NOT_SUPPORTED_IN_V0_1
confidence: LOW | MEDIUM | HIGH
```

Evidence rule: POSSIBLE_TECHNICAL_LIMITATION requires >= 1 primary metric +
>= 1 corroborating metric + a known-ambiguity statement (enforced in
`test_evidence_rule`). No finding authorizes reconstruction.

## ED-01 Bandwidth Limitation

- Primary: `estimated_high_frequency_cutoff_hz`; corroborating:
  `spectral_rolloff_95_hz`; dark-source guard: `presence_2000_5000_hz`.
- Clean (>= 16 kHz) → NOT_APPLICABLE. Low cutoff + rolloff corroboration →
  POSSIBLE; <= 10 kHz → HIGH; <= 12 kHz → MEDIUM; else LOW.
- Presence band nearly empty → LIKELY_ARTISTIC_CHARACTER (dark by nature).
- No rolloff corroboration → INSUFFICIENT_EVIDENCE.

## ED-02 Persistent Noise

- Primary: `estimated_noise_floor_dbfs`; corroborating: `silence_ratio`;
  context: `spectral_flatness` (tonal/hum ambiguity).
- Quiet floor (< -65 dBFS) → NOT_APPLICABLE. Elevated floor + quiet windows
  present → POSSIBLE (>= -55 dBFS → MEDIUM, else LOW).
- No reliable quiet windows → INSUFFICIENT_EVIDENCE (loud hiss that fills
  silence is NOT auto-called technical noise).

## ED-03 Dynamic Damage

- Primary: `clipping_sample_ratio`; corroborating: `true_peak_dbfs`;
  context: `loudness_range_lu`, `crest_factor_db`.
- Clipping + peaks at ceiling → POSSIBLE (heavy clipping + hard ceiling → MEDIUM).
- Clipping without ceiling → OBSERVED (may be intentional distortion).
- Low LRA + low crest without clipping → OBSERVED, ambiguity = genre aesthetic.
- "Dynamic small" is never called a defect by itself.

## ED-04 Stereo / Phase

- Primary: `stereo_correlation`; corroborating: `phase_risk_ratio`,
  `negative_correlation_ratio`.
- corr >= 0.999 → LIKELY_ARTISTIC_CHARACTER (intentional mono; mono transfer
  ambiguity recorded).
- 0.98 <= corr < 0.999 → OBSERVED narrow; NARROW_BY_CHARACTER vs
  POSSIBLE_TECHNICAL_COLLAPSE explicitly undecidable in v0.1 (ambiguity).
- Phase risk + negative correlation both elevated → POSSIBLE MEDIUM; single
  proxy → POSSIBLE LOW.

## ED-05 Spectral Congestion

- Observational only in v0.1: peaky spectrum + dense core-mid → OBSERVED, LOW,
  ambiguity "dense arrangement is artistic". Never a defect claim, never EQ advice.

## ED-06 Transfer / Encoding

- No validated codec/transcode detector in v0.1 → NOT_SUPPORTED_IN_V0_1 by
  default (no fabrication).
- Source sample rate < 44.1 kHz → OBSERVED note (possible downsampled transfer),
  not a defect claim.

## Confidence gates

- HIGH: multiple independent evidence + synthetic-validated pattern (only
  ED-01 severe cutoff in v0.1).
- MEDIUM: corroborated but with artistic interpretation or measurement limits.
- LOW: single proxy / unstable estimator / missing quiet windows / could be
  arrangement. LOW never authorizes automatic processing; findings at LOW with
  POSSIBLE/LIKELY statuses set `requires_human_review=True`.
