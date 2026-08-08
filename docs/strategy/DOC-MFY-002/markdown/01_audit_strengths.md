# T1｜声学合规优点：已具备能力表

> 审计范围：moodify-core-package、moodify_runtime、workers/
> 对照标准：ITU-R BS.1770、EBU Tech 3342、RBJ EQ Cookbook、Schroeder 1962、Zwicker & Fastl 2007
> 审计日期：2026-07-02

---

## 核心判断

Moodify v0.1.0 在**响度测量合规**、**守恒审计框架**、**诊断维度覆盖**、**工艺知识编码**四个方面已达到或超过行业基准。但在**滤波器标准合规**、**感知建模**、**心理声学特征**三个方面存在显著差距（见 02_defect_register.md）。

总体评分：**声学合规度 62/100**（详见 08_formula_metrics.md）。

---

## 优点登记表

### S-001：ITU-R BS.1770-5 响度测量合规

| 属性 | 内容 |
|------|------|
| 标准 | ITU-R BS.1770-5 (2023) — Algorithms to Measure Audio Programme Loudness |
| 实现位置 | `diagnosis/engine.py:_compute_lufs()` — pyloudnorm 集成 |
| 审计证据 | `diagnosis/quality_gate.py` LUFS 容差 0.5 dB；`conservation.py` 使用 LUFS 作为能量审计基准 |
| 合规等级 | **完全合规** — 使用标准库 pyloudnorm (Steinmetz & Reiss, 2020)，K-weighting 滤波器符合 BS.1770-5 §7 |
| 战略意义 | LUFS 是广播/流媒体行业的通用响度语言 — Moodify 的输出可直接对接 Spotify (-14 LUFS)、YouTube (-14 LUFS)、Apple Music (-16 LUFS) 等平台的响度标准 |
| 对应命题 | P04（公式学术深度）、P12（精度压制） |

### S-002：EBU Tech 3342 响度范围 (LRA) 测量

| 属性 | 内容 |
|------|------|
| 标准 | EBU Tech 3342 (2016) — Loudness Range: A Measure to Supplement Loudness Normalisation |
| 实现位置 | `diagnosis/engine.py:_compute_lra()` — 3 秒块 + P10/P95 百分位法 |
| 审计证据 | 诊断引擎 D2 参数（动态范围指数）部分基于 LRA 计算 |
| 合规等级 | **完全合规** — 3 秒块分析和百分位法符合 EBU Tech 3342 §4 |
| 战略意义 | LRA 是比 crest factor 更稳健的动态范围度量 — 不受少数极端峰值的影响 |
| 对应命题 | P03（知识复杂度）、P12（精度压制） |

### S-003：PHYS-007 能量守恒审计框架

| 属性 | 内容 |
|------|------|
| 标准 | PHYS-001 定理 2（自研）、PHYS-007 §4-5（自研） |
| 实现位置 | `conservation.py:audit_conservation()` — 三级审计 (safe/warning/violation) |
| 审计证据 | ΔL_residual ≤ 3σ → safe; 3σ < ... ≤ 12σ → warning; > 12σ → violation |
| 合规等级 | **自研创新** — 非行业标准，但方法论严谨（基于测量噪声 σ 的统计阈值） |
| 战略意义 | 这是 Moodify 独有的质量门机制——竞品没有等价物。能量守恒审计确保每次处理的可归因性 |
| 对应命题 | P04（公式学术深度）、P11（处理即实验） |

### S-004：18 参数多维度诊断引擎

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 5 维波场 (E/D/S/T/H) × 18 诊断参数 |
| 实现位置 | `diagnosis/engine.py` — 5 频谱 (S1-S5) + 4 动态 (D1-D4) + 4 空间 (SP1-SP4) + 4 层级 (L1-L4) + 4 情绪 (E1-E4) |
| 审计证据 | 典型竞品 (iZotope Ozone 助手、LANDR) 提供 3-5 参数诊断。Moodify 的 18 参数覆盖了频谱平衡、动态范围、空间定位、谐波结构、情绪感知五个维度 |
| 合规等级 | **行业领先** — 诊断维度数约为竞品的 4-6 倍 |
| 战略意义 | 诊断深度直接决定处理精度——无法诊断的缺陷无法被修复。18 参数体系构成知识壁垒（L2 半可编码知识） |
| 对应命题 | P03（知识复杂度）、P12（维度压制） |

### S-005：七组 MRS 真实度评分

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 马氏距离 + 7 特征组加权 |
| 实现位置 | `reality_metrics.py` + `workers/mrs_metrics.py` |
| 审计证据 | 7 组特征 (spectrum/dynamic/transient/space/texture/temporal/artifact) × 加权马氏距离 → MRS = 100 × exp(-D_R) |
| 合规等级 | **行业领先** — 大多数竞品仅提供单一维度评分（如 LANDR 的"mastering quality"）。MRS 的 7 组分解提供了可解释的多维度质量画像 |
| 战略意义 | MRS 是 Moodify 的"质量货币"——所有处理决策、校准反馈、实验评估都以此为单位。MRS Open Benchmark v0.3.1 已公开 |
| 对应命题 | P06（实验声誉）、P12（精度压制） |

### S-006：8 情绪 × 15 参数工艺链知识库

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 8 情绪原型 (GA/SE/UD/LW/HL/DR/WL/CN) × 15 参数约束矩阵 |
| 实现位置 | `knowledge/craft_chains.py` — 每种情绪含 min/rec/max 值、risk_warnings、contraindications、processing_steps |
| 审计证据 | 禁忌症 (contraindications) 和常见缺陷 (common_defects) 是隐性知识的显式编码——这些边界条件只有通过真实实验才能发现 |
| 合规等级 | **自研创新** — 无公开竞品提供此等级的情绪-参数映射 |
| 战略意义 | 工艺链是 Moodify 最难复制的知识资产——它同时依赖声学理论（L1）、实验数据（L2）、听觉判断（L3）和方法论（L4） |
| 对应命题 | P05（隐性知识）、P15（先验经验） |

### S-007：B 矩阵系统识别与 T_EFFECTS 状态转移

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 线性化系统识别 + 岭回归在线校准 |
| 实现位置 | `physics/experiments.py` + `physics/b_matrix_parallel.py` + `calibration/online.py` |
| 审计证据 | X' = X + B × Δu + ε — 5×15 线性化映射，残差 ε 捕获非线性交互。在线岭回归根据实际处理结果迭代修正 D 值 |
| 合规等级 | **自研创新** — 将控制系统理论应用于音频处理参数推荐，竞品无等价机制 |
| 战略意义 | B 矩阵是参数推荐的数学引擎——没有系统识别实验就无法获得。这是"非代码化资产"的典型案例 |
| 对应命题 | P04（公式学术深度）、P10（实验飞轮） |

### S-008：HPSS 谐波/打击乐分离

| 属性 | 内容 |
|------|------|
| 标准 | Ono et al. (2008) — NMF-based HPSS; Fitzgerald (2010) — median-filtering HPSS |
| 实现位置 | `processing/spectral_chain.py` — librosa.decompose.hpss() with margin=2.0 |
| 审计证据 | 有意识地选择 HPSS 而非 Demucs 等深度学习方法——基于速度（CPU 实时）和伪影控制（HPSS 不引入学习模型的 hallucination）的工程决策 |
| 合规等级 | **合规且工程合理** — HPSS 是成熟的 MIR 标准方法。选择 HPSS over DL 在此阶段是正确的工程权衡 |
| 战略意义 | 分离处理策略（谐波链 vs 打击乐链）是 Moodify 与简单全混处理的本质区别——更高维度、更精确的处理 |
| 对应命题 | P12（维度压制）、P10（实验飞轮） |

### S-009：安全边界投影

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 15 参数硬边界 (hard_bounds) + 投影算子 (projection) |
| 实现位置 | `safety/bounds.py` + `safety/projection.py` |
| 审计证据 | 每个工艺参数有 min/max 硬边界，越界参数自动投影到最近有效值。投影日志记录每次修正 |
| 合规等级 | **工程良好** — 参数边界保护是工业级音频处理的基本要求，Moodify 的实现完整且可审计 |
| 战略意义 | 安全层是"免疫系统"的一部分——防止参数漂移或异常推荐导致的音频损坏 |
| 对应命题 | P09（有机体隐喻）、P11（处理即实验） |

### S-010：Pedalboard 生产级效果器集成

| 属性 | 内容 |
|------|------|
| 标准 | Spotify pedalboard (基于 JUCE C++) |
| 实现位置 | `processing/pedalboard_chain.py` — PeakFilter, LowShelfFilter, Compressor, Reverb, Distortion |
| 审计证据 | 15 参数工艺卡通过 pedalboard 的 C++ 后端执行——比纯 Python FFT EQ（operators.py）具有更好的滤波器形状精度和实时性能 |
| 合规等级 | **合规** — pedalboard 使用标准 RBJ biquad 滤波器设计，滤波器形状符合 Audio EQ Cookbook |
| 战略意义 | 主处理路径 (pedalboard_chain.py) 已使用合规滤波器——operators.py 的 FFT EQ 是遗留/降级路径。但需文档说明两条路径的滤波器差异 |
| 对应命题 | P01（代码可复制性）、P13（模型层级） |

### S-011：三评委 AI 评估系统

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — DeepSeek + 客观指标 + 融合评分 |
| 实现位置 | `evaluation/judges.py` |
| 审计证据 | 多评委结构借鉴了 ITU-R BS.1116 的多评估者设计——虽然未实施正式的双盲协议，但架构已为此预留 |
| 合规等级 | **自研创新** — 使用 AI 评委进行声学质量评估是前沿方向。三个独立评委降低了单一评估者的偏差 |
| 战略意义 | AI 评委可实现 24/7 自动化质量评估——这是人类听感测试无法达到的规模 |
| 对应命题 | P06（实验声誉）、P13（模型层级） |

### S-012：频段定义体系

| 属性 | 内容 |
|------|------|
| 标准 | 自研 — 六频段标准 + 七频段扩展 |
| 实现位置 | `bands.py` — Sub 20-60, Bass 60-250, Low-Mid 250-500, Mid 500-2000, Presence 2000-5000, Air 8000-16000 |
| 审计证据 | 频段划分与心理声学临界频带 (Zwicker & Fastl, 2007) 大致对齐——Bass 对应 Bark 3-6, Mid 对应 Bark 9-14, Presence 对应 Bark 15-19 |
| 合规等级 | **部分合规** — 频段边界与心理声学 Bark 尺度大致对齐，但**存在内部不一致**：`diagnosis/metrics.py` 的 Bass 上界为 200 Hz，`bands.py` 为 250 Hz（见 DEF-006） |
| 战略意义 | 统一频段定义是所有诊断和处理的根基——频段不一致会导致跨模块测量偏差 |
| 对应命题 | P03（知识复杂度） |

---

## 优点统计

| 类别 | 数量 | 条目 |
|------|------|------|
| 完全合规 | 4 | S-001 (LUFS), S-002 (LRA), S-008 (HPSS), S-010 (Pedalboard) |
| 自研创新 | 5 | S-003 (守恒审计), S-006 (工艺链), S-007 (B 矩阵), S-011 (三评委), S-004 (18 参数) |
| 行业领先 | 2 | S-004 (诊断维度), S-005 (MRS 七组评分) |
| 良好工程 | 1 | S-009 (安全边界) |
| 部分合规 | 1 | S-012 (频段定义——存在内部不一致) |

**总计：12 项已具备能力**，其中 6 项为自研创新或行业领先。

---

## 验收检查

- [x] 每条优点有唯一编号 (S-001 ~ S-012)
- [x] 每条优点标注对照标准
- [x] 每条优点标注实现位置（文件路径）
- [x] 每条优点标注审计证据
- [x] 每条优点标注合规等级
- [x] 每条优点标注战略意义
- [x] 每条优点映射到 DOC-MFY-001 命题
- [x] 优点统计表汇总
