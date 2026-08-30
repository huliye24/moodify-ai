# SEPTEMBER_BUILD_ROADMAP — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) · [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) · [DECISION_LOG.md](DECISION_LOG.md)

---

## 1. 总览

011 → 025 共 15 个 package。每个 package 推进一个或多个 Token Launch Gate（G0–G11）。Token Activation（025）必须等待全部 G0–G11 PASS。

```text
011  Canon Freeze
  ↓ G0
012  Protocol Foundation Extraction
  ↓
013  MOOD Portal Shell
  ↓ G1
014  MOOD Library
  ↓ G2
015  Wallet + MOOD Passport
  ↓ G3
016  Contribution Network v1
  ↓ G4
017  Network Observatory
  ↓ G5
018  AI Agents Registry
019  Nodes Registry
  ↓
020  MIP Governance
  ↓ G6
021  Treasury & Transparency
  ↓ G7
022  Security & Trust Layer
  ↓ G8
023  Public Staging & E2E
  ↓ G9
024  Genesis Readiness Review
  ↓ G10
025  MOOD Token Activation
  ↓ G11
  BLOCKED until G0..G11 ALL PASS
```

## 2. Package 详细

### 011 — Canonical Freeze & Branch Convergence

- **Gate 推进：** G0
- **核心输出：**
  - `docs/mood/CURRENT_CANON.md`（MOOD = WORLD + PROTOCOL + PORTAL）
  - `docs/mood/SYSTEM_ARCHITECTURE.md`（边界）
  - `docs/mood/PRODUCT_RELATIONSHIP.md`（MOOD ↔ Moodify）
  - `docs/mood/ASSET_CLASSIFICATION.md`（KEEP / KEEP BUT DARK / FREEZE / SEPARATE）
  - `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md`（并行分支登记）
  - `docs/mood/TOKEN_LAUNCH_GATE.md`（G0–G11）
  - `docs/mood/SEPTEMBER_BUILD_ROADMAP.md`（本文件）
  - `docs/mood/DECISION_LOG.md`（决策）
  - `docs/mood/START_HERE_FOR_011.md`（入口）
  - 扩展 Canon guard（`scripts/canon_guard.py`）
  - 最小更新 AGENTS.md / README.md（指向 MOOD Canon）
  - `docs/canon/CANON_CHANGELOG.md` 增加 011 条目
- **不做：** 任何 FREEZE 集合内的动作；任何 012–025 准备工作
- **状态：** 进行中（2026-08-30）

### 012 — Protocol Foundation Extraction

- **Gate 推进：** 准备 G0–G3 复用底座（不直接 PASS Gate）
- **核心输出：**
  - Wallet / Signature / Identity primitives 提取
  - Contribution workflow 提取
  - Reputation model 提取
  - Transparency concepts 提取
  - Security / Threat model 引用建立
- **不做：** UI；PROTOCOL 公共 API 暴露
- **依赖：** 011 G0 PASS

### 013 — MOOD Portal Shell

- **Gate 推进：** G1（Public Foundation）
- **核心输出：**
  - WORLD Home 信息架构（crestwavecoin.com PLANNED）
  - PORTAL 与 PRODUCT 入口分层
  - Library / Passport / Governance / Treasury / Observatory 入口容器
- **不做：** Token 入口
- **依赖：** 012 完成

### 014 — MOOD Library

- **Gate 推进：** G2（Library）
- **核心输出：**
  - Whitepaper / Docs / Version / Hash
  - Research archive 引用
  - History / Archive 标签系统
- **不做：** Token 内容
- **依赖：** 013 完成

### 015 — Wallet + MOOD Passport

- **Gate 推进：** G3（Identity）
- **核心输出：**
  - Wallet Connect 复用底座
  - MOOD Passport（Resident Identity）onboarding
  - Public identity ↔ Passport 映射
- **不做：** on-chain identity；SBT / NFT
- **依赖：** 013 / 014 完成

### 016 — Contribution Network v1

- **Gate 推进：** G4（Contribution）
- **核心输出：**
  - Task → Submission → Review → Reputation 完整链路
  - Contribution 评分策略 v1
  - Reputation snapshot 自动生成
- **不做：** Token 奖励
- **依赖：** 015 完成

### 017 — Network Observatory

- **Gate 推进：** G5（Network 之一）
- **核心输出：**
  - 真实 Network status / metrics 视图
  - Contribution / Reputation / Node 全景
- **依赖：** 016 完成

### 018 — AI Agents Registry

- **Gate 推进：** G5 准备
- **核心输出：**
  - Agent identity / capability / proof / status
- **依赖：** 015 / 016 完成

### 019 — Nodes Registry

- **Gate 推进：** G5（Network）
- **核心输出：**
  - Compute / AI / Storage / Verification Nodes 目录
  - Node lifecycle / health / heartbeat
- **依赖：** 015 / 016 完成

### 020 — MIP Governance

- **Gate 推进：** G6（Governance）
- **核心输出：**
  - MIP 提交 / 评审 / 通过 / 落地流程
  - 公共讨论 / 投票 UX（off-chain 默认）
- **不做：** Token 投票权
- **依赖：** 014 / 015 完成

### 021 — Treasury & Transparency

- **Gate 推进：** G7（Transparency）
- **核心输出：**
  - Policy / provenance / transparency 公共面板
  - 历史 Genesis v1.0 docs 标记
- **不做：** 真实资金配置；自动 reward → Token
- **依赖：** 016 / 020 完成

### 022 — Security & Trust Layer

- **Gate 推进：** G8（Security）
- **核心输出：**
  - Threat model 更新
  - Auth / Wallet / API security baseline
  - Incident response runbook
- **不做：** Smart contract 正式审计（属于 024）
- **依赖：** 015–021 完成

### 023 — Public Staging & E2E

- **Gate 推进：** G9（Public Staging）
- **核心输出：**
  - 公网端到端 E2E
  - WORLD Home / Product Home 站点可达
  - PROTOCOL API 公共读
- **不做：** Token Buy / Trade CTA
- **依赖：** 022 完成

### 024 — Genesis Readiness Review

- **Gate 推进：** G10（Tokenomics Freeze）
- **核心输出：**
  - Tokenomics 方案（人类批准）
  - Flap 首期参数（人类批准）
  - Legacy 处置方案（人类批准）
  - Risk 评估报告
  - Audit 计划
- **不做：** Token 部署
- **依赖：** 023 完成 + 022 复审

### 025 — MOOD Token Activation

- **Gate 推进：** G11（Launch Audit）
- **核心输出：**
  - Smart contract 部署
  - LP 配置（如有）
  - 公共 launch
- **BLOCKED：** G0–G11 任一未 PASS 不得开始
- **依赖：** 024 完成 + G11 PASS

## 3. 时间预期

011 在 2026-08-30 启动；012–025 的具体时间窗由 011 之后的人类与 Agent 协作决定，不在 011 内承诺。

时间预期原则：

- 不抢跑：011 完成后才有 012。
- 不偷跑：012 完成后才有 013。
- 不跳过：每个 G 必须显式 PASS。
- 不延期：每个 G 必须有 owner + reviewer + 时间。

## 4. 与 PUBLIC FORM / EXISTING Canon 的衔接

- `docs/brand/public/` 公共品牌语言继续由 `PUBLIC_BRAND_CONSTITUTION.md` 规定；013 + 014 在该宪法下增加 WORLD Home 章节。
- `docs/canon/CURRENT_CANON.md`（v1.1 Public Form Package 01）继续处理 Moodify Music / Player 对外面；011 不覆盖。
- 011–025 进展通过 `docs/canon/CANON_CHANGELOG.md` 与 `docs/mood/DECISION_LOG.md` 持续可见。

## 5. 011 的责任边界

011 只冻结 Canon + 推进 G0。011 不承诺任何 012–025 的实现时间或方案。

011 期间任何越界尝试必须立即停止并记录到 [DECISION_LOG.md](DECISION_LOG.md)。
