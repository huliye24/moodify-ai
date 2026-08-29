# MFY-CR-P06 — Reconstruction Plans (Stage 2, P04-absorbed)

Objective layer: `moodify.reconstruction.objective`
(`reconstruction-objective-policy-v1`, PROVISIONAL budgets).

| Candidate | Label | Params (MoodifyDSPChain) | Objective refs | Plan hash |
|---|---|---|---|---|
| SOURCE | SOURCE | — | — | source |
| A | A = Minimal | comp ratio 1.0 (bypass), reverb 0.0, high shelf +0.5 dB @ 10 kHz | ED-01 bandwidth (LOW, bounded) | deterministic |
| B | B = Balanced | comp bypass, reverb 0.0, high shelf +1.5 dB @ 10 kHz, vocal presence +0.8 dB @ 3 kHz | ED-01 + vocal presence (proxy) | deterministic |
| C | C = Upper Safe Boundary | comp bypass, reverb 0.0, high shelf +3.0 dB @ 10 kHz, presence +1.5 dB @ 3.2 kHz, low shelf +1.0 dB @ 200 Hz | ED-01 + presence + low-end warmth | deterministic |

## Documented decisions (not silent tuning)

1. **Compressor bypassed** (ratio 1.0): the shared chain's always-on compressor
   flattened LRA 12.7 -> 8.0 LU and the identity guard REJECTed it. Dynamics
   preservation outranks the chain default for era reconstruction.
2. **Reverb disabled** (P11=0): the chain's default 20 % wet reverb added
   +4.2 LU; P06 has no space objective and reverb change risks era-texture
   damage (IG-03 is NOT_MEASURABLE).
3. **ED-02 (noise) excluded**: INSUFFICIENT_EVIDENCE findings never produce
   objectives (uncertainty reduces intervention).
4. **ED-06 excluded**: no validated detector, no fabrication.

Unsupported objectives: noise reduction, stereo widening, loudness push,
transfer repair — all BYPASS in P06.
