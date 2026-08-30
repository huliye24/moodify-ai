# MOOD LIBRARY 014 — Document Inventory

**Package:** `MOOD-LIBRARY-014`
**Date:** 2026-08-30
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_METADATA_SCHEMA.md](014_METADATA_SCHEMA.md) · [014_VERSION_POLICY.md](014_VERSION_POLICY.md) · [014_PUBLICATION_POLICY.md](014_PUBLICATION_POLICY.md) · [014_HASH_POLICY.md](014_HASH_POLICY.md) · [014_MISSING_DOCUMENTS.md](014_MISSING_DOCUMENTS.md) · [014_FINAL_REPORT.md](014_FINAL_REPORT.md)

---

## 1. Scope

本清单只统计 **014 实际可注册的、来自 origin/main（经 011 / 013 桥接）** 的文档。`codex/mpf-002-contribution-core` 等并行分支上的文档（apps/web/docs/protocol/*、protocol/*、docs/protocol/* 等）经 012 cherry-pick 审查后才进入 Library，本 014 bridge 不预注册。

## 2. 总数

```text
Total candidates scanned:  ~150+ markdown files in /docs/
Real register-able now:    9 documents (existing in origin/main branch)
Missing / planned:        23 documents (slotted but content pending)
Draft skeletons to add:   5 documents (Constitution + Economics slots)
```

## 3. Category Counts

| Category | Existing | Skeleton | Missing | Total slots |
|---|---|---|---|---|
| foundation | 3 | 0 | 0 | 3 |
| protocol | 4 | 0 | 6 | 10 |
| governance | 1 | 1 | 2 | 4 |
| economics | 0 | 5 | 0 | 5 |
| security | 0 | 5 | 0 | 5 |
| research | 1 | 3 | 0 | 4 |

## 4. Real Documents to Register

### Foundation

| Slug | Title | Source Path | Status | Version | Language | Hash strategy |
|---|---|---|---|---|---|---|
| `mood-canon` | MOOD Canon — WORLD + PROTOCOL + PORTAL | `docs/mood/CURRENT_CANON.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-architecture` | MOOD System Architecture | `docs/mood/SYSTEM_ARCHITECTURE.md` | active | 1.0 | en (zh summary in CURRENT_CANON) | SHA-256 computed |
| `mood-product-relationship` | MOOD Product Relationship | `docs/mood/PRODUCT_RELATIONSHIP.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-launch-gate` | MOOD Token Launch Gate | `docs/mood/TOKEN_LAUNCH_GATE.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-asset-classification` | MOOD Asset Classification | `docs/mood/ASSET_CLASSIFICATION.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-roadmap` | MOOD September Build Roadmap | `docs/mood/SEPTEMBER_BUILD_ROADMAP.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-decision-log` | MOOD Decision Log | `docs/mood/DECISION_LOG.md` | active | 1.0 | bilingual | SHA-256 computed |
| `mood-inflight-changes` | MOOD In-Flight Change Register | `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md` | active | 1.0 | bilingual | SHA-256 computed |
| `public-brand-constitution` | MOOD Public Brand Constitution | `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | active | 1.0 | en (zh via products branch) | SHA-256 computed |
| `public-form-canon` | Moodify Music/Player Public Form Canon | `docs/canon/CURRENT_CANON.md` | active | 1.1 | en | SHA-256 computed |

注：docs/mood/* 八个文档是从 011 / 013 注册而来的，是 MOOD Library 的真实 **MOOD-level** 文档。

### Protocol

| Slug | Title | Source Path | Status | Version | Notes |
|---|---|---|---|---|---|
| `canonical-minimum-contracts` | Canonical Minimum Contracts v1 | `docs/contracts/CANONICAL_MINIMUM_CONTRACTS_V1.md` | draft | 0.1 | 014 不修改内容；登记为 draft 等 012 复审 |
| `data-protocol-v1` | Data Protocol v1 | `docs/contracts/DATA_PROTOCOL_V1.md` | draft | 0.1 | 同上 |
| `product-boundary-contract` | Product Boundary Contract | `docs/contracts/product-boundary.md` | draft | 0.1 | 同上 |
| `quarterly-freeze-1-0` | Quarterly Freeze 1.0 001 | `docs/contracts/QUARTERLY_FREEZE_1_0_001.md` | draft | 0.1 | 同上 |

注：apps/web/docs/protocol/* 与 protocol/* 的 PROTOCOL 文档来自 `codex/mpf-002-contribution-core`（KEEP 集合），需 012 cherry-pick 后才能注册。014 在 014_MISSING_DOCUMENTS.md 标记。

### Governance

| Slug | Title | Source Path | Status | Version | Notes |
|---|---|---|---|---|---|
| `mood-decision-log` | (重复登记在 foundation) | — | — | — | 见 foundation |
| `mip-000` | MIP-000 — MOOD Improvement Proposal Process | `docs/mood/governance/MIP-000.md` | draft | 0.1 | 014 新建 Draft skeleton（只定义流程，不启动链上投票） |

### Economics (Draft slots, no real content)

| Slug | Title | Status | Version | Notes |
|---|---|---|---|---|
| `mood-tokenomics` | MOOD Tokenomics | draft | 0.0 | Parameters UNFROZEN — 等 G10 |
| `mood-treasury-policy` | MOOD Treasury Policy | draft | 0.0 | 等 G7 |
| `mood-holder-rewards-policy` | MOOD Holder Rewards Policy | draft | 0.0 | 等 G7 |
| `mood-legacy-token-policy` | MOOD Legacy Token Policy | draft | 0.0 | 历史 Genesis v1.0 进入 FREEZE |
| `mood-launch-policy` | MOOD Launch Policy | draft | 0.0 | 等 G10 / G11 |

### Security (Draft slots, no real content)

| Slug | Title | Status | Version | Notes |
|---|---|---|---|---|
| `mood-threat-model` | MOOD Threat Model | draft | 0.0 | 022 阶段复用 apps/web/docs/security/* |
| `mood-security-review` | MOOD Security Review | draft | 0.0 | 同上 |
| `mood-privacy-review` | MOOD Privacy Review | draft | 0.0 | 同上 |
| `mood-incident-response` | MOOD Incident Response | draft | 0.0 | 同上 |
| `mood-audit-reports` | MOOD Audit Reports | draft | 0.0 | 没有真实审计，UNFROZEN |

### Research (Draft slots, no real content)

| Slug | Title | Status | Version | Notes |
|---|---|---|---|---|
| `mood-machine-listening` | Machine Listening (MOOD) | draft | 0.0 | Research only; 不承诺结论 |
| `mood-audio-intelligence` | Audio Intelligence (MOOD) | draft | 0.0 | 同上 |
| `mood-proof-of-contribution` | Proof of Contribution (MOOD) | draft | 0.0 | 等 016 |
| `mood-human-ai-collab` | Human + AI Collaboration (MOOD) | draft | 0.0 | 018 / 016 / 017 整理后填充 |

## 5. Cross-source documents NOT registered in 014

### Historical / Archived (FREEZE 集合)

| Title | Source | Reason |
|---|---|---|
| MOOD Protocol Genesis v1.0 | `codex/moodify-classic-reconstruction-001` (branch only) | FREEZE per ASSET_CLASSIFICATION.md §4 |
| CrestWave Public Staging 009 | `codex/mood-mainnet-integration-009` (branch only) | DO NOT MERGE WHOLE; cherry-pick only |
| Pre-011 Canon drafts | `docs/canon/CURRENT_CANON.md` (v1.1) | 已升级为 v1.1 active |

### 014 故意不注册的资产

- `docs/mood/FINAL_REPORT_011.md`（包内报告，不属于对外 canonical doc）
- `docs/mood/START_HERE_FOR_011.md`（包内入口）
- `docs/mood/portal/013_FINAL_REPORT.md`（同上）
- 任何 `docs/experiments/*`、`docs/strategy/*`、`docs/ui-sketches/*`、`docs/bug/*`（实验 / 旧素材）
- 任何 `docs/xuanzhen/*`、`docs/math/*`、`docs/engineer/*`、`docs/plan/*`（早期 / 实验 / 中文草稿）
- `docs/release-notes/*`、`docs/public-form/package-*`（运营报告，不是协议文档）

## 6. Legacy / Historical scoping

按照 [014_PUBLICATION_POLICY.md](014_PUBLICATION_POLICY.md) §Status Honesty 与 [011 docs/mood/ASSET_CLASSIFICATION.md](../ASSET_CLASSIFICATION.md) §4 FREEZE：

- `codex/moodify-classic-reconstruction-001` 的 **Genesis v1.0** 实现（Distributor 部署脚本、Airdrop 流程、`apps/web/contracts/protocol/MoodGenesisDistributor.sol`）**不**自动成为 MOOD Token 的 Canon。
- 任何旧 "Genesis Security Review" / "Token Audit" 类历史文档必须标记 `HISTORICAL / SUPERSEDED / LEGACY SCOPE` —— 不得描述为「未来新 Token 审计」。
- `codex/mood-mainnet-integration-009` 的 Cloudflare Worker 部署、BSC 配置、未来官方 CA 假设属于 FREEZE；012 cherry-pick 后才能用于 KEEP。

## 7. What 014 does next

1. 实现 `apps/web/lib/mood/library/` 单点 metadata registry。
2. 实现 `/library` 列表 + `/library/[slug]` 阅读器。
3. 真实计算 SHA-256（仅针对已注册的真实文档）。
4. 创建 Constitution Skeleton（`/library/mood-constitution`）。
5. 创建 Economics / Security / Research slots（带 `Draft` / `UNFROZEN` / `HISTORICAL` 标签）。
6. 跑 INV-014-01..10 测试。