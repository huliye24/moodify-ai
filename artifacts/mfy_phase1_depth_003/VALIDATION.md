# Validation — MFY-PHASE1-DEPTH-003

日期：2026-08-09
方法：R301-R307 合成 fixture + I1-I12 不变量直接编码于测试（15 测试全绿）。

## Fixture 结果

| fixture | 断言 | 结果 |
|---|---|---|
| R301 平稳正弦 | S1 RMS 稳定（std < 0.5） | ✅ |
| R302 两态电平 | S1 过渡窗对齐（误差 <500ms） | ✅ |
| R303 立体声切换 | S1 反相窗 corr < -0.5 + 事件重叠窗 | ✅ |
| R304 频谱切换 | S2 hf_ratio 响应（宽带 vs 带限） | ✅ |
| R305 静音岛 | 低 RMS 实测（非伪造零）| ✅ |
| R306 削波阶梯 | S0 微尺度定位（误差 <40ms） | ✅ |
| R307 混合场景 | 全事件映射 + 全局 metric_count ≥20 + duration | ✅ |

## 不变量覆盖（10_REPRESENTATION_INVARIANTS.md）

- I1 源身份：representation.source_sha256 == 输入哈希 ✅
- I2/I3/I4 单调时间/有效时长/样本秒一致：逐平面断言 ✅
- I5 特征权威：plane_meta 与 registry 断言 ✅
- I6 尺度权威：scales.py 单一注册 ✅
- I7 缺失值诚实：NaN/null（测试注释显式） ✅
- I8 事件对齐：overlapping_windows 非空 ✅
- I9 全局一致：S3 == compute_metrics ✅
- I10 无语义突变：rep-v1 固定版本 ✅
- I11 确定性：allclose + dict 相等 ✅
- I12 资源有界：3.3x 时长 → 3.3x 窗 ✅

## 资源基准（K）

| 时长 | 构建时间 | 窗口总数 | 稠密数组大小 |
|---|---|---|---|
| 3 分钟 | 18.7s | 11,153 | ~491 KB |
| 10 分钟 | 56.2s | 37,193 | ~1,640 KB |

近似线性（3.33x 时长 → 3.30x 窗 / 3.00x 时间）。
