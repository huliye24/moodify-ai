# 定理 2：代理指标校准定理与 EDSR 实验

**来源**: 技术势能稳步推进的数学路线与定理库 §3 定理2
**层级**: 内部工作定理 — 搜索有效性的前提
**状态**: P0 优先级 — 不验证此定理, 搜索方向可能系统性地错误

---

## 0. 定理陈述

### 0.1 自然语言

代理指标只有在与人耳偏好存在稳定相关性时，才有资格驱动搜索。相关性不够时，代理指标只能作为诊断解释，不能作为优化目标。

### 0.2 形式化

```
ProxyScore(c_i) = p_i
HumanPreference(c_i) = h_i

若:
  Corr(rank(p), rank(h)) ≥ τ
则:
  ProxyScore 可用于候选排序

若:
  Corr(rank(p), rank(h)) < τ
则:
  ProxyScore 只能作为诊断解释, 不能作为搜索目标
```

建议阈值：τ ≥ 0.5 可作为主排序信号；0.3 ≤ τ < 0.5 只能混合使用；τ < 0.3 必须重构指标。

---

## 1. 为什么代理指标可能出错

### 1.1 代理指标的构造路径

当前 EDSR_proxy 的计算链：

```
诊断 18 参数
  → diagnostic_to_process → 5D raw vector
  → params_to_strengths → 5D strength
  → apply_chain_transfer → 5D proxy vector
  → distance(proxy, ideal) vs distance(raw, ideal) → EDS proxy
  → minus safety_penalty → EDSR_proxy
```

这个链条中，每一步都引入了近似：
1. `diagnostic_to_process` 是启发式映射，非精确
2. `T_EFFECTS` 是经验估计，P5/P50/P95 取自有限样本
3. `get_ideal_process_vector` 是预设值，可能不完全匹配用户感知
4. 5D 欧氏距离隐含假设了维度独立和等权重——这几乎肯定不成立

### 1.2 代理指标失真的典型模式

| 失真模式 | 成因 | 后果 |
|---------|------|------|
| 高频偏好 | WHS 中 S4_AirBand 权重过高 | 代理偏好过于明亮的版本 |
| 压缩偏好 | 代理忽略动态保留的主观价值 | 代理偏好过度压缩的版本 |
| 安全过度 | safety_penalty 过重 | 代理永远选最保守的方案 |
| 维度塌缩 | 5D 中某维主导距离计算 | 代理无法区分该维度外的差异 |

---

## 2. EDSR_true 的收集方法

### 2.1 A/B 成对比较（推荐作为第一版）

```
实验设计:
  - 10 首 AI 生成音乐 (覆盖不同风格和缺陷类型)
  - 每首生成 5 个版本: preset / search-top1 / search-top2 / search-top3 / LLM推荐
  - 5-10 位听众
  - 每对 (原始, 处理版本) 做 A/B 选择: "A 更好 / B 更好 / 无差异"
  - 总计: 10 * 5 * 10 = 500 次比较 (每位听众约 50-100 次, 控制在疲劳阈值内)
```

### 2.2 Bradley-Terry 胜率模型

```
对每对 (i, j):
  P(i beats j) = exp(θ_i) / (exp(θ_i) + exp(θ_j))

其中 θ_i 是版本 i 的潜在质量参数。
通过最大似然估计 θ_1...θ_k。
θ_i 的排序 → EDSR_true 的排序。
```

### 2.3 相关性测量

```
Spearman ρ = Corr(rank(EDSR_proxy), rank(θ_hat))
Kendall τ = P(concordant) - P(discordant)

若:
  ρ ≥ 0.5 → 代理可用于搜索排序
  0.3 ≤ ρ < 0.5 → 代理只能用于粗筛 (top-50 而非 top-3)
  ρ < 0.3 → 代理不可用于排序, 需重构
```

---

## 3. 校准策略

### 3.1 简单线性校准

```
EDSR_calibrated = α * EDSR_proxy + β

其中 α, β 通过最小化 |EDSR_calibrated - EDSR_true| 拟合。
```

### 3.2 分情绪校准

不同情绪的代理指标偏差可能不同。例如「温柔觉醒」依赖低频指标，「废土机械」依赖压缩和失真指标。

```
EDSR_calibrated = α(emotion) * EDSR_proxy + β(emotion)
```

### 3.3 分层校准

如果某些音频类型（如纯器乐 vs 有人声）的代理偏差显著不同：

```
EDSR_calibrated = α(type) * EDSR_proxy + β(type)
type ∈ {vocal, instrumental, electronic}
```

---

## 4. 失败样本分析格式

每个代理预测失败（|proxy_rank - true_rank| ≥ 3）的样本必须记录：

```json
{
  "sample_id": "CAL-001",
  "audio_type": "piano_ballad",
  "emotion_target": "GA",
  "proxy_score": 82.0,
  "true_rank": 5,
  "proxy_rank": 1,
  "rank_error": 4,
  "suspected_cause": "S4_AirBand over-weighting caused proxy to prefer overly bright version",
  "diagnosis_snapshot": {"S4_AirBand": -4.2, "S1_SubPresence": -3.1},
  "revision_note": "Consider reducing spectrum dimension weight for dark-timbre audio"
}
```

---

## 5. 留给后续 AI 的题目 (A2)

**题目 A2：建立 EDSR_proxy 与 EDSR_true 的校准实验。**

要求输出:
1. 10 首歌 × 5 版本的实验素材
2. Bradley-Terry 或成对胜率建模脚本
3. Spearman/Kendall 相关计算
4. 失败样本表（格式如上）
5. Proxy Metric Revision Plan — 如果 ρ < 0.3, 提出重构方案

---

## 6. 理论参考

1. Bradley, R. A. & Terry, M. E. (1952). "Rank Analysis of Incomplete Block Designs." *Biometrika*, 39(3-4), 324-345. — 成对比较 → 胜率模型。

2. Thurstone, L. L. (1927). "A Law of Comparative Judgment." *Psychological Review*, 34(4), 273-286. — 主观判断尺度化。

3. Dawid, A. P. & Skene, A. M. (1979). "Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm." *Journal of the Royal Statistical Society: Series C*, 28(1), 20-28. — 多听众噪声建模。

4. ITU-R BS.1534-3 (2015). *Method for the subjective assessment of intermediate quality level of audio systems* (MUSHRA). — 多版本主观评价协议。

5. Kendall, M. G. (1938). "A New Measure of Rank Correlation." *Biometrika*, 30(1/2), 81-93. — Kendall τ 定义。

6. 母文件 §3 定理2：代理指标校准定理的原始陈述。

---

*Moodify 定理库 · 定理 2 · v1.0*
