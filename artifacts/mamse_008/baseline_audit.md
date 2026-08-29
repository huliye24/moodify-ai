# MAMSE-008 — Baseline Audit (Phase A, includes MAMSE008_INPUT_AUDIT)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 6ce2635 — includes MAMSE-001..007)
**Task reference:** MAMSE-008_NMF与听觉成分结构_v0.1 — 03_CODEX_TASK.md Phase A
**Status:** AUDIT COMPLETE — no canonical file modified

---

## 1. 仓库现状

No NMF/factorization implementation exists in `src/moodify/`. MAMSE-007 (PCA/SVD) is the closest neighbor (linear subspace, signed). The canonical representation layer provides `ScalePlane` (S0/S1/S2) with `values` = [windows × features], `NaN = unavailable`.

## 2. 输入语义审计（Phase A 核心）

### 可合法进入 NMF 的 linear nonnegative surfaces

| Surface | Source | Semantics | NMF 资格 |
|---|---|---|---|
| linear power spectrogram (STFT) | 自有分析路径（MAMSE-001..006 惯例） | physical energy ≥ 0 | **OK** |
| CQT power (MAMSE-002) | experimental | energy ≥ 0 | **OK**（需 nonnegative 预处理） |
| S1 band-energy ratios | canonical S1 plane (`band_*`) | 非负、和为 1（simplex 约束） | **OK with caveat**（compositional，记录约束） |
| S1 mid/side energy | canonical S1 | 线性非负 BUT registry 语义是 ratio | **BLOCKED**（SEMANTIC_CONFLICT，同 MAMSE-007 G11） |
| S2 short_term_lufs | canonical S2 | RMS dB proxy vs LUFS | **BLOCKED**（SEMANTIC_CONFLICT） |
| rms_db / peak_db / crest_db | canonical planes | dB（负值） | **REJECTED by signed check**（非物理线性坐标） |
| spectral_centroid_hz | canonical | Hz（正但非能量） | **REJECTED**（单位语义不匹配 NMF 的加法重构） |
| stereo_correlation | canonical | [-1,1] signed | **REJECTED by signed check** |

### 决策

- v0.1 real-case 输入 = **S1 band-energy ratios**（8 列，非负 simplex，skip mid/side/rms/peak/centroid/corr 等）**或独立计算的 STFT 线性功率谱**；
- 混合单位/负值矩阵由 `_validate_matrix` 的 signed check 拒绝（G1/G14）；
- S1 mid/side + S2 short_term_lufs 按 MAMSE-007 相同规则 fail closed（G15）。

## 3. cache / transform 复用（G16）

`execution/cache.py` 是 caller-keyed `(source_sha256, key)`；MAMSE-001..007 均各自携带分析路径（已记录先例）。MAMSE-008 v0.1 复用 MAMSE-006 的 log-frequency surface 惯例（同一 STFT 管线模式）但独立执行；正式 feature-bus 复用列为 R4+。real-case 脚本只对每首曲跑一次 STFT（不重复全曲变换）。

## 4. 依赖

numpy/scipy only（`linear_sum_assignment` 仅测试用，scipy 已是 canonical pin）。**无新依赖**。

## 5. 命名空间

`moodify_experimental/mamse008/`（既有惯例；CODEX 建议的 `auditory/research/factorization/` 非现存路径，以现有宪法为准）。

## 6. 语义边界（README 六条）

component ≠ stem；dB/LUFS/混合单位矩阵禁止直进；缺失不补 0；rank ≠ 声源数；残差是 out-of-subspace candidate；canonical 门禁前不升级。全部由 operator limitations + 测试覆盖。

## Verdict

Proceed as **EXPERIMENTAL NMF operator** in `moodify-core-package/src/moodify_experimental/mamse008/`, numpy/scipy only, config_hash + manifest runtime identity per MAMSE-series standard, input audit in this document, real-case input = band-energy ratios (semantic-clean subset), beta ∈ {2,1,0}, NNDSVD deterministic init, scale/permutation canonicalization, stable basis_id.
