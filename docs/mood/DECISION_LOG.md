# DECISION_LOG — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md) · [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md)

---

## 1. 用途

本文件记录 **MOOD Canon 范围内**的所有人类决议、HUMAN_DECISION_REQUIRED 项、Gate 状态变更、Canon 变更与并行分支处置动作。

每个 decision entry 必须包含：

- `ID`：稳定 ID（如 `MD-011-001`）
- `Date`：决议时间（ISO 8601）
- `Topic`：主题
- `Decision`：决议内容
- `Reviewer`：决定人 / 角色
- `Evidence`：证据（commit / doc / test / runtime）
- `Status`：`PASS` / `BLOCKED` / `PENDING` / `SUPERSEDED`
- `Notes`：附注

## 2. Canon 决议

### MD-011-001 — MOOD 总体身份

- **Date：** 2026-08-30
- **Topic：** MOOD 总体身份
- **Decision：** `MOOD = WORLD + PROTOCOL + PORTAL`。Token 不是产品、不是协议、不是世界。
- **Reviewer：** 011 implementation（基于 011 输入） + 人类权威（待签发）
- **Evidence：** `docs/mood/CURRENT_CANON.md`、`docs/mood/SYSTEM_ARCHITECTURE.md`、`docs/mood/PRODUCT_RELATIONSHIP.md`
- **Status：** `PASS`（待人类签发）
- **Notes：** 011 期间以 implementation PASS 形式记录；正式 PASS 由人类权威在 `docs/canon/CANON_CHANGELOG.md` 签发。

### MD-011-002 — crestwavecoin.com 是 WORLD Home

- **Date：** 2026-08-30
- **Topic：** MOOD WORLD 入口域名
- **Decision：** `crestwavecoin.com` 是 MOOD WORLD Home（PLANNED）。011 不授权上线。
- **Reviewer：** 011 implementation + 人类权威
- **Evidence：** `docs/mood/PRODUCT_RELATIONSHIP.md`、`docs/mood/SEPTEMBER_BUILD_ROADMAP.md`（013 G1）
- **Status：** `PASS`（待人类签发）
- **Notes：** 上线触发条件：G0 + G1 + G9 完成 + 公共语言写入 PUBLIC_BRAND_CONSTITUTION。

### MD-011-003 — Moodify Music / Player 是 Genesis Application

- **Date：** 2026-08-30
- **Topic：** Genesis Application 身份
- **Decision：** Moodify Music / Player 是 MOOD 的 Genesis Application（首个面向用户的应用）。它不是 MOOD 总体身份。
- **Reviewer：** 011 implementation + 人类权威
- **Evidence：** `docs/mood/PRODUCT_RELATIONSHIP.md`
- **Status：** `PASS`（待人类签发）

### MD-011-004 — 011 不授权任何新官方 CA

- **Date：** 2026-08-30
- **Topic：** Token CA 授权
- **Decision：** 011 期间不授权任何「未来新官方 CA」。Token CA 由 G0–G11 全部 PASS 后由人类授权。
- **Reviewer：** 011 implementation
- **Evidence：** `docs/mood/CURRENT_CANON.md`、`docs/mood/TOKEN_LAUNCH_GATE.md`、`docs/mood/ASSET_CLASSIFICATION.md`
- **Status：** `PASS`

### MD-011-005 — 旧 Token / 旧合约不能自动继承

- **Date：** 2026-08-30
- **Topic：** 历史 Token / Genesis v1.0 处置
- **Decision：** 历史 Genesis v1.0 实现（`codex/moodify-classic-reconstruction-001`）与任何旧 Token / 旧合约进入 FREEZE 集合，不得自动成为 MOOD Token 的 Canon。
- **Reviewer：** 011 implementation
- **Evidence：** `docs/mood/ASSET_CLASSIFICATION.md`、`docs/mood/IN_FLIGHT_CHANGE_REGISTER.md`
- **Status：** `PASS`

### MD-011-006 — 009 不允许整条 merge

- **Date：** 2026-08-30
- **Topic：** `codex/mood-mainnet-integration-009` 处置
- **Decision：** `codex/mood-mainnet-integration-009` 不得整条 merge。允许选择性 cherry-pick（Wallet / viem）；禁止带入 009 的未来官方 CA / Cloudflare Worker 主网部署假设。
- **Reviewer：** 011 implementation
- **Evidence：** `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md`
- **Status：** `PASS`

## 3. Gate 状态

### G0 — Canon

- **Date：** 2026-08-30
- **Status：** `IN_PROGRESS`
- **Owner：** 011 implementation
- **Reviewer：** 人类权威
- **Evidence（提交中）：** `docs/mood/CURRENT_CANON.md` + `SYSTEM_ARCHITECTURE.md` + `PRODUCT_RELATIONSHIP.md` + `ASSET_CLASSIFICATION.md` + `IN_FLIGHT_CHANGE_REGISTER.md` + `TOKEN_LAUNCH_GATE.md` + `SEPTEMBER_BUILD_ROADMAP.md` + `DECISION_LOG.md` + 扩展 Canon guard + CANON_CHANGELOG 条目
- **Notes：** 011 完成时尝试转为 `PASS`；正式 PASS 需人类签发。

### G1 — G11

- **Status：** `NOT_STARTED`
- **Notes：** 由 012–025 各自推进。

## 4. HUMAN_DECISION_REQUIRED（待人类决议）

以下项目 011 不判定，标记为人类决议待办：

### MD-HDR-001 — Canonical 文本最终签发

- **Topic：** `docs/mood/CURRENT_CANON.md` + `PRODUCT_RELATIONSHIP.md` + `TOKEN_LAUNCH_GATE.md` 等文本是否作为正式 Canon 签发
- **Why：** 011 期间由 Agent 起草；正式 PASS 需要人类权威签发。
- **Inputs：** 当前 011 提交的所有 `docs/mood/*.md`。
- **Decision required by：** G0 PASS 之前。

### MD-HDR-002 — 024 Smart Contract 审计单位

- **Topic：** 024 阶段 Smart Contract 审计单位
- **Why：** 由人类决定。
- **Decision required by：** G10 之前。

### MD-HDR-003 — 025 Legal Review 范围

- **Topic：** 025 阶段 Legal Review 范围
- **Why：** 由人类决定。
- **Decision required by：** G11 之前。

### MD-HDR-004 — crestwavecoin.com 上线触发

- **Topic：** `crestwavecoin.com` 何时上线、上线语言、上线后是否启用 Buy / Trade CTA
- **Why：** 由人类决定。
- **Decision required by：** G1 + G9 完成后。

### MD-HDR-005 — 历史 Genesis v1.0 资产最终归档

- **Topic：** `codex/moodify-classic-reconstruction-001` 与相关 apps/web/contracts / docs/protocol / docs/releases 文档的最终归档 / 保留 / 公开策略
- **Why：** 011 标记 FREEZE；最终归档策略需人类批准。
- **Decision required by：** G10 之前。

## 5. Canon 变更历史（与 docs/canon/CANON_CHANGELOG.md 同步）

| Date | Change | Reason |
|---|---|---|
| 2026-08-30 | 新增 `docs/mood/CURRENT_CANON.md`：`MOOD = WORLD + PROTOCOL + PORTAL` | MOOD FOUNDATION 011 |
| 2026-08-30 | 新增 `docs/mood/SYSTEM_ARCHITECTURE.md` 等 7 个文档 | MOOD FOUNDATION 011 |
| 2026-08-30 | 扩展 Canon guard 检测 MOOD ≠ Token 反模式 | MOOD FOUNDATION 011 |
| 2026-08-30 | 最小更新 AGENTS.md / README.md 指向 MOOD Canon | MOOD FOUNDATION 011 |
| 2026-08-30 | 标记 `codex/mood-mainnet-integration-009` DO NOT MERGE WHOLE | MOOD FOUNDATION 011 |
| 2026-08-30 | 标记 `codex/moodify-classic-reconstruction-001` Genesis v1.0 进入 FREEZE | MOOD FOUNDATION 011 |
| 2026-08-30 | 新增 `apps/web/lib/mood-launch-state.ts` 单点 runtime launch gate；默认 `foundation` | MOOD FOUNDATION 012 |
| 2026-08-30 | 新增 `docs/mood/extraction/{012_SOURCE_AUDIT, 012_EXTRACTION_MANIFEST, 012_DEPENDENCY_MAP, 012_LEGACY_TOKEN_SEAMS, 012_FINAL_REPORT}.md` | MOOD FOUNDATION 012 |

### MD-012-001 — 012 不修改 Canon

- **Date：** 2026-08-30
- **Topic：** 012 是否修改 Canon
- **Decision：** 012 **不修改** Canon。012 引入 runtime launch gate（`apps/web/lib/mood-launch-state.ts`）作为 Canon 的执行工具，不改变对外身份、内部/外部边界、state machine authority、evidence authority、cloud control authority、data authority。
- **Reviewer：** 012 implementation + 人类权威（待 012 接受后签发）
- **Evidence：** `docs/mood/extraction/012_FINAL_REPORT.md` §8 invariants; `docs/canon/CANON_CHANGELOG.md` 未追加 CANON_CHANGE = YES 条目。
- **Status：** `PENDING`（012 未签发前）

### MD-012-002 — 012 默认 launch state = `foundation`

- **Date：** 2026-08-30
- **Topic：** Launch gate 默认值
- **Decision：** `MOOD_LAUNCH_STATE = "foundation"`。foundation 状态下：no Token CA exposure, no Buy/Trade/Claim/Airdrop CTA, no live wallet token balance, no live treasury token balance, no pending reward settlement to token。
- **Reviewer：** 012 implementation + 人类权威
- **Evidence：** `apps/web/lib/mood-launch-state.ts`、`apps/web/tests/mood-launch-state.test.mjs`（INV-012-01 / INV-012-06 PASS）。
- **Status：** `PENDING`

### MD-012-003 — `codex/mood-mainnet-integration-009` 整条不 merge

- **Date：** 2026-08-30
- **Topic：** 009 处理策略
- **Decision：** 012 不 merge `codex/mood-mainnet-integration-009` 整条；不做整条 cherry-pick。009 的 token-coupled 资产（`mood-token.ts` / `mood-chain.ts` / `mood-treasury.ts` / `/token` / `/genesis` / `/airdrop` / `MoodGenesisDistributor.sol`）保持 FREEZE。Foundation-grade 资产（`evm-address.ts`、`contribution-*`、`reputation_events`、admin auth、transparency read API）由 015 / 016 / 021 在各自迁移包中处理。
- **Reviewer：** 012 implementation + 人类权威
- **Evidence：** `docs/mood/extraction/012_EXTRACTION_MANIFEST.md`、`012_LEGACY_TOKEN_SEAMS.md`。
- **Status：** `PENDING`

### MD-012-HDR-001 — `pending_mood` 字段是否重命名

- **Topic：** Drizzle `reward_events.amountMood` / `amountAtomic` 字段是否在 016 阶段重命名为 `pending_reward_units`
- **Why：** 012 当前不动 schema。语义已在 012 文档中明确为「accounting only, no settlement」；schema 名称仍误导。
- **Inputs：** `docs/mood/extraction/012_EXTRACTION_MANIFEST.md` §4.1。
- **Decision required by：** 016 启动前（不阻塞 012 接受）。

### MD-012-HDR-002 — `genesis_participants` 身份 / 空投字段拆分

- **Topic：** `genesis_participants` 表是否在 015 阶段拆为身份表 + 空投表（或视图）
- **Why：** 同一表同时承载 foundation-grade 字段（`walletAddressNormalized`、`signatureVersion`）与空投字段（`allocationMood`、`contributionScore`）。012 不动 schema。
- **Inputs：** `docs/mood/extraction/012_EXTRACTION_MANIFEST.md` §4.2。
- **Decision required by：** 015 启动前（不阻塞 012 接受）。

## 6. 011 期间冲突 / 越权记录

011 期间如发生：

- 多分支修改同一 Canon 文件
- 未知新 Token 地址
- production deployment 正在进行
- 真实资金操作
- 覆盖并行工作

立即停止相关动作并在本节追加一条 `MD-CONFLICT-NNN` 记录。

011 期间 **未发生** 上述事件，本节留空。
