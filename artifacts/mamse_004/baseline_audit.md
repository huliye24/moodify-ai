# MAMSE-004 — Baseline Audit (T1)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 5e6de72 — includes MAMSE-001/002/003)
**Task reference:** MAMSE-004_相位几何与群延迟_v0.1 — 03_CODEX_TASK.md 强制约束
**Status:** AUDIT COMPLETE — no canonical file modified

---

## Q1. 仓库现有 stereo / phase 实现

**Two existing pieces, neither is group-delay geometry:**

1. `moodify/auditory/stereo.py::compute_stereo_metrics` — canonical quick metrics: stereo_correlation (Pearson), mid/side energy, negative_correlation_ratio (frame-wise c < -0.7), and **`phase_risk_ratio`** = fraction of 4096-sample frames where side energy > 3× mid energy. All frame-wise, time-domain, low-cost proxies. MAMSE-004 does NOT touch or replace any of these.
2. `moodify/phase.py` — contains only `phase2_experiments_enabled()` (a feature flag), no phase mathematics.

No group-delay / phase-derivative / IPD implementation exists anywhere in `src/moodify/`. MAMSE-004 is the first phase-geometry operator.

## Q2. lab namespace 政策

`moodify/auditory/lab/` exists and holds the Phase-I controlled-lab tooling (`calibration.py`, `perturbations.py`, `runner.py`, `evaluate.py`, `ground_truth.py`, `sources.py`, `models.py`) — canonical deliverables of the 受控实验室 package (补丁包24). It is not a research-operator namespace.

The established research-operator convention in this repo is `moodify_experimental/mamseNNN/` (MAMSE-001 bfbfa6a, MAMSE-002 2eb01b0, MAMSE-003 5e6de72). Per the CODEX clause "若现有 lab 目录政策不允许，则放到明确标记 experimental 的 research namespace", MAMSE-004 follows the same convention: `moodify_experimental/mamse004/`.

## Q3. 依赖

`numpy==2.4.4` and `scipy==1.17.1` are canonical pins (pyproject + node lock). MAMSE-004 needs only `scipy.signal.stft` + numpy. **No new dependency.** The CODEX prohibition on heavy NN deps is trivially satisfied (nothing added).

## Q4. phase_risk_ratio semantics 保持不变

`phase_risk_ratio` (stereo.py:68) keeps its exact definition and authority. MAMSE-004 outputs carry `authority_class = EXPERIMENTAL_DESCRIPTOR_ESTIMATOR` and `judgment_eligible = False`; nonzero group delay is never a FAIL. No canonical metric name is reused.

## Q5. 参数版本化与 hash

The task package prototype's `PhaseGeometryConfig` has `to_dict()` but **no config hash**. Per the MAMSE-001/002/003 evidence standard (geometry/operator identity in every manifest and cache key), the repo implementation adds `config_hash` (sha256 of canonical JSON) to the config and records it in every manifest.

## Q6. 确定性

All operations are pure numpy/scipy (STFT, unwrap, gradient, FFT-based GCC-PHAT): same input + same config → identical numerics. No RNG in the operator path (GCC-PHAT uses no randomness). Determinism gate holds.

## Q7. Phase I freeze 允许默认关闭实验算子

Same precedent as MAMSE-001/002/003 (accepted under the freeze Yellow budget as conditional experimental operators, `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`). MAMSE-004 is disabled by default; no App entry point, no UI switch, no canonical-scan integration. Evidence under `artifacts/mamse_004/`.

## Verdict

Proceed as an **EXPERIMENTAL phase-geometry operator** in `moodify-core-package/src/moodify_experimental/mamse004/`, evidence under `artifacts/mamse_004/`, numpy/scipy only, config_hash in every artifact, mono/stereo semantics following the task package prototype with the MAMSE-series evidence contract (manifest runtime identity, honest UNAVAILABLE, limitations).
