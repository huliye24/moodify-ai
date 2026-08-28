# Moodify v1.0 Mainline Declaration — 2026-08-24

**性质**：整合性主线声明（不是新 Canon；不替代 `docs/canon/*`；不替代既有审计 / 减法计划）
**任务**：建立 "Moodify 唯一核心产品 + 主线边界 + 共享地图"，作为下一轮（Reduction Execution 001：物理隔离 archive/freeze）入口。
**CANON_CHANGE**：`NO`
**执行状态**：仅声明；未修改、删除、移动任何业务代码或既有文档。

---

## 0. 为什么是 1 份而不是 6 份

Codex 原始 6 件任务清单（`CORE_PRODUCT_V1.md` / `PRODUCT_BOUNDARY_V1.md` / `ENTROPY_MAP_V1.md` / `MOODIFY_MAINLINE_ARCHITECTURE.md` / `AI_CONTEXT_REDUCTION_PLAN.md` / `EXECUTION_PLAN_V1.md`）会在仓库形成**第二套 authoritative 减法地图**，违反 `CURRENT_CANON.md §3 不变量 #1`（一个对外产品身份）与 `AUTHORITY_ORDER.md`（Canon 第 3 级 > 任何新治理文档）。

仓库已有：

| 文档 | 角色 | 状态 |
|---|---|---|
| `AGENTS.md` | 仓库最高认知入口 | CANONICAL（第 2 级） |
| `docs/canon/CURRENT_CANON.md` | 当前产品身份 | CANONICAL（第 3 级） |
| `docs/canon/PRODUCT_BOUNDARY.md` | 内外边界 | CANONICAL |
| `docs/canon/CURRENT_ARCHITECTURE.md` | 已验证现状 | CANONICAL |
| `docs/canon/INTERNAL_SYSTEMS.md` | 内部系统与 authority | CANONICAL |
| `docs/canon/AUTHORITY_ORDER.md` | 冲突裁决 | CANONICAL |
| `docs/canon/CANON_CHANGELOG.md` | Canon 变更留痕 | CANONICAL |
| `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | 最高 Public Brand 主题权威 | CANONICAL |
| `MOODIFY_PRODUCT_AUDIT.md` | 只读产品减法审计 v1.0（332 行） | 既有审计 |
| `REDUCTION_PLAN.md` | Phase 1-4 减法计划（173 行） | 既有计划 |
| `AI_CONTEXT_OPTIMIZATION.md` | AI 上下文优化建议（124 行） | 既有计划 |
| `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` | 本会话 Delta 审计（本目录已有） | 既有 Delta |

本文件**唯一角色**：把上述 12 份治理文件整合为 **AI 与工程师共享的同一张地图入口**，不重复内容，只做**索引 + 主线声明 + 决策原则**。

---

## 1. Moodify 唯一核心产品（Canon 已确立）

> 下列定义**全部**为 Canon 第 3 级已确立的事实，不是本声明的"判断"。

### 1.1 公共命名

| 字段 | 值 | Canon Evidence |
|---|---|---|
| **对外产品** | Moodify Music / Moodify Player | `CURRENT_CANON.md §1` + `PRODUCT_BOUNDARY.md §External Product` |
| **第一阶段用户动作** | PLAY | `CURRENT_CANON.md §1` + `PRODUCT_BOUNDARY.md §Primary user action` |
| **品牌信念** | 每一种声音，都值得被世界听见。 / Every voice deserves to be heard. | `CURRENT_CANON.md §1` + `PUBLIC_BRAND_CONSTITUTION.md §1.2` |
| **产品原则** | Listen. Then Play. | `CURRENT_CANON.md §1` + `PUBLIC_BRAND_CONSTITUTION.md §2` |
| **公开证明顺序** | Belief → Sound → Play → Proof → Explanation → Technology | `PUBLIC_BRAND_CONSTITUTION.md §11` |
| **站点职责** | `rongjingmusic.com` = Product Home；`rongjingwenchuan.com` = Company Home；`rongjinwenchuan.xyz` = 过渡 Player | `CURRENT_CANON.md §3 不变量 #7` + `PUBLIC_BRAND_CONSTITUTION.md §7` |

### 1.2 内部系统（不构成对外产品面）

| 系统 | 角色 | Canon Evidence |
|---|---|---|
| **Moodify Ear / Auditory Intelligence** | 内部听觉智力（Listen / Represent / Judge / Evidence / Uncertainty / Learn / Verify / Controlled Intervention） | `CURRENT_CANON.md §2` + `INTERNAL_SYSTEMS.md §1` |
| **Cloud Production System** | 内部生产（Intake → Identify → Analyze → Stem → Judge → Intervene → Preset Decision → Render → Verify → Evidence → Delivery） | `INTERNAL_SYSTEMS.md §2` |
| **State machine authority（现状）** | 4 个 authority（workflow_engine LEGACY / node CANONICAL / data_factory CANONICAL / reconstruction_factory EXPERIMENTAL）— 统一方案 `HUMAN_DECISION_REQUIRED` | `INTERNAL_SYSTEMS.md §3` + `CANON_CHANGELOG.md 2026-08-17 CD-015` |
| **Classic Reconstruction** | 内部生产哲学 v1.0（P02 批准）；Article I 对外表述已被 Canon 覆盖 | `CURRENT_CANON.md §5` + `CANON_CHANGELOG.md CD-014` |

### 1.3 Public Form 决策测试（5 项硬门槛）

任何对外功能 / 文案 / 页面**上线前**必须通过 `PUBLIC_BRAND_CONSTITUTION.md §13` 的 5 项测试：

| 测试 | 问题 | 失败默认 |
|---|---|---|
| **Test A - Identity** | 它让 Moodify 更像一个明确的聆听产品，还是把 Moodify 分裂成多个身份？ | 不进入公共表面 |
| **Test B - Comprehension** | 第一次接触的人能否在 10 秒内知道这里是什么？ | 不进入公共表面 |
| **Test C - Audibility** | 这项价值能否最终通过听觉体验得到证明？ | 不进入公共表面 |
| **Test D - Complexity** | 这是用户必须知道的复杂度，还是 Moodify 应替用户承担的复杂度？ | 不进入公共表面 |
| **Test E - Brand** | 它是否服务 "Every voice deserves to be heard."？ | 不进入公共表面 |

> Codex 原始手册的"未来所有决策只问：这个东西是否增强用户打开 Moodify 后更愿意播放下一首音乐" — 这条原则**不可独立**作为决策依据，必须叠加在上述 5 项测试之上，且不压制 `AGENTS.md §Judgment Authority` 中的人类 authority（听觉判断仍需输出 `HUMAN_REQUIRED` / `INCONCLUSIVE`）。

---

## 2. Moodify v1.0 主线边界

> 下列 KEEP / FREEZE / ARCHIVE / DELETE CANDIDATE 均为**建议**；执行必须满足 `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀` 6 项（`git grep / CI / systemd/nginx/Docker / 30 天日志均无调用` + `owner 签字` + `可替代路径有测试` + `不改变 Canon / Job / data / evidence authority` + `必要历史 tag 或归档索引保存` + `回滚为 revert commit 或 release artifact`）。

### 2.1 KEEP（当前主线）

> 服务 PLAY 闭环；已被 Canon / 既有审计 / 本会话 Delta 报告判定。

| 范畴 | 路径 / 能力 | Canon Evidence |
|---|---|---|
| 对外 Web Player | `apps/web/` + `apps/music-android/`（release workflow） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `CURRENT_ARCHITECTURE.md §1` |
| Music BFF | `moodify-music-package/.../bff` | `MOODIFY_PRODUCT_AUDIT.md §4 表` |
| Music data authority | `moodify-music-package/models.py` + Alembic | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.3`（执行需 `CANON_CHANGE = YES` 验证） |
| Ear 内部核心 | `moodify-core-package/src/moodify/`（v01_pipeline + data_factory） | `INTERNAL_SYSTEMS.md §1` + `MOODIFY_PRODUCT_AUDIT.md §4 表` |
| Listen Demo v0.1 落地链 | `apps/web/app/listen/` + `apps/web/app/evidence/` + `moodify-core-package/scripts/listen_demo_render.py` + `ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.{sh,README.md}` | Delta 报告 §1.1 + §1.2（本会话判定 KEEP） |
| 三站公开表达 | `rongjingmusic.com`（Brand）+ `rongjingwenchuan.com`（Company）+ `rongjinwenchuan.xyz`（过渡 Player）+ `play.rongjingmusic.com`（UNVERIFIED） | `CURRENT_CANON.md §3 不变量 #7` + `PUBLIC_BRAND_CONSTITUTION.md §7` |
| 8-12 个治理入口（默认加载） | 详见 `AI_CONTEXT_OPTIMIZATION.md §2 表` | `AI_CONTEXT_OPTIMIZATION.md §2` |

### 2.2 FREEZE（冻结但保留）

> 现有能力**保留**，但 v1.0 不新增 / 不投入主线工程。恢复条件明确。

| 范畴 | 路径 / 能力 | 未来恢复条件 |
|---|---|---|
| Moodify Ear / Auditory Intelligence | `moodify-core-package/src/moodify/era_diagnostic` / `identity_guard` / `reconstruction_objective` 等 | 仅在 PLAY 闭环有真实用户证据后回到主线；目前为 Internal |
| Reconstruction Job | `moodify-core-package/.../reconstruction_job` | 真实生产 case 出现 + 完整 billing / state machine 验证（CD-015 未决） |
| MAMSE-001..016 | `moodify_experimental` / scripts / artifacts | 研究资产；不进入默认安装 / CI / AI 上下文（`MOODIFY_PRODUCT_AUDIT.md §4 表`） |
| Physics / LLM / lyric / transcription 等研究域 | Core 子包 | 同上 |
| Ear Workbench（内部工具） | `apps/ear-workbench` | 内部研究工具；**不得**进入公开导航与 MVP 发布（`MOODIFY_PRODUCT_AUDIT.md §4 表`） |
| Creator Studio / 发布 | `apps/web/app/studio` + BFF creator/track routes | 当前没有 creator 产品证据；不分散 listener-first 主线 |
| 创作者主页 / 关注 | `/c/[handle]` + follows | 足够供给与用户行为后再恢复 |
| License Intent | Web / BFF / DB | 不是播放核心；无成交证据 |
| Support / 支付意图 | Web / BFF / DB | 无真实支付；避免把 intent 当收入 |
| Creation Passport | Music DB / Web | 潜在信任资产，不是 MVP 首次播放所需 |
| Evidence Bridge | Music DB / API | 保留契约研究；无生产流量时不扩展跨域状态 |
| 歌单 | Web + BFF + DB | 可保留已实现能力；v1.0 不新增协作 / 分享 / 推荐逻辑 |
| Music Data API（与 BFF 平行） | `moodify-music-package/.../api` | MVP 不需要 BFF + 大型 internal API 双层 surface；保留清晰单一写 authority |
| Web Drizzle schema（与 SQLAlchemy 平行） | `apps/web/lib/db/schema.ts` | 同上；删除需 `CANON_CHANGE` 验证 |
| 历史审查 / 证据包 | `artifacts/` / `审查包/` / `windows版本开发/` | 移出默认主线上下文；按 Evidence Index 只保留索引与不可替代证据 |
| Demo Intelligence Report | `demo/` + `engine/report_schema` | 可作内部演示；**不能**升级为第二产品面 |
| Demo / 配置文件 | `examples/` / `deliverables/` / `data/` / `inspector_reports/` / `listening_test/` / `phys-lab/` / `pre-music/` / `RJWC_VideoPack_System/` / `research/`（部分子包） | 研究 / 历史资产；不进入默认 AI 上下文（详见 `AI_CONTEXT_OPTIMIZATION.md §3`） |

### 2.3 ARCHIVE（历史资产）

> 移出默认 AI 检索；通过 `docs/ARCHIVE_INDEX.md` 定位（**该索引文件按 `REDUCTION_PLAN.md Phase 2` 尚未建立 — 见 §4**）。

| 范畴 | 当前路径 | 处理方式 |
|---|---|---|
| 审查包 | `审查包/`（382 文件） | `AI_CONTEXT_OPTIMIZATION.md §3` 建议入 `archive/`；按 Evidence Index 只保留不可替代证据 |
| Windows 历史开发 | `windows版本开发/`（330 文件） | 同上 |
| 生成 artifact | `artifacts/`（956 文件） | 大部分移外部 artifact store / archive；保留索引与 hash manifest |
| 07Music / asset-registry / benchmark / calibration_reports / cloud_data / configs / inspector_reports / listening_test / local_audio_assets / moodify-app / moodify-bridge / moodify-system / music / moodify_runtime / night / output / outputs / project_analytics / science / scratch / security / shared-fixtures / temp / third_party / tmp / tools / treatment_records / uploads / video / workers / _github_moodify_ai / Moodify_Deep_Ear_Diagnostic_Pack_v0.1.1 / 中文工作目录（`实验图片` / `工程预算` / `项目ppt` / `研究材料` / `投资资料`） | 大量生成 / 历史 / 临时 / 重复资产；按需建立 ARCHIVE_INDEX.md（详见 §4） |

### 2.4 DELETE CANDIDATE（仅候选，未授权）

> 本节只列**已在本会话 Delta 报告中被 D-1 明确判定的 DELETE 候选**，加上 `MOODIFY_PRODUCT_AUDIT.md §4 表` 与 `REDUCTION_PLAN.md Phase 1-3` 已明示的高置信候选。**不授权 mass-delete**；执行前必须满足 §0 安全阀 6 项。

| 路径 / 范畴 | 当前 Phase | 严格约束 |
|---|---|---|
| **moodify-qa/**（含 `api/`、`core/`、`tests/`、`Dockerfile`、`docker-compose.yml`、`qa_storage.db`） | DELETE 候选（Delta D-1） | 自描述 "AI Audio Quality Assurance Infrastructure"，违反 `PUBLIC_BRAND_CONSTITUTION.md §2.2 禁单`；两份 2026-08-24 新文档把它包装为对外产品面，未声明 `CANON_CHANGE`，未在 `CANON_CHANGELOG.md` 留痕。`REDUCTION_PLAN.md Phase 3 §3.4` 已规划（与 calibration / legacy orchestration 同列）。 |
| **moodify-qa-desktop/**（未跟踪） | DELETE 候选（Delta D-1） | Electron 桌面壳，依赖 moodify-qa；`MOODIFY_PRODUCT_AUDIT.md §4 表`已标 DELETE；`REDUCTION_PLAN.md Phase 1 + Phase 3 §3.5` 双规划。 |
| **docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md** + **docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md** | DELETE 候选（Delta D-1） | 把已 DELETE 候选目录包装为对外产品；自陈"必须声明 CANON_CHANGE"但未声明。Verification (d)：标 STATUS 头 `REJECTED / NOT-AUTHORIZED`。 |
| **products/**（4 个产品模块 qa / master / rating / supply） | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 主要为空目录、README、config；制造不存在的平台认知 |
| **shared/** | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 无实质实现，重复 Core 中已有 contracts / authority / node / safety / api |
| **sdk/** | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | client 返回 placeholder，async 明确未实现；无公开 API authority |
| **moodify-pulse/** | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.5`） | 第二产品身份、mock data、与 Player 重复；先提取必要 Windows 播放代码 |
| **moodify/orchestration/workflow_engine.py** | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 已被 Canon 分类 LEGACY；需 30 天日志观测 |
| **engine/**（仅 facade） | MERGE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 主要被 demo 使用并反向委托 Core；选择 Core 为唯一包 |
| **CWC 积分账本**（Music DB/API） | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 当前无用户闭环，提前引入类货币与账务复杂度 |
| **Root API + worker Docker** | MERGE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表`） | 与真实部署、Core node worker 和多 API facade 对齐后只留一个 compose |
| **扫描 apps/web/app/track/[id]** | DELETE 候选（迁移期结束后）（`MOODIFY_PRODUCT_AUDIT.md §5.2`） | 仅兼容跳转；迁移期结束后 |
| **apps/android/** | MERGE 候选（`MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.1 A`） | 与 `apps/music-android` 双 Android authority；迁移必要功能后退役 |
| **benchmark/baseline.py + research/benchmarks/baseline.py** | DELETE 候选（`MOODIFY_PRODUCT_AUDIT.md §5.2`） | 完全相同；保留一份即可 |
| **scan_err.txt** | DELETE 候选（`REDUCTION_PLAN.md Phase 1`） | 0 字节 |
| **Root 中文工作包 / 压缩快照 / 临时目录 / 安装器** | DELETE 候选（`REDUCTION_PLAN.md Phase 1` + `MOODIFY_PRODUCT_AUDIT.md §5.2`） | 不应属于源码根目录；未跟踪文件可不提交，已跟踪文件先核验发布依赖 |

> 上表是**完整候选列表**。任何 Phase 1 / 2 / 3 的物理执行**必须**走 `REDUCTION_PLAN.md §0` + `MOODIFY_PRODUCT_AUDIT.md §7` 安全阀 + owner 签字。

---

## 3. Moodify v1.0 主线架构

> 不是理想图；只展示**已运行 / 已验证 + 2026-08-24 已有代码的 Canon-aligned 落地**。

```text
[Public Brand Tier — PUBLIC_BRAND_CONSTITUTION.md §9]

  Tier A (核心公开)        : Moodify · Every voice deserves to be heard · Listen. Then Play. · Play.
       │
  Tier B (次级公开, 用户理解后)
                             : Evidence · Original / Moodify · Listening experience
       │
  Tier C (技术/研究层, 默认不暴露)
                             : Listen / Represent / Judge / Intervene / Verify · source preservation
       │
  Tier D (退出公共主叙事)
                             : 严禁出现在首屏

[三站职责 — §7]

  rongjingmusic.com        = Product Home (Moodify 官网)
  rongjingwenchuan.com     = Company Home (荣景文川)
  rongjinwenchuan.xyz      = 过渡 Web Player / 历史入口
  play.rongjingmusic.com   = 优先迁移目标 (UNVERIFIED)

[对外产品面 — KEEP]

  Web Player
    ├── apps/web/app/page.tsx            (Player 主屏, KEEP)
    ├── apps/web/app/listen/             (Public Form §11 Sound, KEEP)
    ├── apps/web/app/evidence/           (Public Form §11 Proof, KEEP)
    └── Music BFF (moodify-music-package/.../bff, KEEP)

  Android Player
    └── apps/music-android/              (release workflow, KEEP)
    └── apps/android/                    (MERGE → 退役; §5.1 A)

[内部系统 — INTERNAL_SYSTEMS.md]

  Ear / Auditory Intelligence (INTERNAL)
    ├── moodify-core-package/src/moodify/   (v01_pipeline, KEEP — 已验证 10/10 pilot)
    ├── era_diagnostic / identity_guard / reconstruction_objective (FREEZE)
    └── apps/ear-workbench (INTERNAL 工具, FREEZE, 不进入公开导航)

  Cloud Production (INTERNAL)
    ├── LA VPS (亿速云)               : nginx + cloudflared + moodify-api(:8000) + moodify-music(:3100) + music-bff(:8100) + worker + audiolla
    ├── 杭州 VPS (阿里云)              : moodify-api(:8000 公网, service-key) + moodify-data-worker + 4 timers + /var/lib/moodify (10 曲 pilot SUCCEEDED)
    ├── PolarDB (3 实例, BLOCKED)     : MySQL 8.0.13 空壳 / MySQL 8.0.18 moodify_dev 19 表 ≈0 / PG 16.14 在线未用
    └── OSS/S3/R2 / 云端 AI 推理      : NOT_PROVISIONED

  State machine authority (现状 4 个, 统一 HUMAN_DECISION_REQUIRED — CD-015)
    ├── workflow_engine               : LEGACY
    ├── node (moodify-node worker)    : CANONICAL (P00 TT-009)
    ├── data_factory                  : CANONICAL (P00 TT-008)
    └── reconstruction_factory        : EXPERIMENTAL (P00 TT-013)

[数据 authority — Canon 5 项中第 6 项]

  Music SQLAlchemy (moodify-music-package/models.py + Alembic)
     = Music data authority (KEEP)
     副作用 : apps/web/lib/db/schema.ts (Web Drizzle) — MERGE 候选, 状态枚举漂移
     副作用 : QA SQLite / PolarDB / 历史本地 — DELETE / FREEZE 候选
```

### 3.1 模块职责（每条带 Canon Evidence）

| 模块 | 职责 | 不属于该模块的事 |
|---|---|---|
| `apps/web/` | 对外 Web Player；唯一 Player 主入口 | 不展示工程预设、不暴露 LUFS / 频段、不强迫用户选择 preset |
| `apps/music-android/` | 对外 Android Player；唯一受支持 Android 工程 | 同上 |
| `apps/android/` | 退役目标；迁移必要能力（离线缓存、MediaSession、本地化） | 不是第二 Android 产品 |
| `moodify-music-package/.../bff` | 唯一公开 Music BFF；catalogue / track / playback / favorite / recent-play | 不是 Creator BFF；不是 License BFF |
| `moodify-music-package/models.py` | 唯一 Music data authority（v1.0 激活 tracks / track_versions / favorites / play_events） | 不承担用户体系 / 创作者 / 市场 / 信用 |
| `moodify-core-package/` | Ear 内部核心；`v01_pipeline` 主线；`data_factory` 数据侧主链 | 不是对外产品面；不作为第二公开身份 |
| `moodify-runtime`（待合并 / 重命名） | （如需）Ear 运行时入口 | 不是公开 API 入口 |
| `apps/ear-workbench` | 内部研究工具；不进入公开导航与 MVP 发布 | 不对外暴露；不是 PUBLIC_PRODUCT |
| `moodify-pulse/` | （DELETE 候选前）Windows 离线播放器；提取必要 Windows 播放代码后退役 | 不再作为 "AI Emotional Music Container" 第二产品身份 |
| `moodify-qa/` | （DELETE 候选）内部审查旁路；不暴露为对外 QA / API 平台 | 不是公开 API / 第三方平台 |
| `moodify-qa-desktop/` | （DELETE 候选）依赖 moodify-qa 的桌面壳 | 不提交主线 |
| `products/` / `shared/` / `sdk/` | （DELETE 候选）空壳 / placeholder / 重复 | 不构成产品能力 |
| `engine/` | MERGE 候选；选择 Core 为唯一包；避免永久 shim | 不是独立运行时 |
| `ops/` | 实际运行 runbook + 三站 origin + 部署 | 删除打包快照和重复站点源（`MOODIFY_PRODUCT_AUDIT.md §4 表`） |
| `docs/canon/*` + `docs/brand/public/*` | Canon 与 Brand 主题权威 | 不由普通功能任务静默修改 |
| `MOODIFY_PRODUCT_AUDIT.md` + `REDUCTION_PLAN.md` + `AI_CONTEXT_OPTIMIZATION.md` | 治理 / 减法 / 上下文（基线） | 不被新治理文档覆盖 |
| `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` | 本会话 Delta 审计（本目录已有） | 不被新治理文档覆盖 |

---

## 4. AI Context 减法地图（5 文件内理解 Moodify）

> 目标：未来 AI Agent **默认加载 ≤ 5 文件** 即可理解 Moodify 核心；不进入默认检索的目录仍可通过 ARCHIVE_INDEX.md 定位。

### 4.1 默认加载（5 文件入口）

| # | 路径 | 角色 |
|---|---|---|
| 1 | `AGENTS.md` | 仓库最高认知入口（Authority Order #2） |
| 2 | `docs/canon/CURRENT_CANON.md` | 当前产品身份（Authority Order #3） |
| 3 | `docs/canon/PRODUCT_BOUNDARY.md` | 内外边界 |
| 4 | `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | 最高 Public Brand 主题权威 |
| 5 | `docs/reduction/MAINLINE_DECLARATION.md`（本文件） | 主线声明 + 共享地图入口 |

### 4.2 按需加载

| 路径 | 何时读 |
|---|---|
| `docs/canon/CURRENT_ARCHITECTURE.md` | 涉及运行时 / 部署现状判断时 |
| `docs/canon/INTERNAL_SYSTEMS.md` | 涉及 Ear / Cloud Production / state machine authority 时 |
| `docs/canon/AUTHORITY_ORDER.md` | 指令冲突需要裁决时 |
| `docs/canon/CANON_CHANGELOG.md` | 需要查看 Canon 变更留痕时 |
| `docs/canon/CURRENT_ARCHITECTURE.md` | 已验证现状 |
| `docs/brand/public/README.md` | Public Brand 主题细化时 |
| `MOODIFY_PRODUCT_AUDIT.md` | 减法 / 价值评级判断时 |
| `REDUCTION_PLAN.md` | Phase 1-4 执行时 |
| `AI_CONTEXT_OPTIMIZATION.md` | AI 上下文优化具体实施时 |
| `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` | 本会话 / 后续 Delta 审计时 |
| `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` | Canonical / Experimental / Legacy 分类时 |
| `docs/ASSET_MODEL.md`（INTERNAL） | 认知基础设施涉及 |
| `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`（INTERNAL） | Ear 架构涉及 |
| `docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md`（内部生产哲学） | 重建生产哲学涉及（对外表述已被 Canon 覆盖） |

### 4.3 Archive（不进入默认检索，通过 ARCHIVE_INDEX.md 定位）

按 `REDUCTION_PLAN.md Phase 2` 与 `AI_CONTEXT_OPTIMIZATION.md §3` 规划：

| 目录 | 内容 | 处理方式 |
|---|---|---|
| `artifacts/`（956 文件） | 生成证据 | 仅保留不可替代证据 + hash manifest |
| `审查包/`（382 文件） | 重复任务书、报告包 | 入 archive/ |
| `windows版本开发/`（330 文件） | 历史 Windows 开发 | 入 archive/ |
| `实验图片/` / `工程预算/` / `项目ppt/` / `研究材料/` / `投资资料/`（中文根目录） | 中文工作包 | 入 archive/ |
| `07Music/` / `asset-registry/` / `benchmark/` / `calibration_reports/` / `cloud_data/` / `configs/` / `data/` / `deliverables/` / `demo/`（部分子包）/ `experiments/` / `inspector_reports/` / `listening_test/` / `local_audio_assets/` / `logo/` / `marketplace/` / `models/` / `moodify-app/` / `moodify-bridge/` / `moodify-system/` / `Moodify_Deep_Ear_Diagnostic_Pack_v0.1.1/` / `moodify_runtime/` / `music/` / `night/` / `output/` / `outputs/` / `phys-lab/` / `plugins/` / `pre-music/` / `project_analytics/` / `research/`（部分子包）/ `RJWC_VideoPack_System/` / `schemas/` / `science/` / `scratch/` / `sdk/`（DELETE 候选）/ `security/` / `shared-fixtures/` / `temp/` / `tests/`（部分）/ `third_party/` / `tmp/` / `tools/` / `treatment_records/` / `uploads/` / `video/` / `workers/` / `_github_moodify_ai/` | 大量生成 / 历史 / 临时 / 重复资产 | 按需建立 ARCHIVE_INDEX.md（**该文件尚未建立 — 见 §5**） |

### 4.4 外部存储（不在仓库内）

| 内容 | 建议位置 |
|---|---|
| 完整 moodify-music-package 数据备份 | PolarDB（核验通过后）+ 外部对象存储 |
| ops LA / 杭州部署快照 | LA VPS / 阿里云 / Cloudflare（核验后） |
| 生成 audio artifact（Cadeau10 wav 等） | `ops/web_origin/site/rongjingmusic/audio/`（已部署于 LA 媒体根，不入 git） |
| 投资人路演 / 内部 PPT | 外部存储（不入 git） |

---

## 5. 下一轮（Reduction Execution 001：物理隔离）的执行边界

> 本节是给下一位 Cursor agent 的**执行边界声明**，不是新执行计划。

### 5.1 必须满足的前置条件（不满足则不执行）

1. **owner 签字**：每个 DELETE / ARCHIVE 候选必须由 ops 确认无生产调用。
2. **30 天观测**：`MOODIFY_PRODUCT_AUDIT.md §7 #1` 要求 git grep / CI / systemd / nginx / Docker / 30 天日志均无调用。
3. **可替代路径测试**：`MOODIFY_PRODUCT_AUDIT.md §7 #3` 要求可替代路径有测试。
4. **Canon 安全**：`MOODIFY_PRODUCT_AUDIT.md §7 #4` 要求不改变 Canon / Job / data / evidence authority；否则必须 `CANON_CHANGE = YES` + 人类授权。
5. **历史保存**：`MOODIFY_PRODUCT_AUDIT.md §7 #5` 要求必要历史被 tag 或归档索引保存。
6. **回滚准备**：`MOODIFY_PRODUCT_AUDIT.md §7 #6` 要求回滚为 revert commit 或 release artifact，不在主线保留第二实现。

### 5.2 推荐 Phase 1 立即可做（不需 owner 签字）

按 Delta 报告 §8 Phase 1 第一步：

```
把 docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md
与 docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md
顶部加 STATUS 头:

> STATUS: REJECTED / NOT-AUTHORIZED — 2026-08-24 Canon Change 主张未获人类批准,
> 不进入 v1.0 实施。
```

**不删文件** / **不改内容** / **不需 owner 签字** / **可由 Cursor 直接执行**。

### 5.3 需要 owner 签字的 Phase 1 物理删除

| 候选 | owner 签字 + 30 天观测 | Canon Change |
|---|---|---|
| `moodify-qa/` | 是 | 否（不在 Canon 5 项之内） |
| `moodify-qa-desktop/` | 是 | 否 |
| `docs/IMPLEMENTATION_PLAN_QA_V0.1_2026-08-24.md` | 是 | 否（加 STATUS 头不需签字） |
| `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` | 是 | 否 |
| `scan_err.txt` | 否（0 字节空文件） | 否 |
| Root 中文工作包 / 压缩快照 / 安装器 | 部分需先核验发布依赖 | 否 |

### 5.4 需要 `CANON_CHANGE = YES` 才能动的项

| 项 | 原因 |
|---|---|
| Music data authority 合并（删除 Web Drizzle schema / 合并 tracks + track_versions + favorites + play_events） | `CURRENT_CANON.md §3 Canon 不变量 #6` "Canon 变更必须可见" + `MOODIFY_PRODUCT_AUDIT.md §5.1 D` 明确说"该动作涉及 data authority" |
| 单一 authoritative state machine 统一方案 | `CANON_CHANGELOG.md CD-015 HUMAN_DECISION_REQUIRED` |
| QA 产品化方向（如果人类否决后想保留 moodify-qa） | `CURRENT_CANON.md §3 不变量 #1` |
| 对外产品身份变更（任何与 v1.1 不一致的新身份） | `CANON_CHANGELOG.md 2026-08-19 v1.1 冻结项` |

### 5.5 本声明**不**做的事

- **不**修改 `docs/canon/*` / `docs/brand/public/*` / `AGENTS.md`
- **不**创建 `CORE_PRODUCT_V1.md` / `PRODUCT_BOUNDARY_V1.md` / `ENTROPY_MAP_V1.md` / `MOODIFY_MAINLINE_ARCHITECTURE.md` / `AI_CONTEXT_REDUCTION_PLAN.md` / `EXECUTION_PLAN_V1.md`（与既有审计 / 减法计划重复）
- **不**移动 / 删除任何文件
- **不**声明 `CANON_CHANGE`
- **不**授权 mass-delete
- **不**对任何 DELETE / ARCHIVE 候选做物理动作

---

## 6. 主线决策原则（机器可二元判断的部分）

按 `PUBLIC_BRAND_CONSTITUTION.md §13` 5 项测试 + `AGENTS.md §Judgment Authority`（不压制人类 authority）+ `MOODIFY_PRODUCT_AUDIT.md §7 DELETE 安全阀` 6 项：

### 6.1 机器可二元判断的部分

| 问题 | 是 / 否 | 后果 |
|---|---|---|
| 这一项是否直接承载 PLAY 闭环？ | 是 | KEEP / 候选进入主线 |
| | 否 | 进入下一问 |
| 这一项是否在 Tier A / Tier B 公开语言中？ | 是（且服务 PLAY） | KEEP |
| | 否（Tier C） | 进入下一问 |
| 这一项是否属于 Ear / Cloud Production 等内部系统？ | 是 | INTERNAL — 保留 + FREEZE |
| | 否 | 进入下一问 |
| 这一项是否属于历史 / 临时 / 重复 / 空壳？ | 是 | DELETE / ARCHIVE 候选 |
| | 否 | HUMAN_DECISION_REQUIRED |

### 6.2 人类必须判断的部分（机器不可替代）

| 问题 | 人类决策 |
|---|---|
| 听觉 / 美学判断（任何最终进入公开比较的 wav） | 必须真人听评确认（参考 `runbook_listen_demo_v0.1.sh` Step 5） |
| Canon 5 项的任何变更 | 必须人类授权 + `CANON_CHANGE = YES` + 留痕 |
| `HUMAN_REQUIRED` / `INCONCLUSIVE` 状态的最终判定 | 必须人类确认 |
| Creator / 收费 / API / B 端商业模式恢复条件 | `CANON_CHANGELOG.md CD-011 + CD-014 + CD-015` 均 `HUMAN_DECISION_REQUIRED` |

> Codex 原始手册的 "未来所有决策只问：这个东西是否增强用户打开 Moodify 后更愿意播放下一首音乐" — 机器只能问这问 + 给出**建议**；最终决策必须叠加 §13 5 项 + §6.1 决策链 + §6.2 人类 authority。

---

## 7. 共享地图索引（AI 与工程师从同一入口开始）

### 7.1 5 文件入口（默认加载）

```
1. AGENTS.md                                    — 仓库最高认知入口
2. docs/canon/CURRENT_CANON.md                  — 当前产品身份
3. docs/canon/PRODUCT_BOUNDARY.md               — 内外边界
4. docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md — 最高 Public Brand 主题权威
5. docs/reduction/MAINLINE_DECLARATION.md       — 本文件（主线声明 + 共享地图入口）
```

### 7.2 决策流程（任意工程任务）

```
读 5 文件入口
   ↓
判断 : Canon 不变量 #1（一个对外产品身份）？  Y/N
   ↓ Y                                            ↓ N
进入主线                                    HUMAN_DECISION_REQUIRED
   ↓
判断 : Public Form §13 5 项测试？  全部 PASS
   ↓ 是                                          ↓ 否
判断 : KEEP / FREEZE / ARCHIVE / DELETE CANDIDATE？
   ↓ KEEP                                       ↓ 其他
直接执行                                读 §6.1 决策链 + §6.2 人类 authority
```

### 7.3 Phase 边界

| 阶段 | 触发条件 | 由谁执行 |
|---|---|---|
| Phase 1 (Documentation First) | 任何未授权 Canon 主张被发现（例：2026-08-24 QA 产品化方向） | Cursor 可直接加 STATUS 头（不删 / 不改） |
| Phase 2 (物理隔离 archive/) | owner 签字 + ARCHIVE_INDEX.md 建立 + 路径映射 | Cursor 在 owner 授权下执行 |
| Phase 3 (物理删除) | owner 签字 + 30 天观测 + 安全阀 6 项全过 | Cursor 在 owner 授权下执行 |
| Phase 4 (CANON_CHANGE) | 触及 Canon 5 项任何一项 | 人类 owner 单独流程（`CANON_CHANGE = YES` + changelog） |

---

## 8. 等下一轮（Reduction Execution 001）

下一轮由 ops / Cursor 启动，按本声明 §5 的 Phase 1 → 4 顺序执行。本声明**不**执行任何修改 / 删除 / 移动。

**报告结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**