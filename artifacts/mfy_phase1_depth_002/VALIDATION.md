# Localization Validation — MFY-PHASE1-DEPTH-002

日期：2026-08-09
方法：合成 ground-truth fixture（已知 start/end）+ 干净对照；定位指标按 07_LOCALIZATION_METRICS。

## 逐检测器结果（15 测试全绿）

| 事件 | fixture | 结果 | 边界 |
|---|---|---|---|
| CLIPPING_CLUSTER | 削波 2.0-2.6s | 检测 1 个，start/end 误差 <0.2s | integrity hop 50ms |
| NEAR_CLIPPING_CLUSTER | 近削波 | 检测（阈值规则） | 50ms |
| SILENCE_GAP | 静音 4.0-5.0s | 检测 1 个，边界 ≤0.15s | 100ms 窗 |
| NEGATIVE_CORRELATION_REGION | 反相 1.5-2.5s | 检测 ≥1，proxy 语义 | 100ms hop |
| PHASE_RISK_REGION | 反相 3.0-3.8s | 检测 ≥1 | 100ms hop |
| HIGH_FREQUENCY_DROPOUT | 宽带→4k 低通 2.0-4.0s | 检测，ESTIMATOR_DERIVED conf≤0.6 | 250ms hop |
| LEVEL_SPIKE | 0.05→0.7 gain | 检测，起点误差 <0.5s | 100ms hop |
| LEVEL_DROP | 0.7→0.05 gain | 检测 | 100ms hop |

## 定位精度（G13 诚实）

- 每事件 localization_precision_ms = 所属域 hop（50/100/250/100 ms）
- 无亚 hop 声称；无认证表计级精度声称

## 合并（G10）

- gap 50ms < 150ms 容差 → 合并为 1 事件 ✓
- 2.0 与 4.0s 相距 2s → 保持 2 事件 ✓

## 误报（G11）

- 干净正弦 6s：0 事件
- 干净噪声 6s：0 事件
