# MOOD LIBRARY 014 — Missing Documents

**Version:** 1.0（MOOD LIBRARY 014, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_DOCUMENT_INVENTORY.md](014_DOCUMENT_INVENTORY.md) · [014_FINAL_REPORT.md](014_FINAL_REPORT.md)

---

## 1. 真实缺失（来自 `codex/mpf-002-contribution-core` 或其他分支，需 012 cherry-pick）

| Slug | Title | 真实位置 | Cherry-pick 由 |
|---|---|---|---|
| `mood-identity-protocol` | MOOD Identity Protocol | `codex/mpf-002-contribution-core` 的 `protocol/reputation/core/identity.js` + `docs/contracts/music/identity_*.md`（如果存在） | 012 |
| `mood-contribution-network` | MOOD Contribution Network | `codex/mpf-002-contribution-core` 的 `protocol/contribution/EXECUTION_REPORT.md` + `protocol/contribution/README.md` | 012 |
| `mood-reputation-model` | MOOD Reputation Model | `codex/mpf-002-contribution-core` 的 `protocol/reputation/EXECUTION_EVIDENCE.md` + `protocol/reputation/README.md` | 012 |
| `mood-ai-agent-protocol` | MOOD AI Agent Protocol | 来自 `web 3.0/2026.8.30/MOOD_AGENTS_018_AI_REGISTRY/`（尚未执行 018） | 018 |
| `mood-node-protocol` | MOOD Node Protocol | `codex/mpf-002-contribution-core` 的 `protocol/node-registry/EXECUTION_EVIDENCE.md` + `protocol/node-registry/README.md` | 012 |
| `mood-transparency-protocol` | MOOD Transparency Protocol | `codex/mpf-002-contribution-core` 的 `apps/web/docs/protocol/TRANSPARENCY.md` | 012 |

## 2. Skeleton-only（014 写占位，等后续 package 填正文）

| Slug | Title | 后续由 |
|---|---|---|
| `mood-constitution` | MOOD Constitution | 014 skeleton → 020 启动后实化 |
| `mood-tokenomics` | MOOD Tokenomics | 024 |
| `mood-treasury-policy` | MOOD Treasury Policy | 021 |
| `mood-holder-rewards-policy` | MOOD Holder Rewards Policy | 021 |
| `mood-legacy-token-policy` | MOOD Legacy Token Policy | 024 |
| `mood-launch-policy` | MOOD Launch Policy | 024 + 025 |
| `mood-threat-model` | MOOD Threat Model | 022 |
| `mood-security-review` | MOOD Security Review | 022 |
| `mood-privacy-review` | MOOD Privacy Review | 022 |
| `mood-incident-response` | MOOD Incident Response | 022 |
| `mood-audit-reports` | MOOD Audit Reports | 024 + 真实审计 |
| `mood-machine-listening` | Machine Listening (MOOD) | 016 / 017 |
| `mood-audio-intelligence` | Audio Intelligence (MOOD) | 016 / 017 |
| `mood-proof-of-contribution` | Proof of Contribution (MOOD) | 016 |
| `mood-human-ai-collab` | Human + AI Collaboration (MOOD) | 016 / 018 |

## 3. 不在 014 Library 范围（明确不登记）

- 任何来自 `apps/web/contracts/protocol/MoodGenesisDistributor.sol` 的链上合约相关文档 → FREEZE 集合，等 G10 / G11 复审
- `docs/experiments/*`、`docs/strategy/*`、`docs/ui-sketches/*`、`docs/bug/*` 等实验 / 旧素材
- `docs/xuanzhen/*`、`docs/math/*`、`docs/engineer/*`、`docs/plan/*`（早期 / 中文草稿）
- `docs/release-notes/*`、`docs/public-form/package-*`（运营 / 收口报告）
- `MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.md`（运营快照）
- 任何 mobile / desktop / electron 内部 docs

## 4. PDF pending（无真实 PDF）

| Slug | 真实 PDF 状态 |
|---|---|
| `mood-canon` | NONE — 014 不强制生成 PDF |
| `mood-architecture` | NONE |
| `mood-product-relationship` | NONE |
| `mood-launch-gate` | NONE |
| `mood-asset-classification` | NONE |
| `mood-roadmap` | NONE |
| `mood-decision-log` | NONE |
| `mood-inflight-changes` | NONE |
| `public-brand-constitution` | NONE |
| `public-form-canon` | NONE |

UI 显示「PDF not available yet」，不显示下载按钮。

## 5. IPFS pending（无真实 CID）

所有 slug：IPFS 字段保持 `undefined`。UI 不显示 IPFS 行。

014 不预 pin、不自动上传、不编造 CID。

## 6. 下一步（等 012 / 015 / 016..022 落地后回填）

| 触发 | 动作 |
|---|---|
| 012 cherry-pick 完成 | 注册 `mood-identity-protocol`、`mood-contribution-network`、`mood-reputation-model`、`mood-node-protocol`、`mood-transparency-protocol` |
| 018 启动 | 注册 `mood-ai-agent-protocol` |
| 020 启动 | `mip-000` v0.1 → v1.0；`mood-constitution` skeleton 替换为正文（人类授权后） |
| 021 启动 | `mood-treasury-policy`、`mood-holder-rewards-policy` 替换为正文 |
| 022 启动 | `mood-threat-model`、`mood-security-review`、`mood-privacy-review`、`mood-incident-response` 替换为正文 |
| 024 启动 | `mood-tokenomics`、`mood-legacy-token-policy`、`mood-launch-policy`、`mood-audit-reports` 替换为正文 |
| 016 / 017 启动 | `mood-machine-listening`、`mood-audio-intelligence`、`mood-proof-of-contribution`、`mood-human-ai-collab` 替换为正文 |