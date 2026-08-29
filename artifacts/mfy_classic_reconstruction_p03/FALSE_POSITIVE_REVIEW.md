# MFY-CR-P03 — False Positive Review

KPI is False Positive Rate (style misread as defect), not detection count.

## Most dangerous scenarios (ranked)

1. **Intentional mono / mono transfer** — the engine can never separate
   "mono by choice" from "mono by fold-down". Mitigation: corr >= 0.999 →
   LIKELY_ARTISTIC_CHARACTER with explicit ambiguity; never POSSIBLE.
2. **Dark / sparse arrangement vs bandwidth loss** — a production without
   high-frequency content must not be diagnosed as a defective transfer.
   Mitigation: presence-band guard (empty presence → LIKELY_ARTISTIC_CHARACTER);
   rolloff corroboration required for POSSIBLE.
3. **Loud hiss that fills the music** — no quiet windows → the engine says
   INSUFFICIENT_EVIDENCE instead of confidently calling noise (observed on the
   -50 dBFS fixture).
4. **Compressed genre aesthetic vs dynamic damage** — no clipping → never
   POSSIBLE; only an OBSERVED note with the genre-aesthetic ambiguity.
5. **Distortion as art vs clipping damage** — clipping without a true-peak
   ceiling is OBSERVED, not POSSIBLE; ambiguity records intentional saturation.

## Guardrails proven by tests

- Negative controls N01-N05 all pass (style never becomes a defect claim).
- `test_unknown_handling`: missing metrics never yield POSSIBLE.
- No finding in the whole suite carries a status that authorizes processing;
  LOW-confidence POSSIBLE/LIKELY findings set `requires_human_review`.

## Known miss (accepted)

- True technical noise in a fully-dense mix (no quiet) is missed by design
  ("宁可漏掉一个可处理问题，也不要误伤一个艺术特征" — 03_VALIDATION_MATRIX §4).
