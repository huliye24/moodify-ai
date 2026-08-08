---
title: "泫榛开放式 MRS 跑分标准"
subtitle: "从 MRS v0.2 到无满分 AI 音乐真实度单位"
author: "Moodify / 文川院"
date: "2026-06-02"
CJKmainfont: "Noto Sans CJK SC"
mainfont: "Noto Sans CJK SC"
sansfont: "Noto Sans CJK SC"
monofont: "Noto Sans Mono CJK SC"
geometry: "margin=1in"
fontsize: 11pt
---

# 泫榛开放式 MRS 跑分标准

## 1. 核心定义

**MRS，Moodify Reality Score，是一种开放式 AI 音乐真实度跑分单位。**

它不是 100 分制，也不存在理论满分。

MRS 衡量的是：

> 一段 AI 音频与真实音乐声波参考系之间的物理距离。

距离越小，MRS 越高；距离越大，MRS 越低。

因此，MRS 不是“好不好听”的主观评价，而是 AI 音乐向真实声波结构收敛的定量指标。

---

## 2. 为什么 MRS 不采用 100 分制

100 分制隐含一个问题：它默认存在“满分”。

但 Moodify 的目标不是做一个封闭评分表，而是建立一个可以长期突破的声学跑分标准。

类似于：

| 类型 | 特征 |
|---|---|
| 显卡跑分 | 可以从几千增长到几万、几十万 |
| Elo 分 | 没有固定满分，水平越高分数越高 |
| dB 分贝 | 是相对强度单位，不是百分制 |
| MRS | 是声音真实度的开放式跑分单位 |

所以 MRS 应该表达：

```text
MRS 600  -> 普通 AI 音乐原声
MRS 1000 -> 第一代真实度基准
MRS 1300 -> 明显接近专业后期水平
MRS 1600 -> 高真实度 AI 音乐
MRS 2000+ -> 下一代声音真实度区间
MRS 3000+ -> 未来极限区间
```

---

## 3. 开放式 MRS 核心公式

开放式 MRS 从 MRS v0.2 的八维真实度指标发展而来，但最终输出不再是 0-100 分，而是一个无满分的跑分值。

核心公式为：

$$
MRS_{\mathrm{open}}=B+K\log_{10}\left(\frac{D_{\mathrm{ref}}+\varepsilon}{D_{\mathrm{real}}+\varepsilon}\right)
$$

其中：

| 符号 | 含义 | 建议初始值 |
|---|---|---|
| $MRS_{\mathrm{open}}$ | 开放式 MRS 跑分 | 无上限 |
| $B$ | 第一代基准线 | 1000 |
| $K$ | 跑分尺度系数 | 300 |
| $D_{\mathrm{ref}}$ | 第一代 AI 音乐参考距离 | 由基准样本集计算 |
| $D_{\mathrm{real}}$ | 当前音频与真实音乐参考系之间的物理距离 | 由八维声学距离计算 |
| $\varepsilon$ | 数值稳定项，避免除零 | $10^{-8}$ 或更小 |

推荐初始形式：

$$
MRS_{\mathrm{open}}=1000+300\log_{10}\left(\frac{D_{\mathrm{ref}}+\varepsilon}{D_{\mathrm{real}}+\varepsilon}\right)
$$

---

## 4. 公式解释

### 4.1 基准点

当：

$$
D_{\mathrm{real}}=D_{\mathrm{ref}}
$$

则：

$$
MRS_{\mathrm{open}}=1000
$$

这意味着：

> MRS 1000 被定义为 Moodify v0.2 阶段的第一代 AI 音乐真实度基准线。

---

### 4.2 距离缩小，跑分上升

如果当前音频与真实音乐之间的距离缩小 10 倍：

$$
D_{\mathrm{real}}=0.1D_{\mathrm{ref}}
$$

则：

$$
MRS_{\mathrm{open}}=1300
$$

如果距离缩小 100 倍：

$$
D_{\mathrm{real}}=0.01D_{\mathrm{ref}}
$$

则：

$$
MRS_{\mathrm{open}}=1600
$$

所以，该公式的含义是：

> 每当 AI 音乐与真实音乐声波参考系的距离缩小 10 倍，MRS 增加 300 分。

---

### 4.3 距离扩大，跑分下降

如果当前音频比第一代基准更远离真实音乐参考系：

$$
D_{\mathrm{real}}=10D_{\mathrm{ref}}
$$

则：

$$
MRS_{\mathrm{open}}=700
$$

因此 MRS 可以低于 1000，也可以持续高于 1000。

它不是满分制，而是开放增长制。

---

## 5. 声音真实距离 $D_{\mathrm{real}}$

开放式 MRS 的核心不是直接给音频打分，而是先计算它与真实音乐参考系之间的物理距离。

基础形式为：

$$
D_{\mathrm{real}}=\sum_{i=1}^{8}w_i d_i + \lambda_{\mathrm{OPR}}OPR + \lambda_{L} L
$$

也可以展开为：

$$
\begin{aligned}
D_{\mathrm{real}} ={}& w_1D_{\mathrm{spectrum}}
+w_2D_{\mathrm{dynamic}}
+w_3D_{\mathrm{texture}}
+w_4D_{\mathrm{space}} \\
&+w_5D_{\mathrm{transient}}
+w_6D_{\mathrm{fatigue}}
+w_7D_{\mathrm{balance}}
+w_8D_{\mathrm{plastic}} \\
&+\lambda_{\mathrm{OPR}}OPR
+\lambda_{L}LoudnessPenalty
\end{aligned}
$$

其中八个核心距离项继承自 MRS v0.2：

| 距离项 | 含义 |
|---|---|
| $D_{\mathrm{spectrum}}$ | 频谱分布与真实音乐参考分布的偏离程度 |
| $D_{\mathrm{dynamic}}$ | 动态范围、响度起伏、压缩状态的偏离程度 |
| $D_{\mathrm{texture}}$ | 人声、乐器、谐波纹理是否过平、过假 |
| $D_{\mathrm{space}}$ | 空间场、混响、声像宽度是否真实 |
| $D_{\mathrm{transient}}$ | 鼓点、辅音、拨弦等瞬态是否发软或模糊 |
| $D_{\mathrm{fatigue}}$ | 高频刺激、响度压迫、长期聆听疲劳风险 |
| $D_{\mathrm{balance}}$ | 低频、中频、高频能量是否失衡 |
| $D_{\mathrm{plastic}}$ | AI 塑料感、伪影感、过度平滑风险 |

惩罚项：

| 惩罚项 | 含义 |
|---|---|
| $OPR$ | Over Processing Risk，过度处理风险 |
| $LoudnessPenalty$ | 响度异常惩罚 |

---

## 6. 从 MRS v0.2 到开放式 MRS

MRS v0.2 的公式为：

$$
MRS_{\mathrm{final}}=\alpha MRS_{\mathrm{after}}+\beta\Delta MRS-\gamma OPR-\eta LoudnessPenalty
$$

该公式适合用于 Night Worker 的处理版本排序，但它更像一个工程筛选公式，而不是最终跑分单位。

因此，v0.2 不应该被废弃，而应该升级为开放式 MRS 的底层特征层。

关系如下：

```text
MRS v0.2
八维真实度检测 + 过度处理惩罚 + 响度惩罚
        ↓
计算 D_real
音频与真实音乐参考系之间的物理距离
        ↓
MRS Open Benchmark
转化为无满分开放式跑分
```

可以概括为：

```text
MRS v0.2 = 声音体检表
MRS Open = 声音跑分单位
```

---

## 7. MRS 跑分区间草案

| MRS 区间 | 声音状态 | 解释 |
|---:|---|---|
| < 500 | 低真实度 AI 音频 | 明显塑料感、动态差、频谱假 |
| 500-800 | 普通 AI 音乐原声 | 可听，但真实感不足 |
| 800-1000 | 第一代可发布级 AI 音乐 | 接近普通平台发布水平 |
| 1000-1300 | Moodify v0.3/v0.4 目标区间 | 明显优于普通 AI 原声 |
| 1300-1600 | 专业后期接近区间 | 塑料感显著下降，结构更真实 |
| 1600-2000 | 高真实度 AI 音乐 | 接近成熟商业音乐声波结构 |
| 2000+ | 下一代真实度区间 | 需要算法、工艺、硬件链路共同提升 |
| 3000+ | 未来极限区间 | 代表新的声音真实度阶段 |

这些区间不是永久标准，而是第一代工程标尺。后续需要随着真实音乐参考库和 Moodify 工艺库不断校准。

---

## 8. 示例换算

假设 $B=1000$，$K=300$：

| $D_{\mathrm{real}}/D_{\mathrm{ref}}$ | 含义 | MRS |
|---:|---|---:|
| 10 | 比基准更差 10 倍 | 700 |
| 2 | 比基准更差 2 倍 | 910 |
| 1 | 等于第一代基准 | 1000 |
| 0.5 | 比基准接近真实约 2 倍 | 1090 |
| 0.1 | 比基准接近真实 10 倍 | 1300 |
| 0.01 | 比基准接近真实 100 倍 | 1600 |
| 0.001 | 比基准接近真实 1000 倍 | 1900 |

因此，MRS 的增长不是线性的，而是对数增长。

这使它更适合长期技术演化：早期小幅提升也能体现，后期极限突破也不会被 100 分上限锁死。

---

## 9. MRS 的基准库原则

为了让 MRS 成为可比较的跑分标准，必须冻结基准库。

建议建立：

```text
MRS-2026A Reference Set
```

该参考集至少包含：

1. 真实商业音乐样本：无损或高质量母带版本；
2. 真实人声样本：包含不同性别、语言、唱法；
3. 真实乐器样本：鼓、钢琴、吉他、弦乐、贝斯等；
4. AI 原始音乐样本：Suno / Udio / 其他生成平台；
5. Moodify 处理样本：mild / medium / strong / destructive / loudness_only / dark_only；
6. 过度处理样本：用于建立惩罚边界。

关键原则：

> 同一个 MRS 版本必须使用同一个冻结参考集。  
> 如果参考集改变，必须升级版本号，例如 MRS-2026B、MRS-2027A。

否则跑分就会失去可比性。

---

## 10. 工程落地建议

### 10.1 文件结构

建议在 Moodify 工程中新增：

```text
workers/mrs_formula_v03_open.py
configs/mrs_open_weights.yaml
configs/mrs_reference_2026A.yaml
runs/mrs_open_validation_v03/
output/rankings/mrs_open_rankings.csv
```

---

### 10.2 配置文件草案

```yaml
version: "MRS-OPEN-v0.3-2026A"

benchmark:
  base_score: 1000
  scale_factor: 300
  epsilon: 1.0e-8
  reference_distance: "median_ai_baseline_distance_2026A"

distance_weights:
  spectrum: 0.18
  dynamic: 0.16
  texture: 0.16
  space: 0.13
  transient: 0.13
  fatigue: 0.08
  balance: 0.08
  plastic: 0.08

penalty_weights:
  opr: 0.30
  loudness: 0.15

output:
  score_name: "MRS_open"
  no_max_score: true
  baseline_score: 1000
```

---

### 10.3 Night Worker 输出字段

建议在 ranking CSV 中增加：

```text
mrs_open_before
mrs_open_after
delta_mrs_open
distance_real_before
distance_real_after
distance_ratio
mrs_version
reference_set
```

这样每一次处理都可以留下明确证据：

```text
原始音频：MRS 642
Moodify mild：MRS 884
Moodify medium：MRS 1117
destructive：MRS 531
```

---

## 11. 人工听感的位置

开放式 MRS 的底层依据不是人工盲听，而是数学和物理声学距离。

人工听感最多用于：

1. sanity check；
2. 发现公式盲区；
3. 作为辅助修正参考；
4. 验证极端样本是否违背常识。

但 MRS 的核心真理来源应该是：

```text
真实音乐参考系
声学特征分布
物理距离函数
过度处理惩罚
AI 伪影检测
```

因此，Moodify 的路线不是“听众投票系统”，而是：

> AI 音乐真实度的工程计量体系。

---

## 12. 最终定义

可以正式写成：

> 泫榛开放式 MRS 跑分标准，是一种用于衡量 AI 音乐真实度的开放式工程计量体系。它不采用 100 分制，也不存在理论满分。MRS 通过计算 AI 音频与真实音乐声波参考系之间的物理距离，将声音真实度转化为可比较、可复现、可长期突破的跑分单位。MRS 1000 被定义为 Moodify v0.2 阶段的第一代 AI 音乐真实度基准线，后续算法、工艺、参考库和硬件链路的提升，都可以推动 MRS 向 1300、1600、2000、3000 以上继续增长。

一句话：

> **别人说这首 AI 音乐“听起来更好”。  
> Moodify 要说：这首 AI 音乐的真实度从 MRS 642 提升到了 MRS 1187。**

