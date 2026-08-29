# Phase I-F Release Gate

| Gate | Verdict | Evidence |
|---|---|---|
| G1 Scope | PASS | CPU/local execution only |
| G2 Single decode | PASS | cold=1, warm=0 |
| G3 Shared transforms | PASS | S3 reuses global metrics; differing spectral window profiles remain separate |
| G4 Cache identity | PASS | content + semantic versions + dependencies |
| G5 Invalidation | PASS | tests cover source/version/rule dependency behavior |
| G6 Corruption safety | PASS | hash mismatch isolates and recomputes |
| G7 Cold/warm equivalence | PASS | logical report equal |
| G8 Chunk equivalence | PASS | exact peak/RMS across chunk sizes |
| G9 Resume equivalence | PASS | checkpoint resume equals fresh run |
| G10 Bounded memory | PASS | 30 s / 3 min / 10 min observed RSS 117/176/320 MB |
| G11 Linear runtime | PASS | 6.787/20.453/84.426 s; no pathological growth |
| G12 Warm acceleration | PASS | six persistent hits, zero decode |
| G13 Rule-only precision | PASS | decode/features reused; judgment recomputed |
| G14 Observability | PASS | required counters exposed |
| G15 Privacy | PASS | local only; no portable absolute path |
| G16 Regression | PASS | 275 passed, 5 skipped |
| G17 Evidence | PASS | required artifact set present |

Overall verdict: **PASS**. No stale-cache or resume semantic mismatch was found.

`MFY-PHASE1-DEPTH-006 VERIFICATION: PASS`
