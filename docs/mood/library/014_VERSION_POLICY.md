# MOOD LIBRARY 014 — Version Policy

**Version:** 1.0（MOOD LIBRARY 014, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_DOCUMENT_INVENTORY.md](014_DOCUMENT_INVENTORY.md) · [014_METADATA_SCHEMA.md](014_METADATA_SCHEMA.md)

---

## 1. 语义版本规则

| Version 范围 | 语义 | Promotion 条件 |
|---|---|---|
| `0.x` | Draft / experimental / pre-constitutional | Agent 可自由登记 |
| `1.0` | 正式冻结版本 | **仅人类授权**（MD-HDR 类决议） |
| `1.x` | 兼容性修订 / 澄清 / 非结构性扩展 | Agent 可登记，需 commit review |
| `2.0` | 重大协议或治理结构变化 | **仅人类授权** |

## 2. Canonical 唯一性

同一 `slug`（doc family）下：

- 同时只能存在一个 `status = active`
- 历史版本进入 `superseded`（默认保留可达 URL）
- `archived` 用于完全退役的版本（仍可读但不出现在 Foundation / Protocol 等默认分类）

## 3. Codex 不得自动 promote

禁止因为：

- 文档完整
- build 通过
- PDF 生成成功
- 测试 PASS

就把 `version` 从 `0.x` 提升到 `1.0`。

Promotion 必须由：

- 人类权威签发决议
- 进入 `docs/mood/DECISION_LOG.md`
- 更新 `docs/canon/CANON_CHANGELOG.md`

## 4. 现状

| Slug | Version | Status | Promotion 由 |
|---|---|---|---|
| mood-canon | 1.0 | active | 011 implementation（待人类 G0 签发） |
| mood-architecture | 1.0 | active | 同上 |
| mood-product-relationship | 1.0 | active | 同上 |
| mood-launch-gate | 1.0 | active | 同上 |
| mood-asset-classification | 1.0 | active | 同上 |
| mood-roadmap | 1.0 | active | 同上 |
| mood-decision-log | 1.0 | active | 同上 |
| mood-inflight-changes | 1.0 | active | 同上 |
| public-brand-constitution | 1.0 | active | Public Form v1.1（已签发） |
| public-form-canon | 1.1 | active | Public Form v1.1（已签发） |
| canonical-minimum-contracts | 0.1 | draft | 等 012 复审 + G2 PASS |
| data-protocol-v1 | 0.1 | draft | 同上 |
| product-boundary-contract | 0.1 | draft | 同上 |
| quarterly-freeze-1-0 | 0.1 | draft | 同上 |
| mip-000 | 0.1 | draft | 020 启动后改 1.0 |
| mood-tokenomics | 0.0 | draft | 等 G10 |
| mood-treasury-policy | 0.0 | draft | 等 G7 |
| mood-holder-rewards-policy | 0.0 | draft | 等 G7 |
| mood-legacy-token-policy | 0.0 | draft | 等 G10 |
| mood-launch-policy | 0.0 | draft | 等 G10 / G11 |
| mood-threat-model | 0.0 | draft | 等 G8 |
| mood-security-review | 0.0 | draft | 等 G8 |
| mood-privacy-review | 0.0 | draft | 等 G8 |
| mood-incident-response | 0.0 | draft | 等 G8 |
| mood-audit-reports | 0.0 | draft | 等 G8 + 真实审计 |
| mood-machine-listening | 0.0 | draft | 等 018 / 016 |
| mood-audio-intelligence | 0.0 | draft | 等 018 / 016 |
| mood-proof-of-contribution | 0.0 | draft | 等 016 |
| mood-human-ai-collab | 0.0 | draft | 等 018 |

## 5. 与 011 G0 的关系

011 完成时把 docs/mood/* 视为 `implementation PASS-ready`，但 014 必须：

- 不擅自把 version 升到 1.0
- 在 metadata 中保持 `version = 1.0`（011 写定）
- 把 `Promotion by` 字段填 `011 implementation (pending human sign-off)`
- 等待 `docs/canon/CANON_CHANGELOG.md` 正式签发后再视为正式 PASS

014 不擅自把 `0.x` 升到 `1.0`。