# Moodify v1.0 Mainline Architecture — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** 主线架构图（不是新理想图；只展示**已运行 + 已验证 + 2026-08-24 已有代码的 Canon-aligned 落地**）；为 Phase 4 Web + Cloud 开发提供工程入口。
**权威：** 引用 `CURRENT_ARCHITECTURE.md §1`（云端现状）+ `INTERNAL_SYSTEMS.md`（内部系统）+ `PUBLIC_BRAND_CONSTITUTION.md §9 Tier`（公开语言）+ `MOODIFY_PRODUCT_AUDIT.md §6.3 MVP Architecture` + `PRODUCT_BOUNDARY_V1.md §1 KEEP` + Delta §1-2。
**CANON_CHANGE：** `NO` —— 本文件**复用** Canon / 既有审计已确立的架构事实，不引入新系统拓扑。
**执行状态：** 仅声明。**未修改、删除、移动任何业务代码、目录或既有文档。**

---

## 1. 目标产品树

```text
                            ┌──────────────────────────────────────┐
                            │              Moodify                 │
                            │  (Moodify Music / Moodify Player)    │
                            │   唯一对外产品身份 (Canon 不变量 #1)  │
                            └──────────────┬───────────────────────┘
                                           │
                            ┌──────────────▼───────────────────────┐
                            │       AI Listening Platform          │
                            │   Listen. Then Play. (Brand §2)      │
                            └──────────────┬───────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                                                         │
   ┌──────────▼────────────┐                                ┌───────────▼──────────┐
   │       Player          │                                │     Cloud Engine     │
   │   对外感知（用户可见） │                                │  内部系统（不可见）   │
   │   Public Brand §11    │                                │  Internal Systems    │
   │   "Play." — 终点      │                                │  "Listen." — 起点    │
   └──────────┬────────────┘                                └───────────┬──────────┘
              │                                                         │
   ┌──────────┼────────────┐                                  ┌─────────┼──────────────┐
   │                       │                                  │                        │
┌──▼────────┐      ┌───────▼────────┐                ┌────────▼─────────┐     ┌───────▼────────┐
│   Web     │      │    Android     │                │  Audio           │     │  Cloud         │
│  Player   │      │    Player      │                │  Intelligence     │     │  Production    │
│           │      │                │                │  (Ear)            │     │                │
│ apps/web/ │      │ apps/music-    │                │                   │     │ Intake→…→      │
│ + listen/ │      │  android/      │                │ moodify-core-     │     │ Render→        │
│ + evidence│      │  (release      │                │  package/src/     │     │ Verify→        │
│ + library │      │   workflow)    │                │  moodify/         │     │ Evidence→      │
│           │      │                │                │                   │     │ Delivery       │
└─────┬─────┘      └────────┬───────┘                │ v01_pipeline      │     └───────┬────────┘
      │                     │                        │ data_factory       │             │
      └────────┬────────────┘                        │ era_diagnostic     │             │
               │                                     │ identity_guard     │             │
               │                                     │ reconstruction_    │             │
               │                                     │  objective         │             │
               │                                     └─────────┬──────────┘             │
               │                                               │                        │
               │                                               └────────────┬───────────┘
               │                                                            │
       ┌───────▼──────────┐                                       ┌─────────▼──────────┐
       │   Music BFF      │                                       │   Music Data        │
       │ (moodify-music-  │◄──────────────────────────────────────┤   Authority         │
       │  package/.../bff)│                                       │ (moodify-music-     │
       │ 唯一公开 API     │                                       │  package/models.py  │
       │                  │                                       │  + Alembic)         │
       │ catalogue /      │                                       │                    │
       │ track /          │                                       │ tracks / track_     │
       │ playback /       │                                       │  versions /         │
       │ favorite /       │                                       │ favorites /         │
       │ recent-play      │                                       │ play_events         │
       └──────────────────┘                                       └────────────────────┘
```

---

## 2. 模块职责（每条带 Canon Evidence）

### 2.1 Moodify（唯一对外产品身份）

| 字段 | 内容 | Canon Evidence |
|---|---|---|
| 身份 | Moodify Music / Moodify Player | `CURRENT_CANON.md §1` + `PRODUCT_BOUNDARY.md §External Product` |
| 第一阶段用户动作 | PLAY | `CURRENT_CANON.md §1` + `PRODUCT_BOUNDARY.md §Primary user action` |
| 品牌信念 | 每一种声音，都值得被世界听见。 / Every voice deserves to be heard. | `CURRENT_CANON.md §1` + `PUBLIC_BRAND_CONSTITUTION.md §1.2` |
| 产品原则 | Listen. Then Play. | `CURRENT_CANON.md §1` + `PUBLIC_BRAND_CONSTITUTION.md §2` |
| 公开证明顺序 | Belief → Sound → Play → Proof → Explanation → Technology | `PUBLIC_BRAND_CONSTITUTION.md §11` |
| 站点职责 | `rongjingmusic.com` = Product Home；`rongjingwenchuan.com` = Company Home；`rongjinwenchuan.xyz` = 过渡 Player；`play.rongjingmusic.com` = UNVERIFIED | `CURRENT_CANON.md §3 不变量 #7` + `PUBLIC_BRAND_CONSTITUTION.md §7` |

**不属于该模块的事：**

- 不得引入第二公开产品身份（QA Web v0.1 / QA Desktop / Pulse / Ear Workbench 作为对外产品）。
- 不得让内部能力（Ear / Auditory Intelligence / ACU / API / Creator Platform）出现在首屏 CTA。
- 不得使用 `PUBLIC_BRAND_CONSTITUTION.md §9 Tier D` 禁词作为首屏叙事。

### 2.2 AI Listening Platform（产品原则）

| 字段 | 内容 | Canon Evidence |
|---|---|---|
| 原则 | Listen. Then Play. — 系统先理解、准备、验证，再把复杂度隐藏在播放之前 | `PUBLIC_BRAND_CONSTITUTION.md §2.1` + §2 |
| 视觉原则 | Sound first. Large whitespace. One focal action. No dashboard aesthetics. | `PUBLIC_BRAND_CONSTITUTION.md §10` |
| 公开语言 | Tier A（核心公开）+ Tier B（次级公开，用户理解后） | `PUBLIC_BRAND_CONSTITUTION.md §9` |

**不属于该模块的事：**

- 不展示工程预设（不暴露 LUFS / 频段 / preset 选择器）。
- 不强制用户理解"为什么要 Listen"。
- 不把 Listen Demo 之外的内部能力（research / benchmark / MAMSE）作为首页证明。

### 2.3 Player（对外感知 / 用户可见）

#### Web Player

| 项 | 内容 | Canon Evidence |
|---|---|---|
| 工程 | `apps/web/`（含 `app/page.tsx` 主屏 + `app/listen/` + `app/evidence/` + 必要 `/library` + BFF 路由） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `CURRENT_ARCHITECTURE.md §1` + Delta §1.2 |
| 路由 | 收敛到 3-4 个：`/`（主屏）、`/listen`、`/t/[id]`（兼容期内）、`/library`（抽屉内） | `MOODIFY_PRODUCT_AUDIT.md §6.3` + `REDUCTION_PLAN.md Phase 3 §3.2` |
| 公开证明顺序 | Belief → Sound → Play → Proof → Explanation → Technology | `PUBLIC_BRAND_CONSTITUTION.md §11` |
| 听感证明 | Listen Demo v0.1 落地链（`apps/web/app/listen/` + `apps/web/app/evidence/` + `runbook_listen_demo_v0.1.{sh,README.md}`） | Delta §1.1 + §1.2 KEEP |
| 公共导航 | Play / Download / About；最小化 | `PUBLIC_BRAND_CONSTITUTION.md §8` |
| 数据 | Music BFF 唯一来源；不直连 Music data authority | `MOODIFY_PRODUCT_AUDIT.md §5.1 D` |

**不属于该模块的事：**

- 不展示 Creator Studio / drafts / `/c/[handle]` / playlists / console / inbox / evidence 等 creator / 创作控制台 / 公共证据仪表盘路由。
- 不暴露 `apps/web/lib/db/schema.ts`（Drizzle）作为平行 schema；最终由 Music data authority 单一权威生成类型 / BFF contract。
- 不打包音频到 Git（仅 checksums/manifest）。
- 不暴露 Moodify Data API（与 BFF 平行层）。

#### Android Player

| 项 | 内容 | Canon Evidence |
|---|---|---|
| 工程 | `apps/music-android/`（CI release workflow 唯一指向） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + §2.3 |
| 路由 | 与 Web Player 共用同一 contract；catalogue / playback / favorite / recent-play | `MOODIFY_PRODUCT_AUDIT.md §6.3` |
| 后台播放 | MediaSession + 锁屏控制 | `MOODIFY_PRODUCT_AUDIT.md §6.2 #4` |
| 弱网 | 本地缓存 + 过期 URL / range / 错误恢复 | `MOODIFY_PRODUCT_AUDIT.md §6.2 #8` |
| 数据 | Music BFF 唯一来源 | 同 Web Player |

**不属于该模块的事：**

- `apps/android/` 不构成第二 Android 工程；迁移必要能力（缓存 / MediaSession / 本地化）后整工程退役（`MOODIFY_PRODUCT_AUDIT.md §5.1 A` + `REDUCTION_PLAN.md Phase 3 §3.1`）。
- 不为 creator / license / support 暴露新 surface。
- 不暴露内部状态机或工程预设。

### 2.4 Cloud Engine（内部系统 / 用户不可见）

#### Audio Intelligence（Ear / Auditory Intelligence）

| 项 | 内容 | Canon Evidence |
|---|---|---|
| 角色 | 内部听觉智力层；listen → represent → judge → evidence → uncertainty → learn → verify → controlled intervention | `CURRENT_CANON.md §2` + `INTERNAL_SYSTEMS.md §1` |
| 工程 | `moodify-core-package/src/moodify/` —— `v01_pipeline`（CANONICAL）+ `data_factory`（CANONICAL）+ 重建系列子包（FREEZE） | `INTERNAL_SYSTEMS.md §1` + `REPOSITORY_STATUS.md` Capability Table |
| 资产 | era_diagnostic / identity_guard / reconstruction_objective（按各自包文档分类；分支级） | `REPOSITORY_STATUS.md` |
| 复杂度由 Moodify 承担 | 用户不需要理解 Ear 即可获得播放体验 | `CURRENT_CANON.md §3 不变量 #3` + `PRODUCT_BOUNDARY.md §User-visible complexity rule` |
| 工具（内部） | `apps/ear-workbench/`（INTERNAL 工具，FREEZE，不进入公开导航） | `MOODIFY_PRODUCT_AUDIT.md §4 表` |

**不属于该模块的事：**

- 不成为对外产品面（`CURRENT_CANON.md §3 不变量 #1`）。
- 不作为 §9 Tier A/B 公开语言出现在首屏；只在 Tier C（技术 / 研究层）或 INTERNAL 上下文出现（`PUBLIC_BRAND_CONSTITUTION.md §9`）。
- 不在 v1.0 默认安装 / CI / AI 上下文中加载 MAMSE / physics / LLM / lyric / transcription 等 research 子包。

#### Cloud Production

| 项 | 内容 | Canon Evidence |
|---|---|---|
| 角色 | 内部生产系统；Intake → Identify → Analyze → Stem → Judge → Intervene → Preset Decision → Render → Verify → Evidence → Delivery | `INTERNAL_SYSTEMS.md §2` |
| LA VPS 103.144.246.242 | nginx + cloudflared + moodify-api(:8000) + moodify-music(:3100) + music-bff(:8100) + worker + audiolla | `CURRENT_ARCHITECTURE.md §1` |
| 杭州 VPS 120.55.191.146 | moodify-api(:8000 公网, service-key) + moodify-data-worker + 4 timers + /var/lib/moodify (10 曲 pilot SUCCEEDED) | `CURRENT_ARCHITECTURE.md §1` |
| PolarDB | 3 实例，BLOCKED 核验；schema 空转 | `CURRENT_ARCHITECTURE.md §1` + `CURRENT_ARCHITECTURE.md §4 数据权威行` |
| OSS/S3/R2 | NOT_PROVISIONED | `CURRENT_ARCHITECTURE.md §1` |
| 云端 AI 推理 | 无（无 GPU、无模型 serving） | `CURRENT_ARCHITECTURE.md §1` |
| 状态机 authority | 4 个（workflow_engine LEGACY / node CANONICAL / data_factory CANONICAL / reconstruction_factory EXPERIMENTAL）；统一方案 `HUMAN_DECISION_REQUIRED` | `INTERNAL_SYSTEMS.md §3` + `CANON_CHANGELOG.md CD-015` |

**不属于该模块的事：**

- 不暴露内部状态机给客户端；READY 之外的内部状态不泄漏。
- 不把未验证的云端能力作为宣传点（`PRODUCT_BOUNDARY.md §Evidence boundary` + `CURRENT_CANON.md §3 不变量 #4`）。
- 不在 v1.0 引入 Redis、微服务网关、企业 API、第二队列（`MOODIFY_PRODUCT_AUDIT.md §6.3 MVP Architecture`）。

### 2.5 公开数据 authority

| 项 | 内容 | Canon Evidence |
|---|---|---|
| Music data authority（结构） | `moodify-music-package/models.py` + Alembic | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.3` |
| v1.0 激活表 | `tracks` + `track_versions` + `favorites` + `play_events` | `MOODIFY_PRODUCT_AUDIT.md §6.3 Database` |
| 公开 API | Music BFF（唯一） | `MOODIFY_PRODUCT_AUDIT.md §6.3 Backend` |
| 写入唯一路径 | Production API / worker；不暴露给普通用户 | `MOODIFY_PRODUCT_AUDIT.md §6.3 Backend` |

**不属于该模块的事：**

- `apps/web/lib/db/schema.ts`（Web Drizzle）不构成平行 schema；最终删除 / 改为生成类型（执行需 `CANON_CHANGE = YES`）。
- CWC 积分账本 / passport / bridge / license intent / support intent 在 v1.0 不激活。
- QA SQLite / PolarDB（待核验）/ 历史本地数据工厂不构成 Music data authority。

---

## 3. Public Brand Tier 与工程的对应

按 `PUBLIC_BRAND_CONSTITUTION.md §9`：

| Tier | 公开语言 | 工程入口（默认可见） | 备注 |
|---|---|---|---|
| **A 核心公开** | Moodify · Every voice deserves to be heard · Listen. Then Play. · Play. | `apps/web/app/page.tsx` 主屏文案 + `rongjingmusic.com` Brand Home | 不变 |
| **B 次级公开** | Evidence · Original / Moodify · Listening experience | `apps/web/app/listen/` + `apps/web/app/evidence/`（Listen Demo v0.1） | 用户理解产品后出现 |
| **C 技术 / 研究层** | Listen / Represent / Judge / Intervene / Verify / Learn · source preservation | INTERNAL 文档（按需加载） | 默认不暴露 |
| **D 退出公共主叙事** | Auditory Intelligence Infrastructure · Give machines the ability to hear · The Ear of AI · ACU · Build with Moodify · Developers · API · Creator Platform | **不出现** | `PUBLIC_BRAND_CONSTITUTION.md §9 Tier D` 明确退出 |

---

## 4. 三站职责

按 `PUBLIC_BRAND_CONSTITUTION.md §7` + `CURRENT_CANON.md §3 不变量 #7`：

| 域名 | 身份 | 主导航 | 内容来源 |
|---|---|---|---|
| `rongjingmusic.com` | Moodify 主官网 / Product Home | Play / Download / About / Company | `ops/web_origin/site/rongjingmusic/` |
| `rongjingwenchuan.com` | 荣景文川公司官网 / Company Home | Moodify / Research / Company / Contact | `ops/web_origin/site/rongjingwenchuan/` |
| `rongjinwenchuan.xyz` | 过渡期 Web Player / 历史入口 | Moodify Logo（返回 rongjingmusic.com） | 过渡 Player |
| `play.rongjingmusic.com` | 优先迁移目标（UNVERIFIED） | 长期 Web Player | 迁移后落地 |

---

## 5. Public Form 决策测试（5 项硬门槛）

按 `PUBLIC_BRAND_CONSTITUTION.md §13`，未来任何对外功能 / 文案 / 页面**上线前**必须通过：

| 测试 | 问题 | 失败默认 |
|---|---|---|
| Test A - Identity | 它让 Moodify 更像一个明确的聆听产品，还是把 Moodify 分裂成多个身份？ | 不进入公共表面 |
| Test B - Comprehension | 第一次接触的人能否在 10 秒内知道这里是什么？ | 不进入公共表面 |
| Test C - Audibility | 这项价值能否最终通过听觉体验得到证明？ | 不进入公共表面 |
| Test D - Complexity | 这是用户必须知道的复杂度，还是 Moodify 应替用户承担的复杂度？ | 不进入公共表面 |
| Test E - Brand | 它是否服务 "Every voice deserves to be heard."？ | 不进入公共表面 |

机器可在 §5 §6.1 决策链范围内二元判断；最终决策必须叠加 `AGENTS.md §Judgment Authority`（听觉判断需 `HUMAN_REQUIRED` / `INCONCLUSIVE`）。

---

## 6. 工程主链（用户外部体验）

```text
[Public Brand Tier A/B]
   用户
   ↓
Web / Android Player           (apps/web/, apps/music-android/)
   ↓ HTTP/S (BFF contract)
Music BFF                       (moodify-music-package/.../bff, 唯一公开)
   ↓
Music Data Authority            (moodify-music-package/models.py + Alembic)
   ↓
PLAY                            (User-visible 终点)

—— 内部（用户不可见）——

Cloud Production                (LA + 杭州 VPS)
   ↓
Audio Intelligence (Ear)        (moodify-core-package/src/moodify/)
   ↓
Source → Analyze → Judge → Render → Verify → READY → Delivery
```

**外部极简，内部可复杂。**（`PUBLIC_BRAND_CONSTITUTION.md §0`：内部可以复杂，外部必须简单。）

---

## 7. 不属于本架构的事

按 `MOODIFY_PRODUCT_AUDIT.md §6.2`（v1.0 不在）：

- 上传分析报告、自动母带、创作者工作台、许可交易、赞助、积分、开放 API、企业 SSO、社交关注、公共 Evidence dashboard、多模型研究界面。
- 第二公开产品（QA Web v0.1、QA Desktop、Pulse、Ear Workbench 作为对外产品）。
- 第二 state machine authority / 第二 Music data authority / 第二 Music BFF。
- 第二 Android 工程 / 第二 Desktop 工程 / 第二 Core 入口。
- `apps/web/lib/db/schema.ts`（Web Drizzle）作为平行 schema（最终删除 / 改为生成类型）。
- 默认加载 MAMSE / physics / LLM / lyric / transcription 等 research 子包。

---

## 8. 本文件**不**做的事

- **不**修改 `docs/canon/*` / `docs/brand/public/*` / `AGENTS.md` / `MOODIFY_PRODUCT_AUDIT.md` / `REDUCTION_PLAN.md` / `AI_CONTEXT_OPTIMIZATION.md`。
- **不**创建新工程、新 BFF / 新 state machine。
- **不**改变 Music data authority 结构 / state machine authority（执行需 `CANON_CHANGE = YES`）。
- **不**移动 / 删除任何文件。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**