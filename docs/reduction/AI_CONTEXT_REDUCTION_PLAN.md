# Moodify AI Context Reduction Plan — 2026-08-24

**任务：** Moodify Entropy Reduction 001 — Establish Mainline Product Boundary
**性质：** AI 上下文减法计划（5 文件入口 + 按需加载 + archive + 外部存储四层）；为 Phase 2 物理隔离提供 **AI 与工程师共享入口**。
**权威：** 引用 `AI_CONTEXT_OPTIMIZATION.md §2-7` + `MOODIFY_PRODUCT_AUDIT.md §6.3` + `MAINLINE_DECLARATION.md §4` + `ENTROPY_MAP_V1.md §1-3`。
**目标：** 未来 AI Agent **5 文件以内**理解 Moodify（`AI_CONTEXT_OPTIMIZATION.md §7` + `MAINLINE_DECLARATION.md §4.1`）。
**CANON_CHANGE：** `NO`。
**执行状态：** 仅计划。**未修改、删除、移动任何业务代码、目录或既有文档。**

---

## 0. 当前 AI 上下文问题

按 `AI_CONTEXT_OPTIMIZATION.md §1` + `MOODIFY_PRODUCT_AUDIT.md §2.1`：

1. **文件数过多**：默认仓库上下文 ≈ 3,300 tracked files；`docs/` ≈ 275 文件（≈246 MD）。
2. **token 浪费来源**：
   - 同一决策在 master task / execution prompt / report / acceptance / final response 重复；
   - 历史文件仍使用 `CURRENT / LIVE / APPROVED`，迫使 AI 逐份做 authority 仲裁；
   - 生成 artifact 与源代码同仓；
   - `docs` 同时承载 Canon + 当前操作 + 设计 + 计划 + 研究 + 历史；
   - 根目录存在大量中文工作包、压缩快照、临时目录、旧产品入口；
   - Core package 同时包含 Canonical + Experimental + Legacy，默认 import 与文档入口没有物理隔离。
3. **CI / 发布 authority 与文档 authority 漂移**：Android release 只构建 `apps/music-android`，不是 `apps/android`；Windows release 当前构建 `moodify-pulse`，与 Canon 冲突。
4. **AI 工具默认检索 vs 默认排除不分**：当前没有 `default_context.include/exclude` 路由。

---

## 1. 默认加载（5 文件入口）

> 任何 agent 默认启动只加载以下 5 个文件即可回答："Moodify 是什么 / 现在主线是什么 / 公开产品面 / 内部入口 / 决策原则 / 主要 freeze 候选"。

| # | 路径 | 角色 | Authority Order |
|---|---|---|---|
| 1 | `AGENTS.md` | 仓库最高认知入口 | 第 2 级 |
| 2 | `docs/canon/CURRENT_CANON.md` | 当前产品身份 | 第 3 级 |
| 3 | `docs/canon/PRODUCT_BOUNDARY.md` | 内外边界 | 第 3 级 |
| 4 | `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | 最高 Public Brand 主题权威 | 第 3 级（主题权威） |
| 5 | `docs/reduction/MAINLINE_DECLARATION.md` | 主线声明 + 共享地图入口 | 治理入口（非 Canon） |

**为什么是这 5 个？**

- 1+2+3 → 锁产品身份、用户动作、内外边界；
- 4 → 锁公开语言 Tier A/B/C/D、5 项测试、三站职责；
- 5 → 把 12 份治理文件整合为单一地图入口（避免新治理文档成为第二权威）。

---

## 2. 按需加载（受任务触发）

> 不进入默认检索；当任务涉及对应主题时加载。

| 路径 | 何时读 |
|---|---|
| `docs/canon/CURRENT_ARCHITECTURE.md` | 涉及运行时 / 部署现状判断（"现在跑着什么 / PolarDB / OSS / 队列 / worker"） |
| `docs/canon/INTERNAL_SYSTEMS.md` | 涉及 Ear / Cloud Production / state machine authority |
| `docs/canon/AUTHORITY_ORDER.md` | 指令冲突需要裁决 |
| `docs/canon/CANON_CHANGELOG.md` | 需要查看 Canon 变更留痕 |
| `docs/brand/public/README.md` | Public Brand 主题细化（language registry / site routing / public surface inventory） |
| `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` | Canonical / Experimental / Legacy / Historical 分类 |
| `docs/ASSET_MODEL.md`（INTERNAL） | 认知基础设施涉及 |
| `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`（INTERNAL） | Ear 架构涉及 |
| `docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md`（内部生产哲学） | 重建生产哲学涉及（对外表述已被 Canon 覆盖） |
| `MOODIFY_PRODUCT_AUDIT.md` | 减法 / 价值评级判断（涉及 KEEP/FREEZE/DELETE 候选） |
| `REDUCTION_PLAN.md` | Phase 1-4 执行（涉及物理动作） |
| `AI_CONTEXT_OPTIMIZATION.md` | AI 上下文优化具体实施（涉及 include/exclude 路由） |
| `docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md` | 本会话 / 后续 Delta 审计 |
| `docs/reduction/CORE_PRODUCT_V1.md` | 主线产品身份详细论证 |
| `docs/reduction/PRODUCT_BOUNDARY_V1.md` | KEEP / FREEZE / ARCHIVE / DELETE CANDIDATE 分类入口 |
| `docs/reduction/ENTROPY_MAP_V1.md` | 逐模块路径级分类 + 阶段归属 |
| `docs/reduction/MOODIFY_MAINLINE_ARCHITECTURE.md` | 主线架构图（不是新理想图） |
| `docs/reduction/EXECUTION_PLAN_V1.md` | Phase 1-4 执行计划（涉及物理动作） |
| 当前 API contract 与数据库 migration | 涉及 catalogue / track / playback / favorite / recent-play |
| 当前 release acceptance、风险与回滚记录 | 涉及发布 / 回滚 |
| 人类听评记录和不可重建的证据索引 | 涉及 evidence authority（按 ARCHIVE_INDEX.md 定位） |

---

## 3. Archive（不进入默认检索，通过 ARCHIVE_INDEX.md 定位）

> 按 `REDUCTION_PLAN.md Phase 2` + `AI_CONTEXT_OPTIMIZATION.md §3` + `ENTROPY_MAP_V1.md §1.6-1.7`。

**3.1 整目录 ARCHIVE（默认排除）**

| 目录 | 内容 | 处理方式 |
|---|---|---|
| `archive/audits/2026-08/`（来自 `审查包/`，382 文件） | 重复任务书 + 报告包 + 模板 | 去嵌套；保留 manifest + 最终报告 + 不可替代证据 |
| `archive/windows-development/`（来自 `windows版本开发/`，330 文件） | 历史 Windows 开发 | 保留 release/tag 对应记录 |
| `archive/evidence/`（来自 `artifacts/`，956 文件） | 生成证据 | 不可替代证据保留；其余按 hash manifest 索引 |
| `archive/patches/`（来自 `补丁包/`） | 补丁包 | 按 commit/tag 建索引 |
| `archive/public-form/2026-08/`（来自 `docs/public-form/package-01..10`） | Public Form 包（部分已被 Canon 吸收） | 只留决议摘要与验收 |
| `archive/product-framework/`（来自 `docs/product-framework/` 中 superseded） | superseded product framework | 文件头统一标记 superseded + successor |
| `archive/engineering-notes/`（来自 `docs/engineer/YYYY-MM-DD`） | 工程笔记 | 研究推理按日期归档 |
| `archive/non-runtime/`（来自 `研究论文/` / `投资ppt/` / `实验图库/`） | 非运行时资产 | 与源码主线物理隔离 |

**3.2 部分 / 子包 ARCHIVE（按需）**

| 目录 | 内容 | 处理方式 |
|---|---|---|
| `artifacts/mamse_*` | MAMSE 16 组 | 入 `archive/evidence/mamse/`；Git 只留 manifest + hash + summary + 再生成命令 |
| `artifacts/mfy_*` | 历史执行包 | 入 `archive/evidence/mfy/`；不可重建证据例外 |
| `artifacts/ear_batch/v1/`（运行时部分除外） | Ear batch 历史 | KEEP 运行时 / ARCHIVE 历史 |
| `examples/` / `deliverables/` / `data/` / `inspector_reports/` / `listening_test/` / `phys-lab/` / `pre-music/` / `RJWC_VideoPack_System/` / `research/`（部分子包） | 演示 / 配置 / 历史 | 按需入 archive |
| `schemas/` / `security/`（部分）/ `scripts/`（临时）/ `tests/`（research） | schemas / security / scripts / tests 部分 | KEEP 主线 / ARCHIVE 临时 |
| `moodify-app/` / `moodify-bridge/` / `moodify-system/` / `moodify_runtime/` | 旧系统壳 / runtime | ARCHIVE |
| `treatment_records/` / `experiments/` / `science/` / `models/` / `plugins/` / `marketplace/` | 研究 / 平台壳 | ARCHIVE |
| `07Music/` / `asset-registry/` / `benchmark/` / `calibration_reports/` / `cloud_data/` / `configs/` / `local_audio_assets/` / `night/` / `output/` / `outputs/` / `project_analytics/` / `shared-fixtures/` / `third_party/` / `tools/` / `uploads/` / `video/` / `workers/` / `_github_moodify_ai/` / `Moodify_Deep_Ear_Diagnostic_Pack_v0.1.1/` | 大量生成 / 历史 / 临时 / 重复资产 | ARCHIVE |
| 中文根目录（`实验图片` / `工程预算` / `项目ppt` / `研究材料` / `投资资料`） | 中文工作包 | ARCHIVE |
| `scratch/` / `temp/` / `tmp/` | 临时目录 | 不提交 / `.gitignore` |

**3.3 索引层：ARCHIVE_INDEX.md（待建）**

按 `REDUCTION_PLAN.md Phase 2` + `AI_CONTEXT_OPTIMIZATION.md §3` + `MAINLINE_DECLARATION.md §4.3`：

- 路径：`docs/ARCHIVE_INDEX.md`（Canon 不变量之外；与 `docs/REPOSITORY_STATUS.md` 同级）
- 必填字段：artifact id / case id / hash / 生成版本 / 存储位置 / 可重建命令 / 保留策略
- 默认 AI 工具排除 `archive/**`；通过 ARCHIVE_INDEX.md 检索

---

## 4. 外部存储（不在仓库内）

> 按 `AI_CONTEXT_OPTIMIZATION.md §4` + `ENTROPY_MAP_V1.md §1.9`。

| 内容 | 建议位置 |
|---|---|
| 完整 `moodify-music-package` 数据备份 | PolarDB（核验通过后）+ 外部对象存储 |
| ops LA / 杭州部署快照 | LA VPS / 阿里云 / Cloudflare（核验后） |
| 生成 audio artifact（Cadeau10 wav 等） | `ops/web_origin/site/rongjingmusic/audio/`（已部署于 LA 媒体根，不入 git） |
| 投资人路演 / 内部 PPT | 外部存储（不入 git） |
| 历史 release APK / 安装器 | GitHub Releases（Git 只留 checksums/manifest） |

---

## 5. AI 默认检索路由（建议）

按 `AI_CONTEXT_OPTIMIZATION.md §6`（需单独变更任务；在 root `AGENTS.md` 后增加机器可执行路由；本文件不修改 `AGENTS.md`）：

```yaml
default_context:
  include:
    - AGENTS.md
    - docs/canon/**
    - docs/brand/public/**
    - docs/REPOSITORY_STATUS.md
    - docs/LEGACY_AND_EXPERIMENTAL_POLICY.md
    - docs/reduction/MAINLINE_DECLARATION.md       # 共享地图入口
  exclude:
    - archive/**
    - artifacts/**
    - 审查包/**
    - windows版本开发/**
    - '**/generated/**'
    - 'artifacts/mamse_*'                            # research 隔离
    - 'artifacts/mfy_*'                              # 执行包隔离
on_demand:
  evidence: docs/ARCHIVE_INDEX.md
  public_brand: docs/brand/public/README.md
  auditory_research: research/README.md
  delta: docs/reduction/PROJECT_ENTROPY_AUDIT_DELTA_2026-08-24.md
  product_audit: MOODIFY_PRODUCT_AUDIT.md
  reduction_plan: REDUCTION_PLAN.md
  mainline_boundary:
    - docs/reduction/CORE_PRODUCT_V1.md
    - docs/reduction/PRODUCT_BOUNDARY_V1.md
    - docs/reduction/ENTROPY_MAP_V1.md
    - docs/reduction/MOODIFY_MAINLINE_ARCHITECTURE.md
    - docs/reduction/AI_CONTEXT_REDUCTION_PLAN.md
    - docs/reduction/EXECUTION_PLAN_V1.md
```

**执行注意：** 上路由是**建议**；写入 `AGENTS.md` 是单独的 Canon-affecting 任务，须走 `CANON_CHANGE` 流程（`AGENTS.md §Canon Change Rule`）。

---

## 6. 每个主线目录只保留一个 README.md（建议）

按 `AI_CONTEXT_OPTIMIZATION.md §6`：

每个主线目录只保留一个 `README.md`，固定包含：

```text
1. Role
2. Authority
3. Entrypoint
4. Tests
5. Dependencies
6. Non-goals
7. Owner
8. Last verified
```

---

## 7. Token 预算目标

按 `AI_CONTEXT_OPTIMIZATION.md §7` + `MAINLINE_DECLARATION.md §7` + `ENTROPY_MAP_V1.md §3`：

| 场景 | 当前估计 | 目标 |
|---|---:|---:|
| 新 agent 判断产品身份 | 跨 10+ 文档 | **4 个 Canon 入口内** |
| 定位运行主链 | 多 architecture / status / report | **1 Current Architecture + 1 Runbook** |
| 定位历史证据 | 全仓 `rg` | **1 Archive/Evidence Index** |
| 理解公开产品 | 多站点多产品 README | **1 Public Brand + 1 Player README** |
| 默认检索文件数 | 3,300 tracked | **500-800 主线文件** |
| 任意 agent 默认加载 | 10+ MD | **5 MD** |
| 任意 agent 回答 Core Product / 公开入口 / 内部入口 / 数据 authority / 测试命令 | — | **5 文件内** |

**验收指标：**

- [ ] 任何 agent 在读取 5 个文件内能回答 Core Product / 公开入口 / 内部入口 / 数据 authority / 测试命令；
- [ ] 搜索 `Status: CURRENT/LIVE/APPROVED` 时，默认上下文不出现互相冲突的低级文档；
- [ ] 生成 artifact 不进入 Git diff，除非它是签字或不可重建证据；
- [ ] 每个历史包只有一个索引入口（ARCHIVE_INDEX.md），不再嵌套复制完整目录。

---

## 8. 风险与缓解

按 `AI_CONTEXT_OPTIMIZATION.md §8`：

| 风险 | 缓解 |
|---|---|
| 过度压缩会损失研究 provenance | content-addressed archive + Evidence Index；不在主线保留全部副本 |
| 移动文档会破坏链接 | link checker + redirect map 验证 |
| Git 历史本身不是易用归档 | 人类签字和外部证据仍需稳定存储位置 |
| 涉及 evidence authority 的删除 / 迁移可能是 Canon Change | 执行前必须明确声明 `CANON_CHANGE = YES` |
| AI 工具 include/exclude 路由写入 `AGENTS.md` 是 Canon-affecting | 单独走 Canon Change 流程 |
| 5 文件入口 vs 12 治理文件并存 | 5 文件是 AI 入口；12 治理文件保留作按需加载；不重复内容，只做索引 |

---

## 9. 本文件**不**做的事

- **不**修改 `AGENTS.md` / `docs/canon/*` / `docs/brand/public/*` / `MOODIFY_PRODUCT_AUDIT.md` / `REDUCTION_PLAN.md` / `AI_CONTEXT_OPTIMIZATION.md`。
- **不**创建 `docs/ARCHIVE_INDEX.md`（属于 Phase 2 物理动作；由 `EXECUTION_PLAN_V1.md` 在 owner 授权下执行）。
- **不**把 include/exclude 路由写入 root `AGENTS.md`（Canon Change）。
- **不**移动 / 删除任何文件。
- **不**声明 `CANON_CHANGE`。

---

**本文件结束。等待 Reduction Execution 001：物理隔离 archive/freeze。**