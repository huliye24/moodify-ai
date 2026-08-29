# MAMSE-010 — Baseline Audit (Phase 0, MAMSE010_TENSOR_INPUT_AUDIT)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 540b454 — includes MAMSE-001..009)
**Task reference:** MAMSE-010_听觉张量表示_v0.1 — 03_CODEX_TASK.md 必须先做的仓库审计
**Status:** AUDIT COMPLETE — no canonical file modified

---

## 1. 仓库现状

Canonical representation: `AuditoryRepresentation`（`representation/models.py`）+ `build_representation`（`build.py`，S0/S1/S2 planes）+ `ScalePlane`（values [windows × features], NaN = unavailable, window_starts_ms/ends_ms）。**不存在** `alignment.py` / `serialize.py`（representation 层无独立对齐模块）；feature bus（`execution/feature_bus.py`）是 caller-keyed registry。MAMSE-001..009 均在 `moodify_experimental/mamseNNN/`（既有惯例）。

## 2. 绝对禁止项对照

1. **不直接 np.stack S0/S1/S2 values** — `build_scale_feature_tensor` 用 interval-overlap-weighted 对齐（真实时间区间），不同 scale 不同 feature 集 → 缺失保持 NaN + mask=False。
2. **不用 array index 代替时间对齐** — 对齐只基于 `window_starts_ms/ends_ms` 区间重叠。
3. **不用 0 填充 unavailable** — valid_mask 显式，NaN 保留（G4）。
4. **不对 mixed-unit feature axis 做 HOSVD** — HOSVD 只作用于 homogeneous view（TIME×FREQ×CHANNEL 功率张量）；scale_feature view 是记录/呈现用，不进 multilinear。
5. **不重复执行完整 STFT** — channel spectral view 复用 MAMSE-006 surface 管线逻辑（同一 STFT 一次执行）；real-case 脚本每曲一次变换。
6. **research tensor 不改写 canonical authority** — `AuditoryRepresentation` 原样保留（G20）。

## 3. 语义冲突放大防护（G21）

S1 mid/side（线性 vs ratio）与 S2 short_term_lufs（RMS proxy vs LUFS）冲突**不进入** tensor 层的高阶分析：scale_feature view 保留全部列（记录用），但 multilinear 研究只用无冲突的 homogeneous 功率张量；冲突列不在 evidence 里被解释。与 MAMSE-007/008 同一规则集。

## 4. 资源安全（G16/G17/G19）

- `estimate_dense_bytes`（shape×dtype）；
- `iter_tiles` 完整无覆盖；
- `guard_materialization(shape, dtype, max_bytes)` 超限 raise（默认禁止巨大 5D 实例化）；
- channel spectral view 用降采样帧（MAMSE-009 功率谱探针同款）控制规模。

## 5. 依赖 / 命名空间

numpy only（scipy 测试用）。`moodify_experimental/mamse010/`。tensor_id 稳定（schema/source/fields meta hash）。

## 6. 升级条件

真实 case 证明 multiway 增量价值 + 资源安全 + schema 稳定 + reopen/determinism 稳定——本次收集证据，不做升级决定。

## Verdict

Proceed as **EXPERIMENTAL tensor view layer** in `moodify-core-package/src/moodify_experimental/mamse010/`（contracts/views/multilinear/resources/evidence），numpy only，manifest runtime identity per MAMSE-series standard，两个 view（scale_feature + channel spectral），HOSVD 只作用于 homogeneous 张量，materialization guard 默认开启。
