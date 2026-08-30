# Moodify AI Context Optimization

**日期：** 2026-08-24  
**目标：** 降低 AI 与新工程师定位主线所需的文件数、token 数和冲突判断次数。  
**执行状态：** 建议；未移动或删除现有文件。

---

## 1. 当前上下文问题

默认仓库上下文包含约 772 份 Markdown。仅 `artifacts`、`审查包`、`windows版本开发` 就包含约 1,073 份跟踪文件和大量报告、任务书、模板、快照与生成 JSON。它们保存了重要 provenance，但不应与当前 Canon、主线代码和运行文档处于同一默认检索层。

主要 token 浪费来自：

1. 同一决策在 master task、execution prompt、report、acceptance、final response 中重复；
2. 历史文件仍使用 `CURRENT/LIVE/APPROVED`，迫使 AI 逐份做 authority 仲裁；
3. 生成 artifact 与源代码同仓，文件数远高于索引所需；
4. `docs` 同时承载 Canon、当前操作、设计、计划、研究与历史；
5. 根目录存在大量中文工作包、压缩快照、临时目录和旧产品入口；
6. Core package 同时包含 Canonical、Experimental、Legacy，而默认 import 与文档入口没有物理隔离。

---

## 2. 必须长期保留文档

默认 AI 启动只应自动读取以下 8–12 个入口：

| 文档 | 角色 |
|---|---|
| `AGENTS.md` | 仓库最高认知入口 |
| `docs/canon/CURRENT_CANON.md` | 当前产品身份 |
| `docs/canon/PRODUCT_BOUNDARY.md` | 内外边界 |
| `docs/canon/AUTHORITY_ORDER.md` | 冲突裁决 |
| `docs/canon/CURRENT_ARCHITECTURE.md` | 已验证现实，不是理想图 |
| `docs/canon/INTERNAL_SYSTEMS.md` | 内部系统与 authority 边界 |
| `docs/REPOSITORY_STATUS.md` | 当前状态索引 |
| `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` | 分类与删除纪律 |
| `docs/brand/public/README.md` | Public Brand 入口 |
| `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | 公共语言最高主题权威 |
| `docs/RUNBOOK.md`（建议新建） | 本地启动、测试、发布、回滚唯一入口 |
| `docs/ARCHIVE_INDEX.md`（建议新建） | 历史与 Evidence 的可检索索引 |

长期保留但按需读取：

- `docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md`；
- `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md`；
- `docs/ASSET_MODEL.md`；
- 当前 API contract 与数据库 migration；
- 当前 release acceptance、风险与回滚记录；
- 人类听评记录和不可重建的证据索引。

原则：长期保留不等于默认加载。

---

## 3. 应该归档的文档和目录

建议目标：`archive/` 不进入默认 AI 搜索；只通过 `docs/ARCHIVE_INDEX.md` 定位。

| 当前路径 | 目标 | 处理方式 |
|---|---|---|
| `审查包/` | `archive/audits/2026-08/` | 去掉嵌套重复目录；每包保留 manifest、最终报告、不可替代证据 |
| `windows版本开发/` | `archive/windows-development/` | 保留 release/tag 对应记录，移除默认上下文 |
| `补丁包/` | `archive/patches/` | 按 commit/tag 建索引，不作为当前说明 |
| `docs/public-form/package-01..10` | `archive/public-form/2026-08/` | Canon 已吸收的部分只留决议摘要与验收 |
| `docs/product-framework/` 中 superseded 文件 | `archive/product-framework/` | 文件头统一标记 superseded + successor |
| `docs/engineer/YYYY-MM-DD` | `archive/engineering-notes/` | 研究推理按日期归档 |
| `artifacts/mamse_*` | 外部 artifact store 或 `archive/evidence/mamse/` | Git 只留 manifest、hash、summary、再生成命令 |
| `artifacts/mfy_*` 历史执行包 | 外部 artifact store | 同上；不可重建证据例外 |
| `研究论文/`、`投资ppt/`、`实验图库/` | `archive/non-runtime/` | 与源码主线物理隔离 |
| `deliverables/releases` 历史二进制 | GitHub Releases | Git 只留 checksums/manifest |

归档不是删除证据 authority。Evidence Index 必须记录：artifact id、case id、hash、生成版本、存储位置、可重建命令、保留策略。

---

## 4. 应该删除的文档

高置信删除候选：

- 0 字节文件，如 `scan_err.txt`；
- 完全重复且 hash 相同的模板、嵌套副本和生成 JSON；
- 已被 Canon 完整吸收、没有新增证据的重复 final response；
- 与空壳模块绑定、只描述不存在产品的 README：`products/*`、`shared/README.md`、未实现 SDK 宣传；
- 未跟踪临时报告和本地压缩快照，不提交版本库；
- 自动生成、可从 schema/代码稳定重建且无签字/听评价值的中间报告。

条件删除候选：

- `docs/PRODUCTIZATION_REVIEW_AND_V0.1_PLAN_2026-08-24.md` 与 QA 实施计划：方向与当前 Canon 冲突。若人类未批准 Canon Change，应标记 `REJECTED/HISTORICAL` 后归档，而不是保留为当前产品计划。
- 旧 `CURRENT/LIVE/APPROVED` 文档：若内容已被高级 authority 覆盖且无独立 provenance，删除；否则改头为 `HISTORICAL` 并链接 successor。

不得删除：人类签字、听评原始记录、合法/权利证据、不可重建生产证据、迁移/回滚所需 schema、Canon changelog。

---

## 5. 应该重新组织目录

建议目标结构：

```text
/
├── AGENTS.md
├── README.md
├── apps/
│   ├── web/                 # 唯一 Web Player
│   └── android/             # 合并后的唯一 Android Player
├── services/
│   ├── music-bff/           # 唯一公开 API
│   └── production/          # 内部生产入口
├── packages/
│   ├── music-contracts/
│   └── auditory-core/       # 当前 moodify-core-package 主线子集
├── research/
│   ├── auditory/            # MAMSE、physics、calibration 等
│   └── tools/
├── docs/
│   ├── canon/
│   ├── brand/public/
│   ├── operations/
│   ├── development/
│   └── ARCHIVE_INDEX.md
├── tests/
└── archive/                 # 默认工具与 AI 排除
```

这不是一次性 mass move 计划。先建立索引和排除规则，再按依赖图迁移，每次只移动一个 authority 边界。

---

## 6. AI 默认读取规则

建议在根 `AGENTS.md` 后增加机器可执行路由（需单独变更任务）：

```yaml
default_context:
  include:
    - AGENTS.md
    - docs/canon/**
    - docs/REPOSITORY_STATUS.md
    - docs/LEGACY_AND_EXPERIMENTAL_POLICY.md
  exclude:
    - archive/**
    - artifacts/**
    - 审查包/**
    - windows版本开发/**
    - '**/generated/**'
on_demand:
  evidence: docs/ARCHIVE_INDEX.md
  public_brand: docs/brand/public/README.md
  auditory_research: research/README.md
```

并为每个主线目录只保留一个 `README.md`，固定包含：Role、Authority、Entrypoint、Tests、Dependencies、Non-goals、Owner、Last verified。

---

## 7. Token 预算目标

| 场景 | 当前估计 | 目标 |
|---|---:|---:|
| 新 agent 判断产品身份 | 需跨 10+ 文档 | 4 个 Canon 入口内完成 |
| 定位运行主链 | 多个 architecture/status/report | 1 个 Current Architecture + 1 个 Runbook |
| 定位历史证据 | 全仓 `rg` | 先查 1 个 Archive/Evidence Index |
| 理解公开产品 | 多站点、多产品 README | 1 个 Public Brand 入口 + 1 个 Player README |
| 默认检索文件数 | 3,300 tracked | 主线工作集控制在 500–800 文件 |

验收指标：

- 任何 agent 在读取 5 个文件内能回答 Core Product、公开入口、内部入口、数据 authority、测试命令。
- 搜索 `Status: CURRENT/LIVE/APPROVED` 时，默认上下文不出现互相冲突的低级文档。
- 生成 artifact 不进入 Git diff，除非它是签字或不可重建证据。
- 每个历史包只有一个索引入口，不再嵌套复制完整目录。

---

## 8. 风险

- 过度压缩会损失研究 provenance；解决方式是 content-addressed archive + Evidence Index，不是在主线保留全部副本。
- 移动文档会破坏链接；必须用 link checker 和 redirect map 验证。
- Git 历史本身不是易用归档；人类签字和外部证据仍需稳定存储位置。
- 任何涉及 evidence authority 的删除或迁移都可能是 Canon Change，执行前必须明确声明。
