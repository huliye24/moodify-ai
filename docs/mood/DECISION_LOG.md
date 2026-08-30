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

## 6. 011 期间冲突 / 越权记录

011 期间如发生：

- 多分支修改同一 Canon 文件
- 未知新 Token 地址
- production deployment 正在进行
- 真实资金操作
- 覆盖并行工作

立即停止相关动作并在本节追加一条 `MD-CONFLICT-NNN` 记录。

011 期间 **未发生** 上述事件，本节留空。
