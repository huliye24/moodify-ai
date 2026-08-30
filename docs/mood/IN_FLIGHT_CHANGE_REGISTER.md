# IN_FLIGHT_CHANGE_REGISTER — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) · [GIT_SAFETY.md](../../审查包/MOOD_FOUNDATION_011/GIT_SAFETY.md)

---

## 1. 用途

本文件记录 **仓库当前已知的并行分支**（含本地 worktree / 远端 origin / 远端 moodify），其内容、风险、011 期间的处置动作。011 不整条 merge 任何分支；所有合并 / cherry-pick 必须经过本表登记。

## 2. Action 枚举

每个分支的 Action 必属以下之一：

| Action | 含义 |
|---|---|
| **SAFE TO CHERRY-PICK** | 提交可单独 cherry-pick 到 011 之后的分支（012 / 013 / 014 等） |
| **NEEDS REVIEW** | 需人类逐提交审查；011 期间不动作 |
| **DO NOT MERGE WHOLE** | 禁止整条 merge（可能覆盖 Canon / FREEZE 资产 / 未知工作） |
| **SUPERSEDED** | 已被其他分支 / Canon 覆盖，仅保留历史 |
| **UNKNOWN / HUMAN DECISION REQUIRED** | 011 不判定；记录后等待人类 |

## 3. 分支表（snapshot 2026-08-30）

> SHA 为 `git rev-parse` 在 `E:/moodify` 主仓库的输出。Action 由 011 根据 [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) 与 [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md) 判定。

### 3.1 必须明确处理的分支

| Branch | SHA（short） | 用途 | 风险 | Action |
|---|---|---|---|---|
| `origin/codex/mood-mainnet-integration-009` | `ed6aae9b` | Package 009：viem BSC integration + wallet（009 Gates A–C） | 含 Cloudflare Worker 部署、BSC 配置、未来官方 CA 假设；与 011 FREEZE 资产重合 | **DO NOT MERGE WHOLE**。允许选择性 cherry-pick（Wallet Connect / viem 抽象）到 015；禁止带入 009 的「future official CA」 |
| `origin/codex/moodify-classic-reconstruction-001` | `b3f0d71c` | MOOD Protocol Genesis v1.0 — Complete 8-Package Implementation | 含旧 Genesis Distributor、Token 部署脚本、Airdrop / Claim 流程 | **SUPERSEDED**。Genesis v1.0 实现全部进入 `ASSET_CLASSIFICATION.md` 的 FREEZE；不得自动继承为 MOOD Token |
| `origin/codex/mpf-002-contribution-core` | `4e2c1e28` | 本地领先 origin 5 commits；包含 PROTOCOL/MPF-001..005 + `apps/web/lib/*` + `apps/web/docs/protocol/*` + `apps/web/contracts/*` + web 3 surface pages | 含 `/airdrop`、`/genesis`、`/token`、`/contribute`、`/transparency` 页面与 API；与 011 KEEP BUT DARK / FREEZE 资产重合 | **NEEDS REVIEW**。KEEP + KEEP BUT DARK 内容可单独 cherry-pick；FREEZE 内容必须先复审 |
| `codex/mood-protocol-foundation-001`（已合并入 main） | `e24b29f5` | 已合并；成为 origin/main 的一部分 | 已纳入 origin/main | **SUPERSEDED**（已被合并） |

### 3.2 历史 / 旧分支（SUPERSEDED）

| Branch | SHA（short） | Action | 说明 |
|---|---|---|---|
| `origin/codex/mfy-mig-001-canonical-contracts` | `af0e1d41` | **SUPERSEDED** | 已部分合并入 e24b29f5；剩余 work 属于 SEPARATE |
| `origin/codex/mfy-data-factory-001` | `e66cbf9d` | **SUPERSEDED** | 数据工厂属于 Moodify Music 内部系统（SEPARATE） |
| `origin/codex/mfy-data-foundation-001-rev2` | `c807e98c` | **SUPERSEDED** | 属于 SEPARATE |
| `origin/codex/auditory-intelligence-unification` | `6446f75c` | **SUPERSEDED** | Auditory Intelligence 内部系统（SEPARATE） |
| `origin/codex/cloud-mainline-dev-20260603-recovered` | `cfecdfec` | **SUPERSEDED** | 旧 cloud dev 分支（SEPARATE） |
| `origin/codex/mainline-cloud-dev-20260603` | `79754390` | **SUPERSEDED** | 旧 cloud dev 分支（SEPARATE） |
| `origin/codex/moodify-1.0-release-convergence` | `19d8a772` | **SUPERSEDED** | Moodify Music 1.0 收口（SEPARATE） |
| `origin/codex/moodify-ai-ear-reconstitution-001` | `8bc30a76` | **SUPERSEDED** | Ear 重建（SEPARATE） |
| `origin/codex/moodify-logo-assets-20260826` | `07f6b272` | **NEEDS REVIEW** | 仅 logo 资产，需审查是否影响 Public Brand |
| `origin/codex/moodify-music-commercial-v1-001` | `5ef38d90` | **SUPERSEDED** | Moodify Music 商业版（SEPARATE） |
| `origin/codex/pr15-asset-extraction-001` | `fc995d29` | **SUPERSEDED** | PR-15 资产提取（已部分合并） |
| `origin/feat/brand-integration` | `1debccb7` | **SUPERSEDED** | 旧 feat 分支（SEPARATE） |
| `origin/huliye24-patch-1` | `d95ec386` | **SUPERSEDED** | 旧 patch（SEPARATE） |
| `origin/mhp-025-api-v01-alignment` | `565220a3` | **SUPERSEDED** | 旧 MHP 分支（SEPARATE） |
| `origin/milestone/moodify-daily-run-mrs-open-v031` | `58601467` | **SUPERSEDED** | 旧 milestone（SEPARATE） |
| `origin/stabilization-sprint-001` | `c64508fa` | **SUPERSEDED** | 旧 stabilization（SEPARATE） |
| `backup/mainline-cloud-dev-pre-github-cleanup` | `7ab16f2c` | **SUPERSEDED** | 旧备份（SEPARATE） |

### 3.3 本地 worktree 状态

仓库存在以下本地 worktree（截至 2026-08-30）：

| Worktree path | Branch | 说明 |
|---|---|---|
| `E:/moodify` | `codex/mpf-002-contribution-core`（领先 origin 5） | 主工作树 |
| `E:/moodify-github-cleanup` | `codex/github-cleanup` | cleanup 工作 |
| `E:/moodify-mfy-mig-001` | `codex/mfy-mig-001-canonical-contracts` | 旧 MIG 工作 |
| `E:/moodify-pr15-extraction-001` | `codex/pr15-asset-extraction-001` | 旧 PR-15 工作 |
| `E:/moodify-readme-license` | `codex/readme-license` | README / License |
| `E:/moodify-reconstitution-001` | `codex/moodify-ai-ear-reconstitution-001` | Ear 重建 |
| `E:/moodify-security-fix` | `codex/remove-leaked-deepseek-key` | 安全补丁 |
| `E:/moodify-security-main` | `codex/security-hygiene-main` | 安全 |
| `E:/moodify-worktrees/moodify-3.0-external-audio` | `codex/moodify-3.0-external-audio` | Moodify 3.0 外部音频 |
| `E:/moodify-foundation-011`（011 创建） | `codex/mood-foundation-011` | 011 工作树（本任务） |
| `C:/Users/Administrator/.cursor/worktrees/moodify/*` | 多 feat/* / detached HEAD | 旧 Cursor worktrees（SEPARATE） |

011 不删除任何 worktree；不在 011 期间清理 detached HEAD。

## 4. Cherry-pick 允许性矩阵

| Cherry-pick 候选 | 来源分支 | 目标 | 条件 |
|---|---|---|---|
| Wallet Connect (`apps/web/lib/wallet.ts`) | `codex/mpf-002-contribution-core` | 015 | 复审后；不带未来官方 CA 假设 |
| viem / chain read abstractions | `codex/mpf-002-contribution-core` + `009` | 015 / 022 | 不带 BSC 主网 CA |
| Contribution workflow | `codex/mpf-002-contribution-core` | 016 | 复审后；不与 011 冲突 |
| Reputation model | `codex/mpf-002-contribution-core` | 016 / 020 | 复审后 |
| Transparency concepts | `codex/mpf-002-contribution-core` | 021 | 复审后 |
| Security / Threat model | `codex/mpf-002-contribution-core` | 022 | 复审后 |
| Drizzle migrations 0002 | `codex/mpf-002-contribution-core` | 016 / 017 | schema 复审 |

**禁止 cherry-pick：**

- 任何引入「未来官方 CA」「Buy MOOD」CTA 的提交
- 任何把 Genesis v1.0 Distributor 部署脚本带入 011 / 012 的提交
- 任何把 `/airdrop`、`/genesis`、`/token` UI 改为「可领取 / 可激活」状态的提交
- 任何把 pending reward 自动转为 Token 的代码路径

## 5. 与 011 任务的并行冲突检测

011 期间监控的潜在冲突：

| 风险类别 | 描述 | 011 处置 |
|---|---|---|
| Canon 冲突 | 多分支修改同一 Canon 文件 | 立即停止；HUMAN_DECISION_REQUIRED |
| 未知新 Token 地址 | 任何分支引入新 CA | 立即停止；HUMAN_DECISION_REQUIRED |
| production deployment | 任何分支触发链上部署 | 立即停止；HUMAN_DECISION_REQUIRED |
| 真实资金 | 任何分支修改 LP / treasury 配置 | 立即停止；HUMAN_DECISION_REQUIRED |
| 覆盖并行工作 | rebase / reset 他人分支 | 立即停止；HUMAN_DECISION_REQUIRED |

## 6. 011 之后更新机制

- 任何 011 之后新增的并行分支应在本表添加新行。
- `Action` 变更必须由人类授权。
- 本文件每次更新必须连同 commit 一起进入 git log。
