# AEP-ACU-002｜频响曲线对比报告

> 日期：2026-07-03
> 任务：RBJ Biquad EQ 替换 FFT sigmoid/Gaussian EQ
> 测量方法：RBJ → `scipy.signal.freqz`；Legacy FFT → 时域等效曲线公式

---

## 1. Low Shelf 对比 (200 Hz, ±6 dB)

![Low Shelf Comparison](aep_acu_002_low_shelf_comparison.png)

**关键差异：**

| 指标 | RBJ Biquad | Legacy FFT Sigmoid | 差异 |
|------|-----------|-------------------|------|
| DC 增益 (+6 dB) | +6.00 dB | +6.00 dB | 一致 |
| 3 dB 点 | ~200 Hz | ~200 Hz | 大致一致 |
| 过渡带宽 | Q=0.707 → ~1.0 oct | 硬编码 ~0.3 oct | **RBJ 更窄** |
| 形状 | 标准 2 阶 shelf | sigmoid (非标准) | 本质不同 |
| 高频趋近 | 0 dB (精确) | 0 dB (精确) | 一致 |

**结论：** RBJ low shelf 在截止频率和 DC 增益上与 legacy 一致。但 RBJ 的过渡带宽可控（通过 Q），而 legacy 固定不可调。RBJ 的 shelf 斜率符合标准 2 阶滤波器，legacy sigmoid 没有明确的 dB/oct 定义。

---

## 2. High Shelf 对比 (6 kHz, ±6 dB)

![High Shelf Comparison](aep_acu_002_high_shelf_comparison.png)

**关键差异：**

| 指标 | RBJ Biquad | Legacy FFT Sigmoid | 差异 |
|------|-----------|-------------------|------|
| HF 增益 (-6 dB) | -6.00 dB | -6.00 dB | 一致 |
| 3 dB 点 | ~6 kHz | ~6 kHz | 大致一致 |
| 过渡带宽 | Q=0.707 → ~1.0 oct | 硬编码 ~0.3 oct | **RBJ 更窄** |
| DC 增益 | 0 dB | 0 dB | 一致 |

**结论：** 与 low shelf 类似，主要差异是过渡带宽可控性。

---

## 3. Peaking 对比 (1 kHz, Q=1.0, ±6 dB)

![Peaking Comparison](aep_acu_002_peaking_comparison.png)

**关键差异：**

| 指标 | RBJ Biquad | Legacy FFT Gaussian | 差异 |
|------|-----------|-------------------|------|
| 中心频率增益 | +6.00 dB | +6.00 dB | 一致 |
| 带宽 (Q=1.0) | ~1.4 oct @ -3 dB (re: peak) | ~1.0 oct (Gaussian sigma) | **不同 Q 定义** |
| 形状 | 在 log-f 轴上对称 | 在线性 f 轴上对称 | **本质不同** |
| DC 增益 | 0 dB | 0 dB | 一致 |
| 远场衰减 | -12 dB/oct (2 阶) | 超高斯衰减 (~exp(-f²)) | RBJ 衰减更慢 |

**最关键发现：**
- RBJ peaking 的 "Q=1.0" 和 Legacy FFT 的 "Q=1.0" 对应不同的带宽——这不是一个参数映射问题，而是两个根本上不同的滤波器定义。
- RBJ peaking 在 log 频率轴上对称——行业中所有 peaking EQ 的标准行为。
- Legacy Gaussian 在线性频率轴上对称——高斯在 1 kHz 处看起来还 OK，但在更高/更低频率会表现完全不同。
- **这就是为什么旧 EQ 的参数不可跨版本复现的根本原因：Q 值的含义完全不同。**

---

## 4. 五种 RBJ 滤波器类型

![All Filter Types](aep_acu_002_all_filter_types.png)

展示了 RBJ 支持的全部五种滤波器类型的代表性曲线。

---

## 5. Q 值行为验证

![Q Comparison](aep_acu_002_q_comparison.png)

**验证结果：**
- Q=0.5: 宽带，~2.5 octaves → 行为正确
- Q=1.0: 标准，~1.4 octaves → 行为正确
- Q=2.0: 窄带，~0.7 octaves → 行为正确
- Q=4.0: 非常窄，~0.35 octaves → 行为正确
- Legacy Gaussian Q=1.0 (灰色虚线)：带宽介于 RBJ Q=1.0 和 Q=2.0 之间

**Q 值可预测性确认：** RBJ peaking 的 Q 值严格遵循行业标准定义：`bandwidth_oct = 2 * arcsinh(1/(2*Q)) / ln(2)`。Q=1.0 约等于 1.4 个倍频程的 -3 dB 带宽（从峰值向下）。DAW 用户期望的正是这种行为。

---

## 6. RMSE 测量（对数扫频）

以 20 Hz – 20 kHz 对数扫频信号，比较 RBJ 输出与理论曲线的 RMSE：

| 滤波器类型 | RMSE vs 理论 | 判定 |
|-----------|-------------|------|
| Low Shelf 200 Hz +6 dB | < 0.05 dB | **PASS** |
| High Shelf 6 kHz -6 dB | < 0.05 dB | **PASS** |
| Peaking 1 kHz Q=1 +6 dB | < 0.05 dB | **PASS** |
| High Pass 80 Hz Q=0.707 | < 0.05 dB | **PASS** |
| Low Pass 8 kHz Q=0.707 | < 0.05 dB | **PASS** |

**所有 RMSE < 0.1 dB 的验收标准通过。**

---

## 7. 零增益透明性

| 滤波器类型 | RMSE (输出 vs 输入, gain=0) | 判定 |
|-----------|---------------------------|------|
| Low Shelf | < -180 dB (b == a 精确) | **PASS** |
| High Shelf | < -180 dB (b == a 精确) | **PASS** |
| Peaking | < -180 dB (b == a 精确) | **PASS** |

**所有零增益情况下 b == a 系数相同 → 数学上恒等。**
