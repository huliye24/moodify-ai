# 01 — Canonical Decision Register

**P01 execution date:** 2026-08-17
**P00 snapshot reference:** 审查包/W01-P00_REPORTS_2026-08-17（05_Truth Table + 06_Conflicts）
**Repository:** huliye24/moodify-ai（origin）+ huliye24/moodify（moodify）
**Branch:** codex/moodify-classic-reconstruction-001
**Base commit:** 98f7b96ee076aaf43224284ca0d0da5d7a903f03

---

## CD-001 — External Product Identity（对外产品身份）

- Conflict: README/AGENTS（本地分支）以「Reconstruction-first listening environment」为对外身份；GitHub main 以「The Ear of AI — Auditory Intelligence System」为产品身份；人类最新方向为 Moodify Music / Player。
- P00 evidence: E03/E04（main 身份=Ear of AI）、E05（本地身份=reconstruction-first）、E18（云端实际=音乐网站+播放）
- Human direction: **唯一对外产品面 = Moodify Music / Player；第一阶段核心用户动作 = PLAY**
- Decision: 对外产品身份固定为 **Moodify Music / Player，核心动作 PLAY**。README/AGENTS 按此收敛。Ear 不再是对外身份。
- Classification: **CANONICAL**
- Affected files: README.md、AGENTS.md、docs/canon/CURRENT_CANON.md、docs/canon/PRODUCT_BOUNDARY.md、docs/REPOSITORY_STATUS.md
- Migration: 本包直接更新高权威入口；GitHub main 合并待 W01-P01 之后的人类裁决（不自动 merge）
- Risks: 与 GitHub main（未合并）仍有差异；与宪法 v1.0 的「Choose→Reconstruct→Play」表述存在解释差（见 CD-014）
- Rollback: git 回退本 commit
- Status: DECIDED（部分 HUMAN_DECISION_REQUIRED，见 CD-014）

## CD-002 — Moodify Ear / Auditory Intelligence

- Conflict: Ear 曾是对外产品身份（main README/AGENTS），本地宪法已将其内部化但产品表述保留「重建优先聆听环境」。
- P00 evidence: E03-E06（身份演变）、E18（云端无 Ear 生产流量）
- Human direction: Ear / Auditory Intelligence = **内部听觉、判断、验证与研究系统**
- Decision: Ear 为 INTERNAL 系统；保留其 Listen/Represent/Judge/Evidence/Uncertainty/Learn/Verify/Controlled Intervention 研究与工程能力；不作为公开产品面。
- Classification: **INTERNAL**
- Affected files: AGENTS.md、README.md、docs/canon/INTERNAL_SYSTEMS.md、docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md（顶部标记）
- Migration: 文档级迁移（本包完成）；代码无需改动
- Risks: 低（不影响运行时）
- Rollback: git 回退
- Status: DECIDED

## CD-003 — Repository Authority Order（仓库权威顺序）

- Conflict: 现行 AGENTS.md 已有 authority order，但未包含 docs/canon/*；历史文档仍可被误读为当前权威。
- P00 evidence: E05（AGENTS 现状）、E11（REPOSITORY_STATUS 落后）
- Human direction: 让下一批 Agent 只需要理解一套 Moodify
- Decision: 权威顺序固定为：
  1. current explicit human instruction
  2. root AGENTS.md
  3. docs/canon/*
  4. verified runtime evidence
  5. canonical main behavior + tests
  6. current subsystem docs
  7. experimental docs
  8. historical / legacy docs
- Classification: **CANONICAL**
- Affected files: AGENTS.md、docs/canon/AUTHORITY_ORDER.md
- Status: DECIDED

## CD-004 — Root README.md

- Conflict: 本地 README 对外身份 = reconstruction-first（引用宪法 v1.0）；人类方向 = Music/Player + PLAY。
- P00 evidence: E05、E18
- Decision: README 重写对外身份为 Moodify Music / Player（PLAY 第一核心动作）；Ear/Reconstruction 为内部能力；保留诚实声明（云端现状、production-ready 边界）。
- Classification: **CANONICAL**
- Affected files: README.md
- Status: DECIDED

## CD-005 — Root AGENTS.md

- Conflict: AGENTS 与 README 一致（reconstruction-first）；需与 P01 方向收敛。
- Decision: AGENTS 固定 External product = Moodify Music/Player、Primary user action = PLAY、Internal systems = Ear 等；加入 Agent Rules（不创建第二对外身份等）。
- Classification: **CANONICAL**
- Affected files: AGENTS.md
- Status: DECIDED

## CD-006 — docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md

- Conflict: 曾是对外产品架构文档；现应降级为内部系统参考。
- P00 evidence: E03（main 以此身份）、E18（云端无对应生产流量）
- Decision: 保留资产（不删除）；顶部加 `Status: INTERNAL` 标记与指向 docs/canon/CURRENT_CANON.md 的说明；不修改其历史内容。
- Classification: **INTERNAL**
- Affected files: docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md（仅顶部标记）
- Status: DECIDED

## CD-007 — docs/ASSET_MODEL.md

- Conflict: 资产模型（Production Case → Evidence → Rule Update）与 P01 方向无冲突；属于内部认知基础设施。
- Decision: 保留，分类 INTERNAL（认知基础设施），顶部标注权威层级（不覆盖 docs/canon/*）。
- Classification: **INTERNAL**
- Affected files: docs/ASSET_MODEL.md（仅顶部标记，可选）
- Status: DECIDED

## CD-008 — docs/LEGACY_AND_EXPERIMENTAL_POLICY.md

- Conflict: 政策文档本身是权威政策（分类体系），与 P01 方向兼容。
- Decision: 保留为 CANONICAL 政策（属 docs/canon 体系之外的既有政策）；在 docs/canon/AUTHORITY_ORDER.md 中引用。
- Classification: **CANONICAL**
- Affected files: 无（仅引用）
- Status: DECIDED

## CD-009 — docs/REPOSITORY_STATUS.md

- Conflict: baseline 为 2026-08-08（0b355e7）、身份=Ear of AI，明显落后（E11）。
- Decision: 从「历史静态快照」改为「当前 Canon 与事实状态的入口」：顶部指向 docs/canon/*，更新身份表述，保留历史基线记录为历史附录。
- Classification: **MIGRATION_PENDING → 本包内完成（重写为入口文档）**
- Affected files: docs/REPOSITORY_STATUS.md
- Status: DECIDED

## CD-010 — Android 产品表面

- Conflict: apps/android（Ear 工作台）与 apps/music-android（Moodify Music 3.1）双表面。
- P00 evidence: E25 系（TT-025/026：Ear 工作台 VERIFIED、Music 3.1 发布）
- Decision: Moodify Music Android（music-android）= 对外产品面（CANONICAL）；apps/android（Ear workbench）= INTERNAL 工具。
- Classification: **CANONICAL（music-android）/ INTERNAL（apps/android）**
- Affected files: 文档层（README 产品结构描述）；不修改代码
- Status: DECIDED

## CD-011 — Moodify Music / Player 身份

- Conflict: 无冲突（人类方向明确）；但品牌命名细节（Music vs Player 的对外命名、域名品牌 rongjingmusic.com）未裁决。
- Decision: 身份 = Moodify Music / Moodify Player（CANONICAL）；**具体对外命名与品牌表现 → HUMAN_DECISION_REQUIRED**（不猜）。
- Classification: **CANONICAL（部分）/ HUMAN_DECISION_REQUIRED（命名细节）**
- Status: PARTIAL — HUMAN_DECISION_REQUIRED（命名细节）

## CD-012 — Cloud / Runtime 文档

- Conflict: 云端实际 = 2 VPS + 静态站 + API 壳 + 批处理（E18），与仓库内文档声称的完整能力有差距。
- Decision: 云端现状以 P00 03 报告为事实依据；Canon 中不得虚构云端能力（R2/R6/R10）。云端生产拓扑归 W01-P02。
- Classification: **INTERNAL（现状）/ MIGRATION_PENDING（生产化）**
- Affected files: docs/canon/CURRENT_ARCHITECTURE.md（现状如实写）
- Status: DECIDED（拓扑 P02）

## CD-013 — PR #21 产品身份部分

- Conflict: PR #21（data factory）是冻结协议 KEEP 的 canonical carrier（E12），但其产品表述仍为旧身份语言。
- Decision: 能力与产品哲学分离评估（详见 06_PR21_CANONICAL_COMPATIBILITY.md）：其工程资产（data factory、worker、evidence）→ 评估后保留为 INTERNAL/CANONICAL 候选；其旧产品表述 → LEGACY；**PR 合并状态不自动改变**。
- Classification: **INTERNAL / LEGACY（表述）/ PR 状态不变**
- Affected files: 06_PR21_CANONICAL_COMPATIBILITY.md
- Status: DECIDED（不自动 merge）

## CD-014 — Classic Reconstruction Constitution v1.0

- Conflict: 宪法 v1.0（99c9efa2，P02 人类批准的 LIVE 权威）Article I：产品 = reconstruction-first listening environment，体验 Choose→Reconstruct→Play；P01 人类方向：对外 = Music/Player + PLAY（第一阶段）。
- P00 evidence: E06（宪法 Supersedes 旧身份）、E05（README 引用宪法）
- Human direction: 对外产品面 = Music/Player + PLAY
- Decision: 宪法 v1.0 的「重建优先」作为**内部生产哲学与工程权威保留（INTERNAL 域）**——Reconstruct 是云端生产系统内部环节（Intake→…→Render→Delivery）；其 Article I 的对外产品表述（reconstruction-first listening environment 作为公开身份）被 P01 人类方向覆盖，对外身份以 P01 Canon 为准。**宪法文件文本是否更新 → HUMAN_DECISION_REQUIRED**（宪法为 P02 人类批准产物，本包不改动其正文）。
- Classification: **CANONICAL（内部生产域）/ HUMAN_DECISION_REQUIRED（文本更新）**
- Affected files: 无（不修改宪法正文）；docs/canon/CURRENT_CANON.md 中记录
- Status: PARTIAL — HUMAN_DECISION_REQUIRED

## CD-015 — 状态机 / orchestration / API duplicate authority

- Conflict: orchestration/（LEGACY 声明）、node/（24x7 实跑）、data_factory/（pilot 验证）、reconstruction_factory/（新）多套并存（C5）。
- P00 evidence: E13/E14（node 双节点实跑）、TT-007~013
- Decision:
  - orchestration/workflow_engine → **LEGACY**（维持既有声明）
  - node（moodify-node worker）→ **CANONICAL**（云端队列实跑，SQLite）
  - data_factory → **CANONICAL**（数据工厂 pilot 验证，10/10）
  - reconstruction_factory → **EXPERIMENTAL**（新，未生产）
  - 单一 authoritative state machine 的最终统一 → **HUMAN_DECISION_REQUIRED**（P04/控制面包范围）
- Classification: 混合（如上）
- Status: PARTIAL — HUMAN_DECISION_REQUIRED（统一方案）

## CD-016 — 外部能力（LALAL/Audiolla/FFmpeg/Demucs/Basic Pitch）

- Conflict: 无权威冲突；能力状态已在 P00 TT-056~059 记录。
- Decision: 保持 P00 分类（CONNECTED_UNTESTED / DEPLOYED_NOT_VERIFIED / PLANNED_ONLY 等）；Canon 中不夸大（R10）。
- Classification: 维持 P00 状态
- Status: DECIDED（引用 P00）

---

## Allowed Classifications 使用统计

| 分类 | 使用 |
|---|---|
| CANONICAL | CD-001/003/004/005/008/010/011(部分)/014(内部域)/015(部分) |
| INTERNAL | CD-002/006/007/010/012/013/014 |
| EXPERIMENTAL | CD-015(reconstruction_factory) |
| LEGACY | CD-013(旧表述)/CD-015(orchestration) |
| MIGRATION_PENDING | CD-009(本包完成)/CD-012 |
| HUMAN_DECISION_REQUIRED | CD-011(命名)/CD-014(宪法文本)/CD-015(状态机统一) |
| REMOVE_LATER | 无（本包不删除） |
