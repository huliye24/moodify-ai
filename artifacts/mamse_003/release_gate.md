# MAMSE-003 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — scattering-inspired texture operator, off by default, R3 Case Proven within a documented resource scope. Not canonical; R4+ (full scattering equivalence, canonical integration) requires a separate RFC.

## Scope discipline

The task package README scopes v0.1 to R0-R2 (theory → operator → verified synthetic). The 3 real cases completed in this package satisfy acceptance Gate F and allow the R2→R3 upgrade; R3 here means "case-proven for the questions listed below", never "canonical texture authority".

## Gate evaluation (acceptance Gates A–G)

| Gate | Status | Evidence |
|---|---|---|
| A. Theory/semantics | **Pass.** Wavelet vs CQT vs STFT vs scattering distinguished in docs; prototype explicitly `scattering-inspired` in README/config/limitations; no "模拟人耳"/auto-quality claims; every descriptor documented with unit/definition/limitation (sketch.py, real_case_results.md) | `00_README.md`, `config.py`, `sketch.py` |
| B. Engineering boundary | **Pass.** No canonical file modified (baseline audit Q5); no second ProductionCase state; source identity/sample clock reused (Q7); disabled by default — no App entry, no UI switch; dense wavelet cube never persisted (NPZ holds fixed-width sketches only) | `baseline_audit.md`, `evidence.py` |
| C. Synthetic validation | **Pass.** 10/10 tests cover all 9 required fixtures + two-state switch | `test_results.md` |
| D. Evidence | **Pass.** JSON manifest readable; NPZ reusable; config_hash + source_sha256 + git_commit in every manifest; runtime/memory recorded; missing values not faked as 0 (Windows RSS/swap recorded as null/NaN, not 0) | `evidence.py`, `real_cases/*/mamse003_manifest.json` |
| E. Resource | **Local benchmark complete** (10/30/45 s, first-order vs first+second-order). 2C2G/target-node measurement deferred to formal integration per acceptance doc. Artifact sizes recorded in `real_case_results.md` | `benchmark_local.json` |
| F. R3 real cases | **Pass (3 cases + A/B pair).** AI fine-texture case, sustained internal-modulation case, and A/B matched-loudness pair (LUFS Δ0.01) with a small-but-real texture delta (cos 0.9884 vs same-song control 0.9995) + control pair proving no fabricated difference. Increment/cost answered per case — including honest negatives | `real_case_results.md` |

## Resource evidence and node policy

Local benchmark (48 kHz source → 24 kHz analysis, 27 carriers, 5 modulation rates):

| Slice | First-order wall / mem | First+second-order wall / mem |
|---|---|---|
| 10 s | 3.2 s / 200 MB | 3.2 s / 200 MB |
| 30 s | 8.5 s / 599 MB | 7.3 s / 599 MB |
| 45 s | 10.1 s / 898 MB | 6.1 s / 898 MB |

Full-track runs (128–198 s) peak at **2.5–3.9 GB tracemalloc** — the whole signal is FFT-processed at once, so peak scales linearly with duration. The 2C2G target node (MemoryHigh 1500M) cannot host full-song runs; per CODEX this must NOT be papered over by upgrading the node.

**v0.1 node policy (documented, not worked around):**
- Full-song texture analysis = **offline/high-ACU operator only**; never on the default node queue.
- On-node slices are limited to ≤45 s under the resource guard, with automatic defer if memory pressure is observed (data_node guard precedent).
- R4+ optimization path (in order): chunk + deterministic aggregation (bounded peak memory), envelope decimation already applied, carrier-band reduction for narrow use cases. Kymatio/PyWavelets equivalence evaluation only after a value case is demonstrated.

## Conditional invocation

MAMSE-003 is disabled by default. v0.1 entry points: `--experimental-texture` style research flag, the dedicated scripts, or a texture-specific research batch. No automatic trigger exists; an evidence-based RFC is required before any auto-trigger.

## Honest negatives

1. Full-song runs exceed the target node budget → v0.1 restricts them to offline; the node policy is a scope decision, not a "runs anywhere" claim.
2. The prototype is NOT numerically equivalent to Kymatio/Mallat scattering — every artifact carries this limitation; second-order "modulation summary" is a 5-rate sketch, not a full scattering path.
3. A/B pair: if the pair shows near-identical linear metrics but different texture, that is a *descriptive* delta — no artistic quality judgment.
4. Windows-local benchmark cannot measure RSS/swap; those cells are recorded as null/NaN (not faked as 0) and must be completed at formal integration on the target node.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ experimental implementation runs (numpy/scipy only, no new dep)
R2 Verified      ✅ 10/10 synthetic tests, ruff clean
R3 Case Proven   ✅ 3 real cases + A/B pair with increments + honest negatives
R4+              ⏸ deferred: full scattering equivalence, chunked aggregation, node measurement, canonical RFC
```

## Outstanding (non-blocking)

1. 2C2G/target-node measurement (30s/45s, swap behavior) at formal integration.
2. Chunk + deterministic aggregation to bound full-song peak memory (R4+ optimization; enables on-node full songs).
3. Frame-level (per-frame dominant switching) texture analysis needs a fixture-based study before claiming value for short anomalies.
4. Kymatio/PyWavelets equivalence assessment if a value case motivates it.
