# MAMSE-011 — Baseline Audit (Phase A, MAMSE011_FEATURE_GEOMETRY_AUDIT)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 6416cc5 — includes MAMSE-001..010)
**Task reference:** MAMSE-011_协方差与听觉本征空间_v0.1 — 03_CODEX_TASK.md Phase A
**Status:** AUDIT COMPLETE — no canonical file modified

---

## 1. 可进入同一 standardized covariance model 的 feature

Canonical S1 plane（`build.py` `_short_rows`）语义清洁子集（12 列）：
`rms_db, peak_db, stereo_correlation, spectral_centroid_hz, band_sub..band_air (8)`。

- 单位/权威：rms/peak = dB（ESTIMATOR）；centroid = Hz（ESTIMATOR）；corr = ratio（PEARSON）；bands = ratio（derived, simplex 约束）。
- **scaling contract 前置**（G5）：median/MAD robust scaling + winsor_z=8（signed 值如 correlation 允许，单位差异由 scaling 消除——与 MAMSE-007 的 robust scaling 同规则）。
- **BLOCKED**（G26，同 007/008/009 规则集）：`mid_energy`/`side_energy`（线性 vs ratio 冲突）、`short_term_lufs`（RMS proxy vs LUFS）。S2 的其余列（crest/hf_ratio/hf_cutoff）单元混杂且与 S1 时间尺度不同 → 本包只用 S1 单尺度矩阵，不做跨尺度合并。

## 2. 缺失策略（G3/G4）

complete-row gate（非 pairwise deletion——pairwise 可产生非 PSD，README 边界 6）；missing_fraction > 0.35 fail closed；complete rows < 4 fail closed。NaN 永不补 0。

## 3. 时间依赖（D/E）

lag1 autocorrelation + AR(1) effective sample size per feature 必须记录（G19/G20）；窗口数不等于 IID n。

## 4. 与 MAMSE-007/010 的边界

- 007：低维状态坐标（scores）；011：协方差矩阵本身作为版本化"听觉关系模型"（drift/whitening/Mahalanobis）。
- 010：张量 view 层；011 在单尺度矩阵上建立统计几何。无冲突，各自独立 evidence。

## 5. 命名空间 / 依赖

`moodify_experimental/mamse011/`（既有惯例）。numpy only（scipy 测试用）。复用 MAMSE-007 的 S1 语义清洁列选择（同一 audit 规则集）。

## 6. 科学边界（README 六条）

covariance ≠ causality；窗口非 IID（neff 记录）；Mahalanobis ≠ 坏音质分数；近重根比较 subspace（principal angles/projector）；mixed-unit 先 scaling；complete-row gate。

## Verdict

Proceed as **EXPERIMENTAL covariance/eigenspace operator** in `moodify-core-package/src/moodify_experimental/mamse011/`，numpy only，config_hash + manifest runtime identity per MAMSE-series standard，S1 清洁子集输入，OAS/fixed/empirical 三种估计器，deterministic sign，eigengap warning，frozen 投影 + Mahalanobis 轨迹 + covariance drift，real cases 验证"组合关系异常增量"（G29）。
