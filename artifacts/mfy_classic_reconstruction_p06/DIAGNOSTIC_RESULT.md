# MFY-CR-P06 — Diagnostic Result (Stage 1)

Era Diagnostic v0.1 on the golden source (real measurement chain).

| Category | Status | Confidence | Evidence | Ambiguity |
|---|---|---|---|---|
| ED-01 Bandwidth | POSSIBLE_TECHNICAL_LIMITATION | LOW | cutoff ~14.1 kHz corroborated by rolloff-95 ~9.3 kHz | could be arrangement-dependent (dark production) |
| ED-02 Noise | INSUFFICIENT_EVIDENCE | LOW | floor ~-29 dBFS but no reliable quiet windows | noise vs music texture unresolvable |
| ED-03 Dynamic | NOT_APPLICABLE | - | no clipping, normal dynamics | - |
| ED-04 Stereo/Phase | NOT_APPLICABLE | - | correlation 0.71, no phase anomaly | - |
| ED-05 Congestion | NOT_APPLICABLE | - | no congestion signal | - |
| ED-06 Transfer | NOT_SUPPORTED_IN_V0_1 | - | no validated detector | - |

## Objective consumption (P03 gate)

- Only ED-01 enters the objective (as a LOW-confidence bounded candidate set —
  an explicit golden experiment, not automatic production).
- ED-02 (INSUFFICIENT) is NOT consumed — per the uncertainty principle the
  engine refuses to guess noise on this source.
- SOURCE stays eligible throughout.
