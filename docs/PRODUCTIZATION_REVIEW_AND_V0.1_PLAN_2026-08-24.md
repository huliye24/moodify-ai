> **STATUS: REJECTED / NOT-AUTHORIZED**
>
> **DATE:** 2026-08-24
>
> **REASON:** The proposed QA product direction is not part of Moodify v1.0 mainline. No Canon Change approval exists. This document is retained as historical decision record only.
>
> **Canon Reference:**
> - `docs/canon/CURRENT_CANON.md §3 不变量 #1`: One external product identity. Ear / QA / Auditory Intelligence Infrastructure do not become a second public product surface.
> - `docs/canon/PRODUCT_BOUNDARY.md §Internal Systems`: Cloud Production is internal. Moodify Ear is internal.
> - `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md §2.2 禁单`: "AI 音乐后处理平台 / Auditory Intelligence Infrastructure / 音频 API 平台 / ACU 计算平台 / Creator Platform" 不再是 Moodify 的首要公共定义。
> - `docs/canon/CANON_CHANGELOG.md 2026-08-19 v1.1`: Public Brand Authority Freeze; 旧 "AI 美化 / 自动 mastering" 退出公共第一叙事。
> - `MOODIFY_PRODUCT_AUDIT.md §4`: `moodify-qa` 已标 DELETE（值 1, 1, 4）。
> - `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`: 本会话 Delta 审计已否决 QA 产品化方向。
> - `docs/reduction/MAINLINE_DECLARATION.md §5.2`: 标 STATUS 头不需 owner 签字，Cursor 可直接执行。
>
> **本文件状态:** 不删除，不修改正文，不移动目录。仅作为历史决策记录保留。v1.0 不进入实施。
>
> **自陈:** 本文件 §3.3 自述"本次产品化方向涉及 Canon 层面的产品身份变更，必须声明 CANON_CHANGE = YES 并由人类批准后记入 CANON_CHANGELOG"。该步骤未发生，本 STATUS 头正式记录该 Canon Change 未获授权。

---

# Moodify 全局审查与产品化规划报告

**日期:** 2026-08-24
**角色:** 技术 CTO / 产品架构师视角
**性质:** 架构审查 + 产品化规划（不含代码实现）
**依据:** 仓库实际扫描 + `docs/canon/*`（CURRENT_CANON v1.1、CURRENT_ARCHITECTURE、REPOSITORY_STATUS）+ W01-P00 云端现实快照

---

## 0. 结论摘要（TL;DR）

1. **Moodify 当前处于 A 阶段（技术验证阶段）的后段**——算法与管线能力扎实（CANONICAL、有测试基线），但没有任何一个面向外部用户的商业闭环在运行。
2. 最大的问题不是缺功能，而是 **"Engine → Product" 的跃迁没有完成**：`engine/` 和 `products/` 是"架构先行、实现滞后"的半成品，真正的产品壳 `apps/web` 定位是创作者音乐社区，与分析产品是两个物种。
3. **30 天内可上线的最小商业闭环 = QA Web v0.1**（上传 → 分析 → 报告 → 历史），复用 `apps/web` 已有的用户体系与 Cloudflare 栈，分析服务复用 `moodify-core-package` 的 FastAPI + engine 门面。
4. ⚠️ 本次产品化方向涉及 Canon 层面的产品身份变更（对外产品面从单一 Music/Player 扩展出 QA 商业产品面），**必须声明 `CANON_CHANGE = YES` 并由人类批准后记入 CANON_CHANGELOG**（见 §3.3）。

---

## 1. 当前状态分析

### 1.1 仓库真实结构（扫描结论）

仓库实际上是**四层平行结构**，而不是一个统一系统：

```text
┌─────────────────────────────────────────────────────────────┐
│ ① moodify-core-package/   真正的分析引擎（CANONICAL）         │
│    audio_io, v01_analyzer, auditory/(BS.1770 LUFS, LRA),     │
│    mrs/, diagnosis/, v01_pipeline, data_factory,             │
│    api/ (FastAPI), cli.py                                    │
│    测试基线: 109 passed (2026-08-08)                          │
├─────────────────────────────────────────────────────────────┤
│ ② engine/   新架构门面层（Intelligence Engine，Phase A/B）    │
│    acoustic_analysis ✅ 有实质代码（facade 委托给①）           │
│    scoring_engine ✅ quality.py + recommendations.py          │
│    music_understanding ⚠️ 仅 commercial_insight.py            │
│    audio_features ❌ 空（仅 __init__）                        │
│    recommendation_engine ❌ 空（仅 __init__）                  │
├─────────────────────────────────────────────────────────────┤
│ ③ products/   产品模块层（qa/master/rating/supply）           │
│    全部为空壳：README + config.yaml + 空 __init__             │
│    qa/ 有清晰的迁移映射表，但 analyzers/scoring/api 均未实现    │
├─────────────────────────────────────────────────────────────┤
│ ④ apps/   应用展示层                                          │
│    web/ = moodify-music（Next.js 16 + vinext + Drizzle + CF） │
│      → 创作者音乐社区：users/creators/tracks/playlists/       │
│        license_intents/support_intents/listen_events          │
│      → 无分析上传、无分析任务、无报告页                          │
│    ear-workbench/ = 内部审查工具（case/evidence/reviews）      │
│    music-android/ = Android 播放器 3.1（对外产品面）           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 云端现实（引用 P00 快照，不虚构）

- 2 台 VPS（LA 核心 4C/8G + 杭州数据工厂 2C/1.6G）
- PolarDB 3 实例空转（19 表 ≈0 数据，核验 BLOCKED）
- **无对象存储**（OSS/S3/R2 均 NOT_PROVISIONED）
- **无云端 AI 推理资源**
- Ear 完整链路（Listen→Judge→Intervene→Verify）**仅存在于仓库代码，云端无生产流量**
- 实际在跑的：静态音乐托管链 + 历史批处理

### 1.3 能力对照表

| 维度 | 现状 | 评级 |
|---|---|---|
| 音频解析/上传 | `audio_io.py` CANONICAL；Web 上传链路 **不存在** | 🔴 |
| LUFS/Loudness | BS.1770-5，CANONICAL，有测试 | 🟢 |
| LRA 动态范围 | EBU Tech 3342，CANONICAL | 🟢 |
| Stereo / M/S | stereo.py + icc.py，CANONICAL | 🟢 |
| 频谱分析 | v01_analyzer band spectrum，CANONICAL | 🟢 |
| HPSS 分离 | 仓库具备，产品化缺失 | 🟡 |
| MRS 评分 | mrs/scoring.py CANONICAL | 🟢 |
| CLI Pipeline | cli.py + v01_pipeline，CANONICAL | 🟢 |
| 分析 API 服务 | FastAPI 壳存在（moodify/api），无生产流量 | 🟡 |
| 用户体系 | apps/web 有 users/auth（beta-login + chatgpt-auth），但与分析无关 | 🟡 |
| 任务队列 | node worker（SQLite 队列，近空），无分析任务类型 | 🟡 |
| 报告展示 | **不存在**（ear-workbench 是内部工具，非用户面） | 🔴 |
| 报告导出 | **不存在**（PDF/JSON 导出无任何实现） | 🔴 |
| 历史作品管理 | apps/web 有 tracks 表，可复用模式但无分析资产 | 🟡 |
| 支付/计费 | support_intents 有支付意图表结构，无真实支付 | 🔴 |
| 对象存储 | 未开通（音频文件存本地磁盘） | 🔴 |

### 1.4 技术债务

1. **巨型单仓库 + 平行身份堆积**：根目录 60+ 顶级目录（含 `补丁包/`、`审查包/`、`工程经验层/` 等工作包），新人（和 AI agent）无法从目录结构推断真实主链。
2. **三套"引擎"表述并存**：moodify-core-package（真实）、engine/（门面）、文档中的 Intelligence Platform（愿景）——迁移只完成了 acoustic_analysis 等局部。
3. **两套产品定位并存于代码**：Canon 说对外是 Music/Player（PLAY），apps/web 却做的是创作者社区；本次又要引入 QA 商业产品面——产品身份需要一次正式裁决。
4. **数据库战略未定**：Drizzle/SQLite（apps/web）vs PolarDB（云端空转）vs 杭州 SQLite（批处理 6.5GB），三个数据孤岛。
5. **无 CI/CD 产品发布链**：交付依赖 APK/artifacts 手工包。

### 1.5 风险点

| 风险 | 等级 | 说明 |
|---|---|---|
| Canon 冲突 | 高 | QA 商业产品面与"一个对外产品身份/PLAY 优先"不变量冲突，未走 Canon 变更流程就开发会破坏仓库治理 |
| 计算资源 | 高 | 分析是 CPU 密集任务，LA VPS 4C/8G 单机并发能力有限，需队列限流 |
| 存储缺位 | 高 | 无对象存储，音频上传后无处可靠存放，数据丢失风险 |
| 付费合规 | 中 | 涉及支付需要 ICP/主体资质、微信支付商户等，前置周期可能超过开发周期 |
| 单点人力 | 中 | 全部认知集中在少数文档与个人，bus factor 低 |

---

## 2. 阶段判断

**结论：A. 技术验证阶段（后段，A⁺）**

判定标准（自证不虚构）：

| 阶段定义 | Moodify 是否达到 |
|---|---|
| A 技术验证：核心算法可重复运行、有测试与证据 | ✅ 109 tests、data_factory 10/10、calibration_reports |
| B MVP 产品：有外部用户完成一次完整价值闭环 | ❌ 无任何外部用户完成"上传→分析→获得报告" |
| C 商业产品：有付费用户、计费、留存 | ❌ 无支付、无配额、无商业用户 |
| D 平台：API/生态/多租户 | ❌ products/ 四模块空壳 |

**为什么不是 B**：apps/web 的用户体系服务于音乐播放社区，与分析能力**零集成**——用户在产品里无法触达任何一次分析。Engine→Product 的"最后一公里"（上传、任务、报告、导出）完全缺失。

**A→B 的门槛（定义清楚才算跃迁）**：第一个非内部用户，在公网上，完成 注册→上传→分析→查看报告→再次使用 的完整闭环。

---

## 3. 产品战略定位

### 3.1 定位陈述

```text
现在:  Audio Analysis Engine（能力在仓库，价值不可被用户触达）
目标:  AI Music Intelligence Platform
       = 一个 Intelligence Engine（复用）
       × 多个产品面（qa / master / rating / supply ...）
       × 第一个商业产品 = QA（AI 音乐质检报告）
```

选择 QA 作为第一个产品面的理由：

1. **能力最全**：LUFS/LRA/Stereo/频谱/MRS 全部 CANONICAL，是四个产品模块中唯一"只差组装"的；
2. **价值感知最快**：上传歌曲 → 30 秒出专业报告，价值感即时、可演示、可传播；
3. **变现路径最短**：音乐人/工作室/发行方对质检付费意愿成熟（对标 LANDR、eMastered、iZotope 的验证过市场）；
4. **反哺引擎**：每一份报告都是 Asset Loop（Production Case → Evidence → Rule Update）的真实生产数据。

### 3.2 目标用户

- 独立音乐人 / AI 音乐创作者（Suno/Udio 用户的"发行前体检"需求）
- 小型工作室 / 混音师（批量质检）
- 音乐版权/发行方（资产评级，P2 接 rating 模块）

### 3.3 ⚠️ Canon 变更声明（必须先行）

本次规划把 QA 提升为对外商业产品面，与 CURRENT_CANON v1.1 的不变量 **"一个对外产品身份（Music/Player，PLAY 优先）"** 冲突。

按 AGENTS.md 的 Canon Change Rule：

- `CANON_CHANGE = YES`
- **why**: 引擎能力已超过单一播放产品可承载的范围；商业化需要独立价值闭环
- **affected files**: CURRENT_CANON.md、PRODUCT_BOUNDARY.md、REPOSITORY_STATUS.md、CANON_CHANGELOG.md
- **建议裁决**: 对外产品面扩展为「Moodify Music/Player（播放）+ Moodify QA（分析报告）」双产品面，共享同一品牌与用户体系
- **migration/rollback**: Canon 变更仅影响文档权威层，不删改代码，可随时回退

此项需要人类明确批准后记入 CANON_CHANGELOG，**批准前不应启动 P0 开发**（开发可以准备，但不得以"已定案产品"名义合并）。

---

## 4. Web v0.1 产品架构

### 4.1 产品闭环（用户视角）

```text
注册/登录 → 上传歌曲 → 等待分析(实时进度) → 查看 Audio Intelligence Report
     ↑                                              ↓
     └── 再次处理新版本 ← 下载 PDF/JSON ← 保存到 My Works
```

### 4.2 页面与职责

| 页面 | 路由（建议） | 目标 | 核心元素 |
|---|---|---|---|
| 首页 | `/` | 30 秒让用户明白"为什么需要 Moodify" | 上传入口前置（先体验后注册）、示例报告、平台标准对照（Spotify -14 LUFS 等） |
| Upload | `/qa/upload` | 上传 + 进度透明 | 拖拽上传、格式校验（wav/mp3/flac）、大小限制、任务状态轮询 |
| Analysis | `/qa/report/[id]` | 专业报告即价值交付 | Overall Score（MRS）、Loudness、Dynamics、Stereo、Frequency、Problems、Suggestions、平台合规对照 |
| Works | `/qa/works` | 音乐资产管理 | 曲目列表（Score 摘要）、版本对比（v1 vs v2 分数变化）、再分析入口 |
| Export | 报告页内 | 变现/传播钩子 | PDF 报告（带品牌水印）、JSON 数据、（P1）处理后的音频 |
| 定价 | `/pricing` | 转化 | Free/Creator/Studio 三档 + 免费次数说明 |

### 4.3 报告信息架构（Analysis 页）

```text
Audio Intelligence Report
├── Overall Score        MRS 总分 + 不确定度区间 + 评级(A/B/C/D)
├── Loudness             Integrated LUFS / LRA / True Peak vs 目标平台
├── Dynamics             DR、Crest Factor、压缩痕迹提示
├── Stereo               相关性、M/S 平衡、相位风险
├── Frequency            频段能量分布、共振/缺失频段标注
├── Problems             缺陷清单（削波、底噪、相位、失衡）按严重度排序
└── Suggestions          可执行改进建议（每条对应一个 Problem）
```

---

## 5. 技术架构调整建议

### 5.1 总原则

- **不新建第二套系统**：复用 `apps/web`（产品壳）+ `moodify-core-package/api`（分析服务）+ engine 门面（长期归位）。
- **分层边界**：`engine/` 纯函数无副作用 → `products/qa` 编排（标准、配额、报告 schema）→ `apps/web` 展示与用户。
- **MVP 优先"能闭环"，架构允许"后归位"**：短期内 analysis 路由可以调用 core-package 能力，中期把实现下沉进 engine/products。

### 5.2 目标架构（v0.1）

```text
用户浏览器
   │  HTTPS
   ▼
apps/web (Next.js 16 / vinext, Cloudflare)         ← 产品壳
   ├── /qa/* 页面 + /api/v1/qa/* 路由
   ├── 认证（复用现有 users 表）
   └── Drizzle: users / tracks / analysis_jobs / reports
   │                    │ 任务入队
   ▼                    ▼
分析服务 moodify-api (FastAPI, LA VPS)             ← 能力服务
   ├── /analyze 提交 / /jobs/{id} 状态 / /reports/{id}
   ├── engine.acoustic_analysis (facade → core-package)
   └── CPU 限流：单并发 + 队列
   │
   ▼
对象存储 Cloudflare R2                              ← 资产层
   ├── uploads/ (原始音频)
   └── reports/ (JSON + PDF)
```

### 5.3 关键技术决策（建议）

| 决策点 | 建议 | 理由 |
|---|---|---|
| 产品壳 | 扩展 apps/web，新增 `/qa` 命名空间 | 已有 Next.js 16 + auth + Drizzle + CF 栈；避免第二个前端 |
| 用户体系 | 复用 users 表 + 新增 qa 配额字段 | 不做第二套账号 |
| 分析服务 | moodify-api FastAPI 部署 LA VPS | 已存在，补 analysis 路由即可；Python 生态（librosa/pedalboard）不可替代 |
| 任务队列 | DB 表 + worker 轮询（先不做 Redis/Celery） | VPS 单机规模足够；云端已有 node worker 经验 |
| 对象存储 | Cloudflare R2 | apps/web 已在 CF 栈；R2 免出口流量费；LA VPS 经 CF Tunnel 可达 |
| 数据库 | MVP: apps/web 现有 SQLite/D1；P1: 评估 PolarDB PG 实例收编 | 避免为 MVP 提前搬库 |
| 报告 PDF | 服务端渲染（Playwright/WeasyPrint）或前端 print-to-PDF | P1 再做，MVP 先 HTML 报告 + JSON 导出 |
| 计费 | P1 接微信支付/Stripe（视主体资质） | 合规前置期长，P0 用"免费次数"硬编码 |

### 5.4 数据模型增量（Drizzle，示意）

- `analysis_jobs`：id / userId / trackVersionId / status(queued/running/succeeded/failed) / progress / engine_version / createdAt
- `analysis_reports`：id / jobId / reportSchemaVersion / reportJson(object key) / overallScore / createdAt
- `users` 增量：qaQuotaUsed / qaQuotaLimit（P0 硬编码，P1 接计费）

---

## 6. 商业化设计

| | Free | Creator ¥69/月 | Studio ¥999/月 |
|---|---|---|---|
| 分析次数 | 3 次/月 | 50 次/月 | 500 次/月 + API |
| 报告 | 基础 HTML 报告 | 完整报告 + PDF 导出 + AI 建议 | 完整报告 + 批量 |
| 历史作品 | 最近 5 首 | 无限 | 无限 + 项目分组 |
| 版本对比 | ❌ | ✅ | ✅ |
| 批量上传 | ❌ | ❌ | ✅ |
| 团队账号 | ❌ | ❌ | ✅（席位制） |
| API | ❌ | ❌ | ✅（rate-limited key） |

定价锚点：LANDR ~$9.99/月（mastering）、eMastered $19/月、iZotope 高价买断。QA 报告作为差异化入口，Creator 定价 ¥69 卡在"一杯咖啡以上、一次混音以下"的决策区间。

转化漏斗设计：未登录可上传 1 次体验（报告打码部分指标）→ 注册解锁完整报告 → 次数用尽转 Creator。

---

## 7. 30 天开发路线（MVP 最小实现路径）

### P0 必须（Day 1–21，上线门槛）

| # | 任务 | 产出 |
|---|---|---|
| P0-1 | Canon 变更批准 + CANON_CHANGELOG 记录 | 双产品面裁决文档 |
| P0-2 | R2 存储开通 + presigned 上传链路 | 上传的音频可靠落桶 |
| P0-3 | apps/web `/qa` 命名空间 + 认证打通 | 登录态下的 QA 入口 |
| P0-4 | analysis_jobs 队列表 + moodify-api 分析路由 + worker | 上传→分析→报告 JSON 全链 |
| P0-5 | 报告页（Score/Loudness/Dynamics/Stereo/Frequency/Problems/Suggestions） | 价值交付页 |
| P0-6 | Works 页 + 报告历史 | 闭环最后一环 |
| P0-7 | 免费配额硬编码 + 次数用尽提示 | 商业化伏笔 |
| P0-8 | 部署：LA VPS 分析服务 + CF 路由 + 域名 | 公网可访问 |

### P1 重要（Day 22–30，转化与合规）

- PDF 报告导出（品牌化模板）
- JSON 数据导出
- 版本对比（v1 vs v2 分数 delta）
- 定价页 + 支付通道接入（依赖主体资质，可能顺延）
- 邮箱注册/验证（如当前仅第三方登录）
- 基础埋点（上传→报告→导出漏斗）

### P2 后续（30 天后）

- AI Mastering（master 模块，复用 v01_pipeline + pedalboard_chain）
- 开放 API（Studio 档）
- rating / supply 产品面
- 批量上传 + 团队协作
- engine/ 剩余模块迁移归位（audio_features、recommendation_engine）

---

## 8. 第一批 Coding Task 列表（P0-2 ~ P0-5 拆解）

每个任务执行前必须回答四问（商业问题 / 所属模块 / 扩展方式 / 架构影响）：

**T1. R2 存储接入与上传 API**
- 商业问题：无可靠存储则上传闭环不存在；对象存储是一切资产的地基
- 模块：apps/web 基础设施（不属于任何产品模块，属平台层）
- 扩展：未来 master/rating 的音频资产走同一存储抽象
- 架构影响：低；纯增量，不触碰现有 tracks 链路

**T2. analysis_jobs 队列表 + 状态机**
- 商业问题：分析是异步 CPU 任务，用户必须看到进度才不会流失
- 模块：平台层（apps/web db + moodify-api worker）
- 扩展：状态机设计需兼容未来 master 处理任务（同一 queue 表 + jobType 字段）
- 架构影响：中；引入第一个跨服务任务协议，需定义状态枚举为 contract

**T3. moodify-api 分析路由（/analyze、/jobs/{id}）**
- 商业问题：把 CANONICAL 的分析能力第一次暴露为产品服务
- 模块：products/qa（路由实现落在 core-package api，长期归位 products/qa/api）
- 扩展：报告 schema 加 version 字段，引擎升级不破坏历史报告
- 架构影响：中；遵守 engine 门面边界，不直接在路由里写分析逻辑

**T4. 报告页 UI（Audio Intelligence Report）**
- 商业问题：报告就是产品本体——价值感知 100% 发生在这一页
- 模块：products/qa 的展示面
- 扩展：组件化（ScoreCard/LoudnessPanel/...），master 产品未来复用
- 架构影响：低；纯前端，消费 T2/T3 的 contract

**T5. Works 页 + 报告历史**
- 商业问题：留存依赖资产沉淀——用户的歌曲历史就是离开成本
- 模块：products/qa
- 扩展：表结构预留版本对比所需字段
- 架构影响：低

**T6. 免费配额与升级引导**
- 商业问题：无配额则无付费理由
- 模块：平台层（用户配额）× products/qa（引导 UI）
- 扩展：P1 计费系统只替换配额来源（硬编码 → 订阅状态）
- 架构影响：低

---

## 9. 执行原则（对本仓库所有后续开发的约束）

1. ❌ 不因"看到一个功能"而写代码——每个任务先过 §8 四问。
2. ❌ 不创建第二套 authoritative state machine / Job authority / 产品身份。
3. ❌ 不把内部复杂度（Ear/HPSS/Evidence）暴露为卖点——对外永远是"上传→报告"。
4. ✅ 任何 Canon 边界任务先声明 `CANON_CHANGE`。
5. ✅ 每次开发识别：canonical / experimental / legacy，并保留证据与可复现性（Asset Loop）。
6. ✅ 未验证的能力不写成已运行（R6/R10）——本报告所有云端现状均引用 P00 快照。

---

*本报告为规划文档，不是 Canon；涉及产品身份的裁决（§3.3）需人类批准后生效。*
