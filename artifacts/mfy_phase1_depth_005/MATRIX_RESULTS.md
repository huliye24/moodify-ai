# Matrix Results — MFY-PHASE1-DEPTH-005

日期：2026-08-09（确定性合成源，CPU/离线）

## 完整本地矩阵（9 算子 × 1 强度）

| 源 | 算子 | TP | FP | Recall | IoU | Delta 方向 | 失败分类 |
|---|---|---|---|---|---|---|---|
| C1 | HARD_CLIP | 1 | 3 | 1.0 | 0.86 | ✓ | — |
| C1 | NEAR_CLIP | 1 | 2 | 1.0 | 0.86 | ✓ | — |
| C1 | DC_OFFSET | 0 | 0 | n/a | n/a | ✓ | — |
| C3 | GAIN_STEP | 1 | 2 | 1.0 | 0.11 | ✓ | TEMPORAL_FAILURE |
| C1 | SILENCE_INSERT | 1 | 2 | 1.0 | 1.00 | ✓ | — |
| C3 | LOWPASS | 1 | 0 | 1.0 | 0.67 | ✓ | — |
| C2 | ANTIPHASE_REGION | 1 | 4 | 1.0 | 0.83 | ✓ | — |
| C3 | NOISE_INJECTION | 0 | 0 | n/a | n/a | ✓ | — |
| C1 | DYNAMIC_COMPRESSION | 0 | 0 | n/a | n/a | ✓ | — |

**聚合**：TP 6 / FP 13 / TN 3 / FN 0 / Recall 1.0 / Precision 0.32

## 校准建议（证据记录，不自动改规则）

| 算子 | 建议 | 证据 |
|---|---|---|
| DC_OFFSET / LOWPASS / NOISE_INJECTION / DYNAMIC_COMPRESSION | KEEP | 0 漏检/0 delta 失败/0 fp |
| HARD_CLIP / NEAR_CLIP / SILENCE_INSERT / ANTIPHASE_REGION / GAIN_STEP | REVIEW_DETECTOR | fp 2-4/实验（预增益削波引发关联事件 + spike/drop 边界误报） |

## 失败分析

- **GAIN_STEP TEMPORAL_FAILURE**：LEVEL_SPIKE 检测器把持续 12dB 阶跃定位为短尖峰（start 误差 ~300ms = 一个 400ms 窗 + 过渡窗）。spike 语义=短尖峰；持续阶跃的定位是检测器已知局限 → REVIEW_DETECTOR 建议。
- fp 来源：HARD_CLIP/NEAR_CLIP 预增益段引发 HIGH_FREQUENCY_DROPOUT（削波频谱变化）+ LEVEL_DROP（段尾回落）；ANTIPHASE 引发 mono 下混静音（反相立体声 mono=0 是真实现象）+ LEVEL_DROP。这些是**真实关联事件**（跨域传播），非随机误报——G12 门仅要求"不可接受"级误报，当前已分类记录。

## 实验设计修正记录（实验室价值）

梯级初版暴露 5 个实验设计缺陷（见 BASELINE.md）——矩阵是检验"耳朵"的真实工具，修正后全算子召回 1.0。
