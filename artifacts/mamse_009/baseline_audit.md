# MAMSE-009 — Baseline Audit (A. 输入与事件审计, MAMSE009_INPUT_AND_EVENT_AUDIT)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 2bbc98a — includes MAMSE-001..008)
**Task reference:** MAMSE-009_RobustPCA低秩与稀疏异常分离_v0.1 — 03_CODEX_TASK.md Phase A
**Status:** AUDIT COMPLETE — no canonical file modified

---

## 1. 仓库现状

No robust-PCA / PCP implementation exists in `src/moodify/`. Nearest neighbors: MAMSE-007 (PCA/SVD, signed subspace) and MAMSE-008 (NMF, nonnegative). Canonical event layer: `auditory/events/engine.py` (`run_temporal_hearing`, DOMAINS = integrity/level/spectrum/stereo, events with start_ms/event_type/domain) + `rules.py` (deterministic threshold rules, e.g. `_level_events`, `_hf_dropout`, `_stereo_events`).

## 2. 输入审计

MAMSE-009 的 X = L + S 需要**单一连贯矩阵空间**（一个 feature 族、一个单位体系）：
- **合法**：S1 band-energy ratios（8 列非负 simplex，同 MAMSE-008）；独立计算的 STFT 功率谱（非负）；M/S 功率（非负）。
- **BLOCKED**：mixed-unit ScalePlane 全矩阵（dB + Hz + ratio + correlation，G10）；含 NaN/Inf（v0.1 fail closed，G2）。
- 与 MAMSE-008 相同：mid/side + short_term_lufs 语义冲突字段不进入（G15 规则集延续）。

## 3. 事件层审计（G11）

Canonical events 是确定性规则（阈值运行检测），DOMAINS 固定四域。MAMSE-009 的 `SPARSE_STRUCTURE_CANDIDATE` **不加入** `DOMAINS`（Phase-I freeze 不允许）——它作为独立 experimental evidence 输出，real-case 脚本计算 RPCA candidate 区间与 canonical events 的**时间重叠报告**（并存，不覆盖）。

## 4. 模型语义（G1/G9）

X = L + S 是建模假设非物理真值；L 低秩 ≠ "正常音频"；S 稀疏 ≠ "坏音频"；`dense_residual = X - L - S` 单独保存（G13），不与 S 混淆；candidate 语义固定 `EXPERIMENTAL_UNKNOWN`（G9）。

## 5. 依赖 / 命名空间 / 复用

numpy/scipy only（IALM 每迭代 SVD）。`moodify_experimental/mamse009/`（既有惯例）。复用 MAMSE-008 的 band-ratio 输入管线（real-case 每曲一次 build_representation，不重复变换，G20 长曲资源策略：IALM SVD 每次 O(m·n²)，m=8 时轻量；power-spectrogram 输入留给 9 月）。

## 6. 升级条件（F）

只有 real-case 证明 RPCA 能稳定发现"规则检测未覆盖但可检查"的结构才升级——本次只收集证据（G16 目标），不做升级决定。

## Verdict

Proceed as **EXPERIMENTAL unknown-anomaly evidence operator** in `moodify-core-package/src/moodify_experimental/mamse009/`, numpy/scipy only, config_hash + manifest runtime identity per MAMSE-series standard, IALM-PCP baseline, fail-closed NaN, anonymous candidates, event-overlap reporting in real cases.
