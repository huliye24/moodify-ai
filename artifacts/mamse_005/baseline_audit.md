# MAMSE-005 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 8e291b2 — includes MAMSE-001..004)
**Task reference:** MAMSE-005_倒谱与声源滤波结构_v0.1 — 03_CODEX_TASK.md 强制约束
**Status:** AUDIT COMPLETE — no canonical file modified

---

## Q1. 仓库现有 cepstrum / quefrency / lifter 实现

**None.** Grep over `src/moodify/` for `cepstrum|quefrency|lifter` returns nothing. The canonical representation path is STFT-based (linear-Hz scales, `representation/build.py`) + MAMSE-001 (MR-STFT) + MAMSE-002 (CQT, librosa) + MAMSE-003 (wavelet texture) + MAMSE-004 (phase geometry). No homomorphic/cepstral layer exists anywhere.

## Q2. 现有 F0 / pitch 实现

**None in canonical metrics.** `measurement_registry_v1.yaml` contains no f0/pitch/cepstrum entries. The `f0`/`pitch` grep hits in `representation/models.py`, `data_factory/*` and `physics/experiments_2.py` are non-semantic (no actual pitch estimator exists). MAMSE-002's `dominant_midi` is a CQT-based descriptor (ESTIMATOR, not perceived pitch) — the nearest neighbor, but it estimates a dominant grid note, not cepstral periodicity. MAMSE-005's `f0_candidate` is a new descriptor family.

## Q3. 依赖

`numpy==2.4.4`, `scipy==1.17.1` are canonical pins; the operator needs only numpy/scipy (`find_peaks`, `iirpeak` in tests only). **No new dependency.** No NN requirement.

## Q4. 命名空间与宪法

Same convention as MAMSE-001..004: `moodify_experimental/mamse005/` (research namespace per `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`; the CODEX's suggested `moodify/auditory/research/cepstrum/` is not a pre-existing path — the experimental namespace is the established convention, "以现有宪法为准，不建立竞争路径"). Evidence under `artifacts/mamse_005/`.

## Q5. Canonical 边界

No canonical metric definition/unit/threshold/schema is touched. `f0_candidate` is labeled ESTIMATOR (not ground-truth pitch); `resonance_candidates` are envelope peaks (not formants); silence/short inputs return UNAVAILABLE; config is versioned with config_hash in every manifest (per MAMSE-001..004 evidence standard — the prototype lacks a hash, the repo implementation adds it).

## Q6. 默认关闭 / 调用路径

Disabled by default. No App entry, no "naturalness score" exposed. Deep-scan/diagnostic paths only (research flag or dedicated scripts). Future conflict-detection against CQT/MSE pitch is a stated integration point, not built here.

## Verdict

Proceed as an **EXPERIMENTAL cepstral structure operator** in `moodify-core-package/src/moodify_experimental/mamse005/`, evidence under `artifacts/mamse_005/`, numpy/scipy only, config_hash in every artifact, UNAVAILABLE semantics, and fixed-width NPZ sketches (dense per-frame arrays decimated per the MAMSE-004 payload lesson).
