# Moodify Cloud Production v0.1 — Internal Entry

**状态:** INTERNAL（不构成对外产品面；不替代 `docs/canon/CURRENT_ARCHITECTURE.md` 或 `docs/canon/INTERNAL_SYSTEMS.md`）
**日期:** 2026-08-24
**作者:** Reduction Execution 001（Delta 报告 + MAINLINE_DECLARATION 派生）
**CANON_CHANGE:** NO（本文件是内部 entry；Cloud Production System 角色已在 Canon v1.0 确立，本文件不引入新 authority）
**执行状态:** 只描述现状 + 内部规划目标；不实施任何云端修改 / 数据库迁移 / API 重设计

---

## 0. 重要约束（不可越界）

1. **不构成对外产品面。** Cloud Production 是 `INTERNAL_SYSTEMS.md §2` 已确立的内部生产系统。本 entry 不把它包装为 "AI Platform / Audio API Platform / Enterprise Infrastructure" — 这些都是 `PUBLIC_BRAND_CONSTITUTION.md §2.2` 禁单。
2. **不替代 `CURRENT_ARCHITECTURE.md`。** 现状描述必须以 `CURRENT_ARCHITECTURE.md §1` P00 扫描为准，不写未验证能力。
3. **不创建第二 authoritative state machine。** `INTERNAL_SYSTEMS.md §3` 4 个 state machine authority（`workflow_engine LEGACY` / `node CANONICAL` / `data_factory CANONICAL` / `reconstruction_factory EXPERIMENTAL`）统一方案 `HUMAN_DECISION_REQUIRED`（CD-015）。本 entry 不引入第 5 个。
4. **data authority 变更需 `CANON_CHANGE = YES`。** 当前 Music data authority 不是单一 SQLAlchemy（Drizzle schema 与 SQLAlchemy 双 schema 漂移）。任何把 "Music data model 是唯一 authority" 写成既成事实的话必须改为 `HUMAN_DECISION_REQUIRED`。
5. **Player Delivery 不暴露内部状态。** 这是 Canon 现状，不是 v0.1 新目标（见 `apps/web/app/listen/page.tsx:11` 与 §0 不变量 #3）。

---

## 1. Purpose

定义 Moodify v1.0 云端生产闭环的**内部目标**与**已验证现状**之间的边界。

**它是什么:**

> Moodify Player 背后的音乐资产生产系统。负责把外部输入的源音频,经 Moodify Ear 与受控处理,产出可被 Player 消费的 `READY` 资产版本。
>
> 输入: 源音频（upload 或 curate）。
> 输出: `READY` 音频版本 + 必要 metadata。
> 不输出: 任何内部状态、LUFS / 频段 / 工程参数、unverified asset。

**它不是:**

- AI Platform
- Audio API Platform
- Enterprise Infrastructure
- 公开第三方 API 平台
- Creator Platform
- Marketplace

---

## 2. Architecture — Already Running（已运行,来自 P00 / CURRENT_ARCHITECTURE.md）

```text
[已运行 路径 — P00 扫描 2026-08-17 验证]

  LA 103.144.246.242 (亿速云, 核心节点 4C/8G/98G)
   ├── nginx :80 (三域名)
   ├── cloudflared 隧道 (rongjingmusic.com 等)
   ├── moodify-api :8000 (Ear FastAPI, 127.0.0.1)
   ├── moodify-music :3100 (node vinext 平台)
   ├── moodify-music-bff :8100
   ├── moodify-worker (SQLite 队列, 近空)
   └── docker: moodify-audiolla (:18080→8000, lalal.ai 代理)

  杭州 120.55.191.146 (阿里云, 2C/1.6G/40G)
   ├── moodify-api :8000 (公网, service-key 鉴权)
   ├── moodify-data-worker (moodify-node + 4 timers)
   └── /var/lib/moodify (SQLite + 历史批处理 6.5GB, 10 曲 pilot SUCCEEDED)

  PolarDB (3 实例, 直接核验 BLOCKED — 内容引用同日黑箱调查)
   ├── MySQL 8.0.13  172.27.118.106 (空壳)
   ├── MySQL 8.0.18  172.27.118.104 (moodify_dev 19 表 ≈0 数据)
   └── PG 16.14      101.133.107.206 (在线未用)

  OSS / S3 / R2: NOT_PROVISIONED
  云端 AI 推理: 无 (无 GPU, 无模型 serving)
```

**真实主链（已运行,非理想图）:**

```text
[对外 — 静态音乐托管链]
  网站 → nginx → music-bff / music-platform → music-media 音频 → 浏览器 / App 播放

[对内 — 数据工厂批处理链, 历史运行]
  杭州 worker → /var/lib/moodify (10 曲 pilot SUCCEEDED)

[对内 — 完整 Ear 链路, 仅仓库代码]
  Listen → Judge → Intervene → Verify 云端无生产流量
```

**音频资产部署位置（已运行, Listen Demo v0.1）:**

```text
  /opt/moodify/music-media/audio/cadeau10-album1/          ← Original (5 wav, deployment asset, not in git)
  /opt/moodify/music-media/audio/cadeau10-album1-moodify/   ← Moodify (5 wav, deployment asset, not in git)
  https://play.rongjingmusic.com/audio/cadeau10-album1[/-moodify]/<file>.wav  ← 公开 URL (UNVERIFIED 域名)
```

> **R6/R10 规则（来自 `CURRENT_ARCHITECTURE.md` 顶部）:** 本节只记录已由运行时证据支持的现状。任何"未验证不写成已运行"。

---

## 3. Architecture — Planned but Unverified（v1.0 目标,未实施）

> 本节是**目标路径**。以下目标与既有 `MOODIFY_PRODUCT_AUDIT.md §4 + §6.3` 一致,但**未实施**,任何实施必须先做 §0 的 P00 核验 + 30 天观测。

```text
[目标路径 — v1.0, HUMAN_DECISION_REQUIRED]

  Source / Curate Upload (Cloud-prepared Track)
     │
     ▼
  Storage (original / processed / preview / waveform / metadata)
     │
     ▼
  Worker (Queue + Audio processing pipeline)
     │
     ▼
  Moodify Ear (Internal — INTERNAL_SYSTEMS.md §1)
     │
     ▼
  Verification
     │
     ▼
  READY Audio Version (Track Version in Music data authority)
     │
     ▼
  Player (apps/web + apps/music-android)
```

### 3.1 Storage（目标）

负责:
- original audio
- processed audio (Moodify 处理后)
- preview
- waveform
- metadata

**现状:** NOT_PROVISIONED（OSS / S3 / R2 均未配置；`CURRENT_ARCHITECTURE.md §1` 显式记录）。
**目标位置:** `HUMAN_DECISION_REQUIRED`（CD-011 后续：LA 本地磁盘 / 阿里云 OSS / Cloudflare R2 候选均未决策）。
**不实施任何存储迁移。** 不动 `moodify-music-package/.../bff` 写路径。

### 3.2 Database（目标, 但 data authority 未决）

**当前 Music data authority 现状**（来自 `MOODIFY_PRODUCT_AUDIT.md §5.1 D`）:

| 路径 | 状态 | 说明 |
|---|---|---|
| `moodify-music-package/models.py` + Alembic | 已被文档定义为 Music data authority（执行前需再核验部署） | `MOODIFY_PRODUCT_AUDIT.md §4 表` |
| `apps/web/lib/db/schema.ts` (Web Drizzle) | 与 SQLAlchemy 重复（users / tracks / social / intents），状态枚举漂移 | `MOODIFY_PRODUCT_AUDIT.md §4 表` MERGE 候选 |
| `moodify-qa/qa_storage.db` | DELETE 候选（Delta D-1） | 与本 entry 无关 |

**v1.0 激活表（目标,非既成事实）:**

```
tracks
track_versions
play_events
favorites
```

**约束（不可越界）:**
- 这不是既成事实。这是 `MOODIFY_PRODUCT_AUDIT.md §6.3 + REDUCTION_PLAN.md Phase 3 §3.3` 的目标。
- 删除 `apps/web/lib/db/schema.ts` 与 SQLAlchemy 合并属于 `CANON_CHANGE = YES`（`CURRENT_CANON.md §4` + `MOODIFY_PRODUCT_AUDIT.md §5.1 D`）。
- 未实施任何 schema 合并 / migration / Drizzle 删除。

### 3.3 Worker（目标）

**当前 Worker 现状**（来自 `CURRENT_ARCHITECTURE.md §1 + INTERNAL_SYSTEMS.md §3`）:

| Worker | 状态 | 依据 |
|---|---|---|
| `moodify-node`（LA + 杭州） | CANONICAL（云端队列实跑） | P00 TT-009 |
| `moodify-data-worker`（杭州 4 timers） | 实跑，10 曲 pilot SUCCEEDED | `CURRENT_ARCHITECTURE.md §1` |
| `data_factory` | CANONICAL（pilot 10/10） | P00 TT-008 |
| `reconstruction_factory` | EXPERIMENTAL | P00 TT-013 |
| `moodify/orchestration/workflow_engine.py` | LEGACY | `INTERNAL_SYSTEMS.md §3` |
| 单一 authoritative state machine 统一 | `HUMAN_DECISION_REQUIRED` | CD-015 |

**目标处理流程（与 INTERNAL_SYSTEMS.md §2 一致）:**

```text
Upload → Queue → Analyze → Process → Verify → Ready
```

**注意:** `INTERNAL_SYSTEMS.md §2` 完整链路是:

```
Intake → Identify → Analyze → Stem → Judge → Intervene
      → Preset Decision → Render → Verify → Evidence → Delivery
```

本 entry 的简化版 `Upload → Queue → Analyze → Process → Verify → Ready` 只是流水线层;不引入新状态机 authority。

### 3.4 Player Delivery（Canon-aligned, 已确立）

**只接收:** `READY` 资产版本。

**不暴露（这是 Canon 现状,不是新目标）:**

- LUFS / 频段 / 评分等 Tier C 工程字段（`PUBLIC_BRAND_CONSTITUTION.md §9 Tier C + §13 Test D`）
- 波形 / 工程参数（用户必须知道的复杂度）
- 内部状态（`CURRENT_CANON.md §3 不变量 #3` "内部可以复杂,复杂度由 Moodify 承担,不转嫁给用户"）
- unverified asset

**已运行验证:** `apps/web/app/listen/page.tsx:11` 已写 "本页不展示 LUFS / 频段 / 评分等 Tier C 工程字段"。`apps/web/app/evidence/page.tsx` 注释引用 §9 Tier B + §11。

---

## 4. 与现有 Canon / 治理文件的关系

| 文件 | 关系 |
|---|---|
| `docs/canon/CURRENT_CANON.md` | **第 3 级**权威；本 entry 不替代它；所有 v1.0 目标若与它冲突必须走 `CANON_CHANGE` 流程 |
| `docs/canon/CURRENT_ARCHITECTURE.md` | **已验证现状**权威；本 entry §2 直接引用；理想架构不写 |
| `docs/canon/INTERNAL_SYSTEMS.md` | **内部系统**权威；本 entry §3.3 引用；不引入新系统 |
| `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | **最高 Public Brand 主题权威**；本 entry §1 引用其禁单；不引入新命名 |
| `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` | 本会话 Delta 审计；§2 D-1 已否决 QA 产品化方向；本 entry 不引入 QA / Platform 命名 |
| `docs/reduction/MAINLINE_DECLARATION.md` | 本会话主线声明；§3 架构图为本 entry §2 的简化版来源 |
| `MOODIFY_PRODUCT_AUDIT.md` §6.3 | v1.0 MVP 架构参考；本 entry §3 直接对齐 |
| `REDUCTION_PLAN.md` Phase 3 §3.3 | data authority 合并规划；本 entry §3.2 引用其约束 |
| `INTERNAL_SYSTEMS.md §2` | Cloud Production System 角色级权威；本 entry §3.3 引用其完整链路 |

---

## 5. 下一阶段（Cloud Production Implementation 001）触发条件

按 `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀 6 项` + `CURRENT_ARCHITECTURE.md R6/R10`：

1. P00 重新核验当前 LA / 杭州部署（不是引用 2026-08-17 快照）。
2. PolarDB 核验（当前 BLOCKED）。
3. OSS / R2 选型决策（CD-011 后续）。
4. Music data authority 单一化决策（CD-015 + `CANON_CHANGE = YES`）。
5. Worker / 队列 authority 决策（CD-015）。
6. owner 签字 + 30 天观测。

未满足上述任一条件时,**不实施任何 Cloud Production 代码 / 数据库 / API 修改**。

---

**报告结束。等待 Cloud Production Implementation 001 触发条件满足。**