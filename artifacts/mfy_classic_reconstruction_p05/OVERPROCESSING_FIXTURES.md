# MFY-CR-P05 — Overprocessing Fixtures

Controlled bad candidates generated at test time (deterministic, seeded) to
prove the Guard rejects obvious overprocessing. All derived from the same
clean synthetic source (tones 60 Hz-19 kHz + noise bed + silence gaps, stereo
corr ~0.97).

| Fixture | Perturbation | Guard verdict |
|---|---|---|
| over_bright | 3 kHz high shelf +0.45 | HUMAN_REQUIRED (IG-01 proxy drift) |
| over_bass | 150 Hz low shelf +0.9 | REJECT (IG-05 low-end inflation) |
| over_compressed | 1.4*tanh(2.5x) | REJECT (IG-02 flattening + new clipping) |
| over_wide | side x2.5 | REJECT (IG-04 width beyond boundary) |
| over_loud | 2.0*tanh(x) | REJECT (IG-06 loudness jump + new clipping) |
| minimal | +0.5 dB gain | PASS (not killed) |
| balanced | +1 dB + mild 8 kHz shelf | PASS (within budgets) |
| source vs source | none | PASS |

## Key results

- 5/5 deliberate overprocessing fixtures produce REJECT or HUMAN_REQUIRED.
- Minimal and balanced candidates are not systematically killed (false
  positive guard).
- SOURCE-vs-SOURCE always PASS — the guard is deterministic and self-consistent.
- Note: over_compressed/over_loud also trip the new-clipping hard guard — the
  guard rejects for multiple independent reasons, which is correct.
