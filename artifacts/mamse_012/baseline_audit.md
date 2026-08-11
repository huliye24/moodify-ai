# MAMSE-012 — Baseline Audit (Phase A)

**Date:** 2026-08-11
**Branch:** codex/mfy-data-factory-001 (head 7369316 — includes MAMSE-001..011)
**Task reference:** MAMSE-012_听觉图信号处理与结构拓扑_v0.1 — 03_CODEX_TASK.md Phase A
**Status:** AUDIT COMPLETE — no canonical file modified

---

## 1. 仓库现状

No graph-signal-processing implementation exists in `src/moodify/`. Relevant neighbors: MAMSE-011 (covariance model → positive correlation matrix 可直接成图)、MAMSE-010 (tensor views)、canonical events engine（`run_temporal_hearing` → TemporalEvent 带 start_ms/end_ms/event_type/domain，可建事件图）、representation BANDS（8 canonical bands，可建 band path graph）。

## 2. 三张图的输入

| 图 | 输入 | 语义 | 权威 |
|---|---|---|---|
| Canonical Band Graph | BANDS 8 band path（有序邻接，单位权重） | ordered acoustic-band adjacency | DETERMINISTIC_TOPOLOGY（非 psychoacoustic similarity，G19） |
| Temporal Event Graph | TemporalEvent 序列（时间重叠/距离，exp(-gap/tau) 权重） | time-interval proximity | DETERMINISTIC_DERIVED（保留原事件语义，G20） |
| Positive Correlation Graph | MAMSE-011 correlation 矩阵（只取 ≥ threshold 正相关） | positive empirical correlation | DATA_DERIVED（负相关不 abs()，G22） |

## 3. 边界

- graph frequency = topology frequency ≠ acoustic Hz（G18，进 evidence semantic boundaries）
- undirected + nonnegative + homogeneous edge（v0.1 契约，G3/G4/G5）
- 事件图不创造 forbidden musical label（G21）
- dense eigendecomposition guard（max_dense_nodes=512，G25）；大图 partial sparse（eigsh，G26）
- 语义冲突 fail closed（G29）：positive correlation graph 输入来自 MAMSE-011 的 S1 clean subset（mid/side + short_term_lufs 已排除）

## 4. 命名空间 / 依赖

`moodify_experimental/mamse012/`（既有惯例）。numpy/scipy（sparse/eigsh 是 scipy 内建，node lock 已有 scipy 1.18.0）。无新依赖。每 case 一次 build_representation（G28）。

## 5. 升级门槛

scientific topology + deterministic graph_id + explicit authority + resource safety + real-case incremental value + no canonical regression——本次收集证据。

## Verdict

Proceed as **EXPERIMENTAL graph-signal layer** in `moodify-core-package/src/moodify_experimental/mamse012/`，numpy/scipy only，config 无独立参数（图本身是版本化模型）→ manifest runtime identity + graph_id per MAMSE-series standard，三张图 + GSP 算子族，dense guard + sparse path，real cases 验证结构证据增量。
