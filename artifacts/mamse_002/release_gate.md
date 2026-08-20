# MAMSE-002 — Release Gate (T12)

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — conditional operator, off by default, R3 Case Proven. Not canonical; R6 requires a separate RFC.

## Gate evaluation (blockers listed in T12)

| Blocker criterion | Status | Evidence |
|---|---|---|
| No proven increment over STFT/MR-STFT | **No failure.** Case A (1-semitone low pair) resolved at 55/58.27 Hz where 93.75 Hz linear bins cannot; real cases show dense low-register tonal grid + near-zero tuning lock | `linear_vs_log_increment.md`, `real_case_results.md` |
| Resource cost unacceptable on target node | **No failure.** Full 188.5 s track: 18.4 s wall, peak RSS 575 MB (36% of 1.6 GB; below 1500M MemoryHigh), swap delta 0. One-time JIT ~17 s. Conditional invocation keeps it off the default path | `benchmark.json`, `payload_size_report.md` |
| Creates new canonical frequency-band authority | **No failure.** BANDS untouched; geometry is versioned/hashable and off by default | `geometry_contract.md`, baseline audit Q3–Q5 |
| dominant_midi/chroma misused as artistic/harmony authority | **No failure.** All such features carry `FEATURE_AUTHORITY` markers ("ESTIMATOR — not perceived pitch" etc.); interpretation policy in evidence JSON | `sketch.py`, `log_frequency_evidence.json` |
| Geometry version missing from cache/evidence key | **No failure.** geometry_id + config_sha256 in every manifest, NPZ, and caller-supplied cache key policy | `geometry_contract.md` §Hash & cache lineage |
| Real cases yield only "prettier plots" | **No failure.** Case C honestly reports NO mean-level increment on its fixture (only frame-level wobble) — negative result preserved; positive increments documented per case | `linear_vs_log_increment.md` Case C |
| Breaks Phase I freeze / release convergence | **No failure.** Full suite 353 passed / 5 skipped (341 baseline + 12 new); ruff clean; canonical files unmodified | `test_results.md` |

## Conditional invocation (T7)

`need_log_frequency(case_context, prior_metrics)` returns a policy suggestion only. v0.1 triggers: explicit research/MSE-bridge flag, manual research flag, persistent narrowband cluster, low-band activity > 0.25. Never an automatic default-scan component.

## Honest negatives

- Case C (weak note-locked narrowband) shows no mean-spectrum increment — logged as PARTIAL, not glossed over.
- 24 bpo is a research baseline, not the final optimal parameter set.
- Near-zero tuning deviation in all three AI tracks is a descriptive observation, not an AI-detection claim.

## Maturity

```text
R0 Theory        ✅ task docs
R1 Operator      ✅ experimental implementation runs (librosa.cqt 0.11.0 locked)
R2 Verified      ✅ 12/12 tests (10 required + 2 extra)
R3 Case Proven   ✅ 3 real cases with documented increments + honest negatives
R4+              ⏸ deferred to data phase / separate decision
```

## Outstanding (non-blocking)

1. Frame-level analysis (per-frame dominant switching) for weak narrowband anomalies needs a fixture-based study before claiming value.
2. One-time JIT cost (~17 s) should be absorbed by a warm-start or documented per-deployment.
3. Cache integration with `execution/cache.py` deferred (MAMSE-001 same decision); geometry identity policy is defined and ready.
4. Chroma/octave fold analysis on real cases deferred to September data phase.
