# 05 — Research Direction / 研究方向

> **Document Type:** Industrial Documentation System
> **Date:** 2026-08-23
> **Authority:** Research direction document. Research outputs live under `research/`.

---

## 1. 核心问题

**Can machines learn to hear? — 机器能学会听吗？**

人类发展出了视觉智能（识别、理解、解释图像）。机器需要听觉智能：不止处理声音，而是理解声音里发生了什么。这是 Moodify 存在要探索的问题，也是整个 AI 音乐产业缺失的一层。

---

## 2. 研究主线

### 2.1 Wave-Spectral Evolution (WSE)

**问题：** 声音在生产过程中发生了什么？

- 波形与频谱特征如何随制作环节（录音→混音→母带）演化
- 可测量的信号属性与感知质量的关系
- 已有论文：`research/papers/WSE-AIM-001_Wave-Spectral_Evolution.pdf`
- `WSE-AIM-002_MIDI-Score-Anchored_Post-Production.pdf`

### 2.2 三层研究架构

**框架：** `research/papers/Moodify_Three_Layer_Research_Architecture_Edition_0.1.pdf`

Moodify 的研究按三层组织：

| 层 | 内容 | 学科 |
|----|------|------|
| WSE — Wave-Spectral Evolution | 声音里发生了什么 | 信号处理、声学 |
| MSE — Musical-Structural Engineering | 音乐结构是什么 | 音乐信息检索（MIR） |
| PPE — Production Process Engineering | 结果如何可靠地生产、验证、恢复 | 工程学 |

### 2.3 听觉判断与不确定性

- 有界判断（bounded judgment）：机器只能在已验证范围内决策
- 不确定性量化：每个评分携带不确定度
- 证据链：每个判断产出可审计的 evidence artifact
- 升级机制：证据不足时产生 `HUMAN_REQUIRED`，而非虚构确定性

### 2.4 人类偏好学习

- 听测协议（`listening/` 模块）：盲测、响度匹配
- 听觉判断如何为机器评估提供校准信号
- 情绪目标（emotion targets）与感知的映射

### 2.5 音乐资产估值

- 音乐价值评分：商业/艺术/技术三维建模
- 情绪与场景标签的可计算表示
- 资产分级（S/A/B/C/D）的统计基础

---

## 3. 实验体系

### MAMSE 系列（Music Analysis & Music Structural Engineering）

`research/experimental/`（迁移自 `moodify_experimental/`）

16 个实验模块，每个独立成证据包：

| 系列 | 主题 |
|------|------|
| MAMSE-001..005 | 分解方法（NMF、RPCA、多线性分析） |
| MAMSE-006..010 | 协方差、图信号处理、结构分析 |
| MAMSE-011..016 | Gammatone 滤波器组、掩蔽、对象分离、音高跟踪 |

**规则：** 实验模块状态为 EXPERIMENTAL_ACCEPTED，不进入生产主线，不作为能力声明。

### 资产循环（Asset Loop）

```
Production Case → Measurement Record → Evidence Artifact
→ Theory Update → Rule Update → Next Production Case
```

每个生产案例产出测量记录与证据工件，反哺理论与规则更新 — 研究与工程通过这个循环互相驱动。

### 评测基准

`research/benchmarks/` — 数据集 schema、评测协议、基线脚本。

---

## 4. 研究产出规范

| 产出 | 位置 | 要求 |
|------|------|------|
| 论文 | `research/papers/` | 双语摘要；可复现实验 |
| 白皮书 | `research/whitepapers/` | 面向产业；方法论 + 验证数据 |
| 基准 | `research/benchmarks/` | 评测协议 + 公开数据 |
| 实验 | `research/experimental/` | 证据包完整；状态标注 |

---

## 5. 与产品的关系

```
研究 → 引擎：新的测量方法、更好的表示、更准的评分
引擎 → 研究：真实案例数据、失败模式、生产约束
```

- **QA** 消费：声学测量 + 质量评分研究
- **Master** 消费：受控干预 + 身份保持研究
- **Rating** 消费：资产估值 + 情绪建模研究
- **Supply** 消费：相似性 + 场景匹配研究

研究的每一步进展直接增强引擎能力，引擎的每个生产案例为研究提供数据。

---

## 6. 开放协作

欢迎以下方向的外部研究合作：

- AI 听觉模型（auditory models）
- 音频基础模型（audio foundation models）
- 音乐质量基准（music-quality benchmarks）
- 个性化听感（personalized listening）

**姿态：** 证据优先 — 机器决策保持 scoped、versioned、reviewable；证据不足产生不确定性或人工审核，而非虚构确定性。
