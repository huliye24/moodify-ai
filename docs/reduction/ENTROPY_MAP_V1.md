# Moodify Entropy Map v1 — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** 模块级熵地图（per-module inventory + KEEP/FREEZE/ARCHIVE/DELETE 决议）；为 Phase 2-3 物理动作提供**逐路径**判定依据。
**数据来源：**
- `MOODIFY_PRODUCT_AUDIT.md §2.1`（仓库总体规模，含文件数）
- `MOODIFY_PRODUCT_AUDIT.md §4 表`（每模块价值评级）
- `MOODIFY_PRODUCT_AUDIT.md §5.1`（重复系统 A-F）
- `MOODIFY_PRODUCT_AUDIT.md §5.2`（死代码与空壳候选）
- `REDUCTION_PLAN.md Phase 1-3`
- `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md §2 D-1`
- 当前工作树直接观察（`git status` / 目录扫描）
- `CURRENT_ARCHITECTURE.md §1`（云端现实）
- `INTERNAL_SYSTEMS.md §3`（状态机 authority）

**CANON_CHANGE：** `NO` —— 本文件归类引用既有审计 / Delta / Canon；任何 data / state machine authority 合并在表格中**已显式标记** `CANON_CHANGE = YES`。
**执行状态：** 仅分类。**未修改、删除、移动任何业务代码、目录或既有文档。**

---

## 0. 仓库总体规模（基线）

按 `MOODIFY_PRODUCT_AUDIT.md §2.1` 2026-08-24 观察值：

| 指标 | 观察值 | 含义 |
|---|---:|---|
| Git tracked files | 3,300 | 单仓库认知面过大 |
| Markdown | 约 772 | 文档数接近代码数 |
| Python | 686 | 集中于 Core / 实验 / 历史执行包 |
| JSON | 527 | 大量为生成证据 |
| `artifacts/` | 956 文件（≈510 MD） | 生成证据最大单一目录 |
| `moodify-core-package/` | 621 文件（≈507 代码） | 内部能力中心 |
| `审查包/` | 382 文件（≈308 MD） | 重复任务书 / 报告包 |
| `windows版本开发/` | 330 文件（≈255 MD） | 历史 Windows 开发 |
| `docs/` | 275 文件（≈246 MD） | 权威 + 现状 + 设计 + 计划 + 历史混放 |
| 活跃本地分支 | 30+ | 多条"主线/产品/迁移"叙事并存 |

**基线结论：** 主线工作集应从 3,300 tracked 收敛到 500-800（`AI_CONTEXT_OPTIMIZATION.md §7` 验收指标）。

---

## 1. 模块级熵地图

> 列：`模块 / 当前作用 / 是否服务主线 / 决定 / Canon Evidence / 阶段归属`

### 1.1 apps/

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `apps/web/` | 对外 Web Player；`page.tsx` + `listen/` + `evidence/` + `/library` + BFF 路由；含 `lib/db/schema.ts`（Drizzle） | 是 | **KEEP**（Drizzle 部分 MERGE） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + Delta §1.2 + `CURRENT_ARCHITECTURE.md §1` | Phase 1 KEEP；Phase 3 §3.2 Web surface 减法 + §3.3 data authority 合并 |
| `apps/music-android/` | 对外 Android Player 3.1；CI release 唯一 Android 工程 | 是 | **KEEP** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + §2.3 | Phase 1 KEEP |
| `apps/android/` | 第二 Android 工程；功能更多但与 release authority 重复 | 否（双 authority） | **MERGE → 退役** | `MOODIFY_PRODUCT_AUDIT.md §5.1 A` | Phase 3 §3.1 |
| `apps/ear-workbench/` | 内部研究工具；操作员界面 | 否（内部） | **FREEZE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 1 FREEZE；不进入公开导航 |
| `apps/` 其他子包（如 `music-web/` 未观察 / 残余 scaffold） | 见 `MOODIFY_PRODUCT_AUDIT.md §5.1` | — | 已在 §5.1 列出 | — | Phase 2-3 |

### 1.2 服务 / 包 / Core

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `moodify-core-package/` | 内部 Ear 能力中心；`v01_pipeline` 主线 + `data_factory` + auditory / reconstruction 子包 | 是（作为内部能力） | **KEEP**（子包级分类） | `INTERNAL_SYSTEMS.md §1-2` + `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 结构调整；子包拆出 research profile |
| `moodify-core-package/src/moodify/auditory` 等 | Ear 内部子包；listen / represent / judge / evidence | 是（内部） | **KEEP** | `INTERNAL_SYSTEMS.md §1` | 保留 |
| `moodify-core-package/.../reconstruction_job` | Reconstruction Job；含未完成 billing | 否（生产 case 未到） | **FREEZE** | `INTERNAL_SYSTEMS.md §3` | Phase 2 FREEZE；执行需 `CANON_CHANGE = YES` |
| `moodify-core-package/.../era_diagnostic` / `identity_guard` / `reconstruction_objective` | 未合并分支承载的重建系列 | 否 | **FREEZE / MERGE**（按需） | `REPOSITORY_STATUS.md` 表格 | Phase 2-3 |
| `moodify-music-package/` | Music BFF + Music Data API + Music SQLAlchemy data authority + Alembic | 是（部分） | **KEEP / MERGE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.3` | Phase 3 §3.3 data authority 合并（`CANON_CHANGE = YES`） |
| `moodify-music-package/.../bff` | 唯一公开 Music BFF | 是 | **KEEP** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | 保留 |
| `moodify-music-package/.../api` | Music Data API（与 BFF 平行） | 否（双层 surface） | **MERGE → 退役** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 3 §3.4 |
| `moodify-music-package/models.py` + Alembic | Music data authority（结构） | 是 | **KEEP**（结构） | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.3` | 结构 KEEP；schema 合并需 `CANON_CHANGE = YES` |
| `moodify-pulse/` | Electron 桌面 Player；第二产品身份 "AI Emotional Music Container"；mock data | 否（第二产品 + mock） | **DELETE 候选** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.1 B` + `REDUCTION_PLAN.md Phase 3 §3.5` | Phase 3 §3.5（先提取必要 Windows 播放代码） |
| `moodify-qa/` | 独立 QA API（两个入口）+ 独立 SQLite + Core 分析复制 | 否（Canon 冲突） | **DELETE 候选** | Delta §2 D-1 + `MOODIFY_PRODUCT_AUDIT.md §4 表` + `REDUCTION_PLAN.md Phase 3 §3.4` | Phase 1 候选；需 owner 签字 + 30 天观测 |
| `moodify-qa-desktop/`（未跟踪） | Electron 桌面壳；依赖 moodify-qa | 否（第三桌面 + 第二产品） | **DELETE 候选** | Delta §2 D-1 + `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 1 候选；`.gitignore` 保护 |
| `moodify_experimental/` | MAMSE / research 资产 | 否（research） | **FREEZE → research profile** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.2` | Phase 2 拆出 research profile |

### 1.3 engine / products / shared / sdk

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `engine/` | Facade + compatibility bootstrap；反向委托 Core；主要被 demo 使用 | 否（永久 shim） | **MERGE → 退役** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.1 E` | Phase 3 §3.4 |
| `engine/report_schema` | Demo report schema | 否（demo） | **FREEZE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `products/`（qa / master / rating / supply） | 空 `__init__.py` + README + config；4 个不存在的公开产品 | 否（空壳） | **DELETE 候选** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.2` | Phase 1 |
| `shared/` | 新架构壳；空代码 + README | 否（空壳） | **DELETE 候选** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.2` | Phase 1 |
| `sdk/` | placeholder client + 未实现 async client；无公开 API authority | 否 | **DELETE 候选** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.2` + `REDUCTION_PLAN.md Phase 1` | Phase 1（30 天下载核验 + owner 签字） |

### 1.4 demo / research / examples / benchmark

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `demo/` | Demo Intelligence Report 入口 | 否（内部演示） | **FREEZE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `research/` | 研究子包；benchmarks + 工具 | 否（research） | **FREEZE → research profile** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `§5.2` | Phase 2 拆出 research profile |
| `research/benchmarks/baseline.py` + `benchmark/baseline.py` | 完全相同 | 否（重复） | **DELETE 候选（保留一份）** | `MOODIFY_PRODUCT_AUDIT.md §5.2` | Phase 1 |
| `examples/` | golden_case / 配置文件 | 否（demo） | **FREEZE / ARCHIVE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` + `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `benchmark/` | 旧 benchmark 资产 | 否（research） | **FREEZE → research profile** | 同上 | Phase 2 |

### 1.5 ops / ops/web_origin / docker / 部署

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `ops/` | 实际运行 runbook + 三站 origin + 部署脚本 | 是（运行必需） | **KEEP / MERGE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 1-2 删除打包快照和重复站点源 |
| `ops/web_origin/site/rongjingmusic/` | Product Home 站点源；Brand + Listen Demo v0.1 runbook | 是 | **KEEP** | `CURRENT_CANON.md §3 不变量 #7` + Delta §1.2 | Phase 1 KEEP |
| `ops/web_origin/site/rongjingwenchuan/` | Company Home 站点源 | 是 | **KEEP** | `PUBLIC_BRAND_CONSTITUTION.md §7` | 保留 |
| `ops/data_node/` / `ops/ear_batch/` / `ops/cloud_capabilities/` | 云端运维 + Ear API/worker | 是（内部） | **KEEP**（内部） | `CURRENT_ARCHITECTURE.md §1` + `INTERNAL_SYSTEMS.md §2` | 保留 |
| Root `Dockerfile` + `docker-compose.yml` + worker Docker | 多 facade + future Redis/nginx 设计 | 否（重复 facade） | **MERGE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 3 §3.4（与真实部署对齐后只留一个 compose） |

### 1.6 docs / artifacts / 审查包 / windows版本开发

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `docs/canon/` | Canon（CANONICAL 第 3 级） | 是 | **KEEP** | `AUTHORITY_ORDER.md` | 保留 |
| `docs/brand/public/` | Public Brand 主题权威 | 是 | **KEEP** | `AUTHORITY_ORDER.md` + `PUBLIC_BRAND_CONSTITUTION.md` | 保留 |
| `docs/REPOSITORY_STATUS.md` | 状态入口（第 5-6 级之间） | 是 | **KEEP** | `AUTHORITY_ORDER.md` | 保留 |
| `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` | 分类政策 | 是 | **KEEP** | `AUTHORITY_ORDER.md` | 保留 |
| `docs/canon/PRODUCT_MAINLINE_INCLUSION_20260820.md` | execution inventory（execution 用，非 authority） | 是 | **KEEP** | 自身 Status | 保留 |
| `docs/public-form/package-01..10` | Public Form 10 包（部分已吸收） | 部分（已被 Canon 吸收） | **KEEP 摘要 + ARCHIVE 子包** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 ARCHIVE |
| `docs/product-framework/` 中 superseded | superseded 旧 product framework | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `docs/engineer/YYYY-MM-DD` | 工程笔记 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `docs/contracts/music/` | API contract | 是 | **KEEP** | `REPOSITORY_STATUS.md` | 保留 |
| `docs/releases/v1.0.0-rc.1.md` 等 | release notes | 是 | **KEEP** | `REPOSITORY_STATUS.md` | 保留 |
| `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md` | INTERNAL Ear 架构 | 是（INTERNAL） | **KEEP** | `AUTHORITY_ORDER.md` 表 | 保留；按需加载 |
| `docs/ASSET_MODEL.md` | INTERNAL 认知基础设施 | 是（INTERNAL） | **KEEP** | `AUTHORITY_ORDER.md` 表 | 保留；按需加载 |
| `docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md` | 内部生产哲学 v1.0 | 是（INTERNAL） | **KEEP** | `CURRENT_CANON.md §5` + `CANON_CHANGELOG.md CD-014` | 保留；按需加载 |
| `MOODIFY_PRODUCT_AUDIT.md` + `REDUCTION_PLAN.md` + `AI_CONTEXT_OPTIMIZATION.md` | 治理基线 | 是 | **KEEP** | `MAINLINE_DECLARATION.md §0 表` | 保留 |
| `docs/reduction/`（`MAINLINE_DECLARATION.md` + `PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` + 本套 6 份 v1 文件） | 主线声明 + Delta + 6 份冻结边界 | 是 | **KEEP** | 本会话 | 保留 |
| `artifacts/`（956 文件） | 生成证据 | 部分（不可替代证据） | **ARCHIVE**（仅留索引 + hash） | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `artifacts/mamse_*` | MAMSE 16 组 | 否（research） | **ARCHIVE → research profile** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `artifacts/mfy_*` | 历史执行包 | 否（执行包） | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `artifacts/ear_batch/v1/` | Ear batch 证据 | 部分（运行时） | **KEEP 运行时 / ARCHIVE 历史** | `INTERNAL_SYSTEMS.md §2` | Phase 2 |
| `审查包/`（382 文件） | 重复任务书 + 报告包 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `windows版本开发/`（330 文件） | 历史 Windows 开发 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |

### 1.7 schemas / security / scripts / tests / 其它

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| `schemas/` | schema 资产 | 部分 | **FREEZE / ARCHIVE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `security/` | threat-model 等 | 部分 | **KEEP / FREEZE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | 保留 |
| `scripts/` | 受控生产 / 工具脚本（部分） | 部分 | **KEEP 受控生产 / ARCHIVE 临时** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `tests/` | 部分测试；MAMSE / benchmark / experimental | 部分 | **KEEP 主线 / FREEZE research** | `MOODIFY_PRODUCT_AUDIT.md §5.2` | Phase 2 拆出 research profile |
| `deliverables/` | APK / release 资产 | 是（发布） | **KEEP checksums/manifest / 外部 release** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `inspection_reports/` / `listening_test/` / `phys-lab/` / `pre-music/` | 内部演示 / 听评 / 历史资产 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `moodify-app/` / `moodify-bridge/` / `moodify-system/` / `moodify_runtime/` / `RJWC_VideoPack_System/` | 旧系统壳 / runtime | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `treatment_records/` | 实验 treatment 记录 | 否 | **ARCHIVE** | `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 2 |
| `experiments/` / `science/` / `models/` / `plugins/` / `marketplace/` | 研究 / 平台壳 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `07Music/` / `asset-registry/` / `cloud_data/` / `configs/` / `data/` / `local_audio_assets/` / `night/` / `output/` / `outputs/` / `project_analytics/` / `shared-fixtures/` / `third_party/` / `tools/` / `uploads/` / `video/` / `workers/` / `_github_moodify_ai/` / `Moodify_Deep_Ear_Diagnostic_Pack_v0.1.1/` / 中文根目录（`实验图片` / `工程预算` / `项目ppt` / `研究材料` / `投资资料`） | 大量生成 / 历史 / 临时 / 重复资产 | 否 | **ARCHIVE** | `AI_CONTEXT_OPTIMIZATION.md §3` | Phase 2 |
| `scratch/` / `temp/` / `tmp/` | 临时目录 | 否 | **不提交 / gitignore** | `MOODIFY_PRODUCT_AUDIT.md §5.2` | Phase 1 |
| Root 安装器 / 压缩快照 / 临时目录 | 根目录打包产物 | 否 | **DELETE 候选** | `MOODIFY_PRODUCT_AUDIT.md §5.2` | Phase 1 |

### 1.8 状态机 / Job authority

| 模块 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 | Canon Change |
|---|---|---|---|---|---|---|
| `moodify/orchestration/workflow_engine.py` | LEGACY workflow engine | 否（LEGACY） | **DELETE 候选** | `INTERNAL_SYSTEMS.md §3` + `MOODIFY_PRODUCT_AUDIT.md §4 表` | Phase 3 §3.4 | NO |
| `node`（moodify-node worker） | CANONICAL（云端队列实跑） | 是 | **KEEP** | `INTERNAL_SYSTEMS.md §3` + P00 TT-009 | 保留 | NO |
| `data_factory` | CANONICAL（pilot 10/10） | 是 | **KEEP** | `INTERNAL_SYSTEMS.md §3` + P00 TT-008 | 保留 | NO |
| `reconstruction_factory` | EXPERIMENTAL | 否（EXPERIMENTAL） | **FREEZE** | `INTERNAL_SYSTEMS.md §3` + P00 TT-013 | Phase 2 | NO |
| 单一 authoritative state machine 统一方案 | 控制面任务 | — | **HUMAN_DECISION_REQUIRED** | `CANON_CHANGELOG.md CD-015` | Phase 3+ | **YES**（若执行统一） |

### 1.9 云端现状（`CURRENT_ARCHITECTURE.md §1` 引用）

| 节点 | 当前作用 | 是否服务主线 | 决定 | Canon Evidence | 阶段 |
|---|---|---|---|---|---|
| LA VPS 103.144.246.242（亿速云，核心节点） | nginx + cloudflared + moodify-api(:8000) + moodify-music(:3100) + music-bff(:8100) + worker + audiolla | 是（运行） | **KEEP**（运行必需） | `CURRENT_ARCHITECTURE.md §1` | Phase 4 维持 |
| 杭州 VPS 120.55.191.146（阿里云） | moodify-api(:8000 公网) + moodify-data-worker + 4 timers + /var/lib/moodify (6.5GB 历史) | 是（运行） | **KEEP** | `CURRENT_ARCHITECTURE.md §1` | Phase 4 维持 |
| PolarDB（3 实例） | MySQL 8.0.13 空壳 / MySQL 8.0.18 moodify_dev 19 表 ≈0 / PG 16.14 在线未用 | 否（BLOCKED） | **FREEZE**（核验后决定） | `CURRENT_ARCHITECTURE.md §1` | Phase 3 §3.3（data authority 合并时核验） |
| OSS/S3/R2 | NOT_PROVISIONED | 否 | **NOT-PROVISIONED** | `CURRENT_ARCHITECTURE.md §1` | 不动 |
| 云端 AI 推理 | 无 | 否 | **NOT-PROVISIONED** | `CURRENT_ARCHITECTURE.md §1` | 不动 |

---

## 2. 决定分布统计

| 决定 | 数量 | 占比 |
|---|---:|---:|
| KEEP | 主线 Web / Android / BFF / Music data authority（结构） / Ear 内部核心 / Listen Demo v0.1 / 三站 / 8-12 治理入口 / 节点运行 / 历史 production 关键脚本 | 小（少数模块承担主线） |
| FREEZE | Ear 重建系列 + Reconstruction Job + MAMSE + research 子包 + Ear Workbench + Creator / License / Support / CWC / Passport / Bridge + Music Data API 平行 + Web Drizzle + 歌单 + 历史审查包 + reconstruction_factory + demo + research | 部分 |
| ARCHIVE | `artifacts/` / `审查包/` / `windows版本开发/` / 大量生成与临时资产 + `examples/` / 中文根目录工作包 | 大 |
| DELETE CANDIDATE | `products/` / `shared/` / `sdk/` / `moodify-qa/` / `moodify-qa-desktop/` / `moodify-pulse/` / `moodify/orchestration/workflow_engine.py` / 第二 Android / `engine/` facade / `moodify-pulse` 必要播放代码提取后 / 重复 baseline / `scan_err.txt` / 中文工作包压缩快照 / 冲突 QA 产品化方向 2 份文档 | 中 |
| MERGE | `apps/android/` → `apps/music-android/` / `engine/` → Core / `moodify-music-package/.../api` → BFF / `apps/web/lib/db/schema.ts` → SQLAlchemy / Root Docker → 单 compose | 部分 |

---

## 3. 主线工作集目标（基线 → 收敛）

按 `AI_CONTEXT_OPTIMIZATION.md §7` 验收指标：

| 场景 | 当前估计 | 目标 |
|---|---:|---:|
| 新 agent 判断产品身份 | 跨 10+ 文档 | **4 个 Canon 入口内** |
| 定位运行主链 | 多 architecture / status / report | **1 Current Architecture + 1 Runbook** |
| 定位历史证据 | 全仓 `rg` | **1 Archive/Evidence Index** |
| 理解公开产品 | 多站点多产品 README | **1 Public Brand + 1 Player README** |
| 默认检索文件数 | 3,300 tracked | **500-800 主线文件** |

**目标判定：KEEP + FREEZE + ARCHIVE 物理隔离后，主线工作集（默认加载 + 按需加载）= 500-800；ARCHIVE 目录默认工具与 AI 排除；DELETE 候选在 owner 签字后消失。**

---

## 4. 与 `docs/reduction/MAINLINE_DECLARATION.md` 的关系

`MAINLINE_DECLARATION.md` 是单一文件整合；本文件是按用户任务清单 Part 3 的**逐模块分类地图**。两者不冲突：

- `MAINLINE_DECLARATION.md §2` 的 KEEP / FREEZE / ARCHIVE / DELETE CANDIDATE 列表 = 本文件 §1-4 的子集（声明视角）；
- 本文件 §1-4 的 per-module inventory = 更细的路径级 + 阶段归属 + Canon Change 标注（执行视角）。

Phase 1+ 的物理动作以本文件 §1-4 + `EXECUTION_PLAN_V1.md` 为入口；`MAINLINE_DECLARATION.md` 提供共享地图与决策原则。

---

## 5. 本文件**不**做的事

- **不**修改 `docs/canon/*` / `docs/brand/public/*` / `AGENTS.md` / `MOODIFY_PRODUCT_AUDIT.md` / `REDUCTION_PLAN.md` / `AI_CONTEXT_OPTIMIZATION.md`。
- **不**移动 / 删除任何文件。
- **不**声明 `CANON_CHANGE`（仅在表中标注哪些候选若执行需 `CANON_CHANGE = YES`）。
- **不**授权 mass-delete。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**