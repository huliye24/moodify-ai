# MFY-CR-P06 — Identity Guard Results (Stage 4/5)

Identity Guard v0.1 on A/B/C vs SOURCE (six dimensions, veto semantics).

| Candidate | IG-01 Vocal/Mid | IG-02 Dynamics | IG-03 Reverb | IG-04 Stereo | IG-05 Low-end | IG-06 Loudness | Overall |
|---|---|---|---|---|---|---|---|
| A | PASS | PASS | NOT_MEASURABLE | PASS | PASS | PASS | **PASS** |
| B | PASS | PASS | NOT_MEASURABLE | PASS | PASS | PASS | **PASS** |
| C | PASS | PASS | NOT_MEASURABLE | PASS | PASS | PASS | **PASS** |

No REJECT, no HUMAN_REQUIRED. (IG-03 is always NOT_MEASURABLE in v0.1; the
overall rule "unmeasured critical + any change -> HUMAN_REQUIRED" does not
trigger because every measured dimension is PASS.)

## Technical ranking (Stage 5)

```text
1. C (PASS, auto-approvable)  — upper safe boundary
2. B (PASS, auto-approvable)
3. A (PASS, auto-approvable)
4. SOURCE (PASS, always eligible)
TECHNICAL_TOP = C
```

The ranking answers only "which candidate performs best under the current
objective" — it does NOT claim artistic superiority. SOURCE remains a legal
result throughout.

## Why candidates stayed PASS

- LUFS delta <= 0.93 (IG-06 budget 3.0, caution 1.5) — C is technically at
  caution level 0.62/1.5 but still under budget; guard reports PASS.
- LRA/crest deltas within budget (compressor bypassed — the earlier REJECTs
  came from the chain's always-on compressor and were correctly caught).
- Centroid +253 Hz < 300 Hz proxy budget (C is at the edge of the proxy budget).
- No new clipping; stereo correlation delta <= 0.011.
