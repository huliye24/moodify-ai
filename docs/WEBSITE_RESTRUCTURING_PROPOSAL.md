# Moodify 官网重构方案 — rongjingmusic.com

> **Document Type:** Website Restructuring Proposal
> **Date:** 2026-08-23
> **Target Site:** https://rongjingmusic.com/
> **Goal:** 从「AI 音乐产品网站」升级为「AI Audio Intelligence Company」官网

---

## 1. 现状分析

### 当前网站结构（2026-08-23 抓取）

| Section | 当前内容 | 定位 |
|---------|---------|------|
| Hero | "AI Audio Player — Make every song sound better" | 单一产品（播放器） |
| The Problem | 播放停留在固定时代 | 播放器痛点 |
| The Approach | AI 音频技术找更好的播放方式 | 播放器方案 |
| Products | Moodify Player / Cloud Audio / Personalized Listening | 三条产品线 |
| Technology | 输入→分析→处理→优化→输出 | 播放器技术链 |
| Research | Can machines learn to hear? | 研究方向 |
| Android | APK 下载 | 单产品分发 |
| Footer | 荣景文川公司信息 | 公司 |

### 核心问题

1. **单一产品形象** — 首页以 Player 为绝对主角，访客第一印象是「一个音乐播放器 App」
2. **没有公司层叙事** — 没有「我们在建设什么基础设施」的宏大叙事
3. **B2B 能力被埋没** — Cloud Audio（面向合作方的基础设施）只占一小块卡片
4. **缺少四大产品支柱** — QA / Master / Rating / Supply 完全没有露出
5. **缺少投资人/合作方入口** — 没有 business、whitepaper、partnership 页面

---

## 2. 重构目标

**从：** AI 音乐产品网站（卖播放器）
**到：** AI Audio Intelligence Company（卖基础设施 + 产业能力）

访客应该在 10 秒内理解：Moodify 是一家建设音乐产业听觉智能基础设施的 AI 公司。

---

## 3. 新首页结构

### Hero

```
Moodify
The Intelligence Layer for the Future of Music.

AI Audio Intelligence Infrastructure
— We measure, understand, score, and process audio
  for the music industry.

[ Explore the Engine ]  [ For Partners ]
```

**要点：**
- 主标题不再出现 "Player"
- 副标题一句话讲清公司定位
- 双 CTA：技术好奇者 → Engine；商业合作方 → Partners

### Section 1 — Moodify Engine（AI Ear Infrastructure）

```
Moodify Engine
AI Ear Infrastructure

One auditory intelligence engine. Every Moodify product
is built on it — and partners can build on it too.

[ Acoustic Analysis ]  [ Music Understanding ]
[ Scoring Engine ]     [ Recommendation Engine ]

Every judgment produces evidence.
Every score carries uncertainty.
Every decision is auditable.
```

**内容要点：**
- 4 个引擎能力卡片（分析 / 理解 / 评分 / 推荐）
- 强调 evidence-first、uncertainty-aware 的技术差异化
- 可放一个交互式频谱/LUFS 分析 demo 作为视觉锚点

### Section 2 — Moodify QA（AI Music Quality Assurance）

```
Moodify QA
AI Music Quality Assurance

AI-generated music is exploding. Quality verification
hasn't kept up. Moodify QA industrializes it.

- LUFS & platform compliance (Spotify / Apple / YouTube)
- Spectral, dynamic range & true-peak diagnostics
- MRS quality scoring with uncertainty bounds

[ The QA standard stack → ]
```

**产业叙事：** AI 生成音乐爆发 → 质量验证成为瓶颈 → Moodify 把它工业化。

### Section 3 — Moodify Master（Industrial Audio Processing）

```
Moodify Master
Industrial Audio Processing

Mastering that never destroys musical identity.

- Evidence-driven DSP intervention
- Identity preservation gates
- Commercial release standardization

[ How controlled processing works → ]
```

**产业叙事：** 不是「自动修音」，是「有边界、可审计的工业级音频处理」。

### Section 4 — Moodify Rating（Music Asset Intelligence）

```
Moodify Rating
Music Asset Intelligence

Music as a measurable asset class.

- Value scoring: commercial / artistic / technical
- Emotion & scene tagging
- S/A/B/C/D asset grading for catalogs & marketplaces

[ Rating methodology → ]
```

**产业叙事：** 音乐目录需要机器可读的估值层，Moodify 提供评分基础设施。

### Section 5 — Moodify Supply（Future Music Economy）

```
Moodify Supply
Future Music Economy

Matching music to where it creates value.

- Audio similarity & semantic search
- Scene matching for game / film / advertising
- Verified supply pipeline: Intake → Process → Deliver → Verify

[ Supply chain architecture → ]
```

**产业叙事：** 游戏/影视/广告授权市场碎片化，Moodify 建设匹配层。

### Section 6 — Research

```
Research
Can machines learn to hear?

- Wave-Spectral Evolution (WSE)
- Auditory intelligence architectures
- Human preference learning

[ Papers ]  [ Whitepapers ]  [ Benchmarks ]
```

**升级点：** 从单一 research 页升级为三入口：Papers（学术）/ Whitepapers（产业）/ Benchmarks（方法）。

### 底部新增 — Company Bar

```
Moodify is a product of 荣景文川.
Building AI audio intelligence infrastructure.

[ About ]  [ Business Inquiries ]  [ Research Collaboration ]
```

---

## 4. 现有内容的处置

| 现有内容 | 处置 |
|---------|------|
| AI Audio Player hero | 移到 Player 产品子页 |
| The Problem / The Approach | 精简后作为 Engine section 的支撑文案 |
| Moodify Player 卡片 | 保留，移入 "Products we ship" 或 apps 区域 |
| Cloud Audio 卡片 | 升级为 Engine 的 "For Partners" 入口 |
| Personalized Listening 卡片 | 保留为 roadmap 项 |
| Technology 链路图 | 升级为 Engine 架构图（四层架构） |
| Research section | 扩展为 Papers / Whitepapers / Benchmarks 三入口 |
| Android APK 下载 | 移到底部或 apps 子页，不再是首页主角 |

---

## 5. 新增页面建议

| 页面 | 路径 | 内容 |
|------|------|------|
| Engine | `/engine` | 引擎技术详解 + 交互 demo |
| For Partners | `/partners` | B2B 合作模式、API 接入、案例 |
| Whitepapers | `/research/whitepapers` | 产业白皮书下载（留资入口） |
| Business | `/business` | 商业模式、融资材料摘要 |

---

## 6. 信息架构层级

```
rongjingmusic.com/
├── /                    # 新首页（公司 + 四支柱 + 研究）
├── /engine              # Engine 技术页
├── /products
│   ├── /player          # 原 Player 内容（含 Android 下载）
│   ├── /qa              # QA 产品页
│   ├── /master          # Master 产品页
│   ├── /rating          # Rating 产品页
│   └── /supply          # Supply 产品页
├── /research            # Papers + Whitepapers + Benchmarks
├── /partners            # B2B 合作
├── /business            # 公司商业信息
└── /about               # 荣景文川公司信息
```

**规则：** 首页讲公司，产品页讲产品，Player 降级为产品页之一。

---

## 7. 语言与文案原则

1. **首页不再出现 "AI Audio Player" 作为主标题** — 公司 > 产品
2. **每个产品 section 用「产业问题 → Moodify 方案」结构** — 先讲行业痛点再讲能力
3. **量化差异化** — evidence-backed、uncertainty-aware、auditable 这三个词是技术护城河的表达
4. **中英双语保持** — 现有双语结构保留，新增内容同步双语
5. **品牌信念延续** — "每一种声音，都值得被世界听见" 保留为品牌层文案

---

## 8. 实施顺序建议

| 步骤 | 内容 | 优先级 |
|------|------|--------|
| 1 | 首页 Hero 更换为公司定位 | P0 — 一天可完成 |
| 2 | 新增四个产品 section（QA/Master/Rating/Supply） | P0 |
| 3 | Research section 扩展三入口 | P1 |
| 4 | 新建 /engine、/partners 页面 | P1 |
| 5 | Player 内容迁移到 /products/player | P2 |
| 6 | 新建 /business 页面 + whitepaper 留资 | P2 |

---

## 9. 与仓库的联动

- 官网 Research section 链接 → `research/papers/`、`research/whitepapers/` 中的内容
- 官网 Engine 页的架构图 → 与 `docs/MOODIFY_ARCHITECTURE_V1.md` 保持一致
- 官网四支柱文案 → 与 `docs/01_PRODUCT_STRATEGY.md` 保持一致
- Whitepaper 落地页 → 收集 B2B 线索，反哺产业合作
