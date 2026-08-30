# TASK — MOOD FOUNDATION 012

## Gate 0 — Confirm 011 Exists

开始前确认 011 已经执行并通过。

必须找到并读取：

```text
docs/mood/CURRENT_CANON.md
docs/mood/SYSTEM_ARCHITECTURE.md
docs/mood/PRODUCT_RELATIONSHIP.md
docs/mood/IN_FLIGHT_CHANGE_REGISTER.md
docs/mood/TOKEN_LAUNCH_GATE.md
docs/mood/ASSET_CLASSIFICATION.md
docs/mood/DECISION_LOG.md
```

如果缺少 011 输出：

**STOP. DO NOT IMPLEMENT 012.**

返回：

```text
BLOCKED_BY_MOOD_FOUNDATION_011
```

不要自行猜测 Canon。

---

## Phase A — Preflight

```bash
git fetch --all --prune
git status
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git branch -vv
git worktree list
```

若当前 workspace 有其他任务：

- 不清理
- 不 reset
- 建立独立 worktree
- 建立 `codex/mood-foundation-012` 或唯一后缀分支

012 必须基于 **被接受的 011 commit**，而不是直接基于旧 009。

---

## Phase B — Source Audit

审计 `codex/mood-mainnet-integration-009` 中与以下领域相关的代码：

```text
Wallet / EVM
Identity / Signature
Contribution
Reputation
Transparency
Treasury read models
Protocol configuration
Chain read abstractions
Security / admin auth
Database schema / migrations
Tests
```

重点检查但不限于：

```text
apps/web/app/token/WalletConnect.tsx
apps/web/lib/wallet.ts
apps/web/lib/mood-chain.ts
apps/web/lib/evm-address.ts
apps/web/lib/contribution-*
apps/web/app/contribute/**
apps/web/app/api/contribution/**
apps/web/app/transparency/**
apps/web/app/api/protocol/transparency/**
apps/web/db/schema.ts
apps/web/drizzle/**
apps/web/docs/protocol/CONTRIBUTION_NETWORK.md
apps/web/docs/protocol/TRANSPARENCY.md
apps/web/docs/security/**
apps/web/tests/*contribution*
apps/web/tests/*mood*
```

不要假定路径仍然完全一致。先搜索再决定。

---

## Phase C — Build Extraction Manifest

新增：

```text
docs/mood/extraction/
├── 012_SOURCE_AUDIT.md
├── 012_EXTRACTION_MANIFEST.md
├── 012_DEPENDENCY_MAP.md
├── 012_LEGACY_TOKEN_SEAMS.md
└── 012_FINAL_REPORT.md
```

### `012_EXTRACTION_MANIFEST.md`

对每个候选资产记录：

| Asset | Source Branch | Source Path | Classification | Action | Token Coupling | Tests |
|---|---|---|---|---|---|---|

Action 只能是：

- EXTRACT
- ADAPT
- LEAVE
- FREEZE
- REWRITE_MINIMAL
- HUMAN_DECISION_REQUIRED

---

## Phase D — Target Architecture

目标结构应尽量形成清晰边界，例如：

```text
apps/web/lib/mood/
├── identity/
├── wallet/
├── contribution/
├── reputation/
├── transparency/
├── chain/
└── launch-gate/
```

如果仓库已有更合适的模块边界：

**优先复用，不为目录美观做大迁移。**

012 的原则是：

> isolate semantics before reorganizing filesystem.

必须做到：

### 1. Wallet
钱包连接不依赖 MOOD Token 地址。

### 2. Identity
地址规范化、签名 nonce/message 等基础能力不能暗示持币才有身份。

### 3. Contribution
Task / Submission / Review 可以在没有 Token 的情况下完整工作。

### 4. Reputation
Reputation 保持 non-transferable / off-chain v1。

### 5. Rewards
允许保留 `pending` reward accounting，但必须与“已发行 Token”解耦。

推荐命名语义：

```text
reward_units
pending_reward_units
future_token_allocation_hint
```

如果已有 `pending_mood` 字段，除非迁移风险极低，不要求 012 强行改 DB；
可以通过 adapter / docs 明确它当前只是历史命名，不代表链上债权。

### 6. Transparency
Transparency 页面 / API 可以展示：

- contribution provenance
- system version
- public policy
- network facts

但不应必须依赖：

- future official CA
- DEX price
- live treasury assets
- token distribution

### 7. Chain
仅保留 read-only 通用链能力：

- chain config abstraction
- address validation
- RPC health
- generic balance / block reads when useful

任何 future MOOD Token-specific read 必须经过 launch gate。

---

## Phase E — Introduce Launch-Gate Boundary

新增一个单一权威的 runtime / build-time launch gate。

例如：

```ts
type MoodLaunchState =
  | "foundation"
  | "staging"
  | "token-ready"
  | "token-active";
```

默认必须是：

```text
foundation
```

并提供明确语义：

- `foundation`: 无新 Token Canon，无交易 CTA
- `staging`: 可测试非资金流程
- `token-ready`: 024 审计后等待人工激活
- `token-active`: 025 后才允许官方 CA / DEX / token UI 成为 Canon

不得通过前端 query string 或普通用户输入绕过。

---

## Phase F — Extract Contribution Foundation

优先保留现有已经成熟的流程：

```text
Task
  ↓
Submission
  ↓
Review
  ↓
Reputation
  ↓
Pending Reward Record
```

确保：

- active task catalog 可工作
- submit / resubmit 可工作
- review state machine 可工作
- reputation append-only 语义不破坏
- pending reward 不触发链上转账
- admin 边界仍然 fail-closed

不要在 012 做 DAO voting 或 Token gating。

---

## Phase G — Extract Wallet / Identity Foundation

目标是给 015 Passport 做底座。

必须支持或准备：

```text
Connect Wallet
↓
Normalize Address
↓
Request Nonce
↓
Sign Human-readable Message
↓
Verify Signature
↓
Create / Resolve Resident Identity
```

012 不要求完整 Passport UI。

如果现有 Genesis registration 已经包含 nonce/signature 机制：

- 可以抽取其通用部分
- 不能保留 “Genesis airdrop enrollment” 作为身份核心

---

## Phase H — Legacy Token Seam Audit

建立 `012_LEGACY_TOKEN_SEAMS.md`。

列出所有仍然耦合旧 Token 的地方：

```text
File
Symbol
Legacy assumption
Risk
Temporary handling
Removal target package
```

至少覆盖：

- hard-coded CA
- totalSupply
- DEX URL
- PancakeSwap copy
- “official token” 文案
- Genesis distribution
- Airdrop eligibility
- Treasury token balance
- automatic MOOD reward claim
- token-gated admin or identity

不要在 012 一次性删光历史资产。

目标是：

> known seams, isolated seams, dark seams.

---

## Phase I — Tests

必须有测试证明以下不变量：

### INV-012-01
没有配置新 MOOD Token 地址时，应用核心 foundation 可以 build。

### INV-012-02
Wallet connect 不依赖 token contract。

### INV-012-03
Contribution workflow 不依赖 token contract。

### INV-012-04
Reputation 不可转移。

### INV-012-05
Pending reward 不产生链上 side effect。

### INV-012-06
Foundation state 下，不出现 production Buy / Trade / Claim CTA。

### INV-012-07
Unknown launch state fail closed。

### INV-012-08
Legacy Token-specific adapter 不可自动升级为 canonical Token config。

---

## Phase J — Verification

运行最小必要集合：

```bash
git diff --check
```

以及相关：

```text
typecheck
lint
unit tests
contribution tests
wallet / identity tests
launch-gate tests
```

如果完整 build 太重：

写 `NOT_RUN`，给出精确命令。

---

## Phase K — Final Output

严格使用 `OUTPUT_TEMPLATE.md`。

最后给 013 明确 handoff：

```text
What is now stable enough for Portal Shell?
What routes/data contracts may 013 consume?
What remains dark/frozen?
What must 013 never surface?
```
