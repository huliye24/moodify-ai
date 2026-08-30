# ASSET_CLASSIFICATION — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) · [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)

---

## 1. 分类总览

仓库现有资产（含本地分支、`codex/mood-mainnet-integration-009`、`codex/moodify-classic-reconstruction-001`、`codex/mpf-002-contribution-core` 等）按下列四类处置：

| 类别 | 含义 | 011 期间的处置 |
|---|---|---|
| **KEEP** | 可复用，011 之后继续作为 PROTOCOL / PORTAL / Genesis Application 的一部分 | 保持并演进 |
| **KEEP BUT DARK** | 保留但在 Token 激活前不作为「已激活能力」展示 | 保留代码，UI/文档不外露 |
| **FREEZE** | Token Launch Gate 通过前禁止继续生产化 | 冻结，不增量 |
| **SEPARATE** | 不属于 MOOD 主线（如 Moodify Music / Player、Android、Electron、Player-only 等） | 不混入 011 |

## 2. KEEP（可复用资产）

### 2.1 PROTOCOL 层

| 资产 | 位置 / 引用 | 用途 |
|---|---|---|
| MPF-001 Mainnet Facts | `protocol/mainnet.json` + `protocol/mainnet.lock.json` + `protocol/mainnet.schema.json` | PROTOCOL 主权威 |
| MPF-002 Contribution Core | `protocol/contribution/`（已实现，参见 `EXECUTION_REPORT.md`） | 贡献记录 |
| MPF-003 Reputation | `protocol/reputation/`（已实现，参见 `EXECUTION_EVIDENCE.md`） | 协议身份与声誉 |
| MPF-004 Node Registry | `protocol/node-registry/`（已实现，参见 `EXECUTION_EVIDENCE.md`） | 节点目录 |
| MPF-005 Protocol API | `protocol/protocol-api/`（已实现，参见 `EXECUTION_EVIDENCE.md`） | 统一 API |

### 2.2 共享底座

| 资产 | 位置 / 引用 | 用途 |
|---|---|---|
| Wallet Connect | `apps/web/lib/wallet.ts` + viem 抽象 | 015 复用 |
| Signature / Identity primitives | EIP-712 helpers、signature utilities | 015 / 016 / 022 复用 |
| Contribution workflow | `apps/web/lib/contribution-service.ts` + `lib/contribution-config.ts` + `lib/contribution-export.ts` + `lib/admin-auth.ts` | 016 复用 |
| Reputation model | `apps/web/lib/reputation-*`（若存在） | 016 复用 |
| Transparency concepts | `apps/web/lib/transparency-*` + `apps/web/app/api/protocol/transparency/route.ts` + `apps/web/app/transparency/page.tsx` | 021 复用 |
| Security / Threat model | `apps/web/docs/security/*`（GENESIS_SECURITY_REVIEW / THREAT_MODEL / PRIVACY_REVIEW / INCIDENT_RESPONSE） | 022 复用 |
| Viem / chain read abstractions | `apps/web/lib/evm-address.ts` + viem wrapper | 015 / 022 复用 |
| Drizzle migrations | `apps/web/drizzle/0001_*` + `0002_contribution_network.sql` | 016 / 017 复用 |

### 2.3 文档与品牌

| 资产 | 位置 / 引用 | 用途 |
|---|---|---|
| Public Brand authority | `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` + `docs/brand/public/*` | WORLD Home / Product Home 公共语言 |
| 既有 Canon | `docs/canon/*`（v1.1 Public Form Package 01） | Moodify Music / Player 对外身份 |
| Repository Status | `docs/REPOSITORY_STATUS.md` | 状态入口 |

## 3. KEEP BUT DARK（保留但不发币前不外露）

以下资产 **保留代码 / 接口**，但在 Token Launch Gate（G0–G11）全部 PASS 前，**不作为「已激活能力」展示在 UI / 公共文档 / 营销内容中**。

### 3.1 Token-adjacent UI / routes（不外露）

| 资产 | 位置 / 引用 | 处置 |
|---|---|---|
| `/airdrop` page | `apps/web/app/airdrop/page.tsx` | 保留代码，UI 不外露为「可领取」状态；CTA 改为「Pending Token Launch Gate」 |
| `/airdrop` API | `apps/web/app/api/airdrop/eligibility/route.ts` | 保留代码，路由默认不暴露在公开文档 |
| `/token` page | `apps/web/app/token/page.tsx` + `WalletConnect.tsx` + `layout.tsx` | 保留代码，UI 不外露「Token 已激活」表述 |
| `/genesis` page | `apps/web/app/genesis/page.tsx` | 保留代码，UI 不外露「Genesis 已激活」表述 |
| `/genesis` API | `apps/web/app/api/genesis/{me,nonce,register}/route.ts` | 保留代码，路由默认不暴露在公开文档 |

### 3.2 Token-adjacent services（保留）

| 资产 | 位置 / 引用 | 处置 |
|---|---|---|
| Mood Token service | `apps/web/lib/mood-token.ts` | 保留，011 不删 |
| Mood Chain service | `apps/web/lib/mood-chain.ts` | 保留，011 不删 |
| Mood Treasury service | `apps/web/lib/mood-treasury.ts` | 保留，011 不删 |
| Genesis distribution | `apps/web/lib/genesis-distribution.ts` | 保留，011 不删 |
| Genesis service | `apps/web/lib/genesis-service.ts` | 保留，011 不删 |
| Genesis message | `apps/web/lib/genesis-message.ts` | 保留，011 不删 |
| Genesis config | `apps/web/lib/genesis-config.ts` | 保留，011 不删 |

### 3.3 Token-adjacent contracts（保留但不部署到生产）

| 资产 | 位置 / 引用 | 处置 |
|---|---|---|
| MoodGenesisDistributor | `apps/web/contracts/protocol/MoodGenesisDistributor.sol` | 保留代码；011 不授权部署到生产链 |
| 配套测试 | `apps/web/contracts/test/MoodGenesisDistributor.t.sol` + `Package004Compatibility.t.sol` + fixtures | 保留测试 |

### 3.4 Token-adjacent docs（保留但标记历史）

| 资产 | 位置 / 引用 | 处置 |
|---|---|---|
| GENESIS_AIRDROP / RUNBOOK / DISTRIBUTION / LAUNCH_RUNBOOK | `apps/web/docs/protocol/GENESIS_*.md` | 保留，但首页头部加历史标记 |
| GENESIS_V1_RC | `apps/web/docs/releases/GENESIS_V1_RC.md` | 保留，标记 `HISTORICAL / FREEZE` |
| TREASURY | `apps/web/docs/protocol/TREASURY.md` | 保留，标记 KEEP BUT DARK |
| GENESIS_SECURITY_* / PRIVACY_REVIEW / THREAT_MODEL / INCIDENT_RESPONSE | `apps/web/docs/security/*` | 保留，022 阶段复用 |

## 4. FREEZE（Token Launch Gate 前禁止继续生产化）

011 期间禁止以下行为增量生产化。任何新增尝试必须经 **HUMAN_DECISION_REQUIRED**。

### 4.1 部署 / 上线 / 链上动作

- ❌ new token deployment
- ❌ future official CA
- � DEX trade CTA
- ❌ Genesis distributor 部署
- ❌ Airdrop execution
- � Claim flow 上线
- ❌ automatic token distribution
- ❌ Flap production configuration

### 4.2 UI / 公共文档

- ❌ 在 WORLD Home / Product Home / Company Home 任何位置增加「Buy / Trade MOOD」CTA
- ❌ 在 Genesis Application UI 暴露「可领取空投」按钮
- ❌ 在 PROTOCOL docs 把 Token 默认设为贡献奖励目标
- ❌ 在公开 marketing 中声称 MOOD Token 已激活 / 已上线

### 4.3 数据 / 后端

- ❌ 把 pending reward 自动转为 Token
- ❌ 启动真实 LP / 流动性池
- ❌ 把测试网 CA 升级为「官方 CA」
- ❌ 把历史 Genesis v1.0 实现的部署参数作为未来 MOOD Token 的 Canon

## 5. SEPARATE（不混入 MOOD 主线）

以下资产属于 Moodify 产品线（PLAY-first Genesis Application）或其他独立项目，不混入 MOOD 主线：

### 5.1 Moodify Music / Player 专属

- Moodify Music Android（`apps/music-android`）
- Moodify Music Desktop / Electron
- Player-only features（PLAY UX、vinyl 视觉、playback state）
- moodify-core-package（`moodify-core-package/*`）中的 Ear / Reconstruction 内部系统
- Auditory Intelligence 内部代码（`src/moodify/auditory/*`、`identity_guard`、`era_diagnostic`、`reconstruction_objective`）
- v01 pipeline / data_factory / treatment_records / inspector / calibration
- 全部 `artifacts/mamse_*` 实验资产
- 全部 `artifacts/mfy_*`（除与 PROTOCOL 直接对应者外）
- 审查包 / 蒸馏包 / Cognitive Distillation（W01-P*、W01-*）

### 5.2 与 MOOD 无直接关系

- 重构 / 旧 production-case state machine（`orchestration/workflow_engine.py`）
- 旧 music-platform-listening-first / library-frontend / local-library-backend / player-integration / player-backend / brand-integration / 4pages-refactor / routing-and-stores / aip-protocol 等 feat/* 分支
- stabilization-sprint-001、milestone/moodify-daily-run-mrs-open-v031、huliye24-patch-1
- 旧 `mfy-mig-001-canonical-contracts`（已被 e24b29f5 合并入 main 的部分）
- 旧 `mhp-025-api-v01-alignment`

### 5.3 实验 / 早期

- `docs/experiments/*`
- `docs/strategy/*`
- `docs/ui-sketches/*`
- 旧历史 `PROJECT_SNAPSHOT_*` / `PHASE1_CONSTITUTION.md`（作为 LEGACY 处理）

## 6. 处置表（action matrix）

| 类别 | 代码保留 | 测试保留 | 文档保留 | UI 外露 | 增量生产 | 公共引用 |
|---|---|---|---|---|---|---|
| **KEEP** | ✓ | ✓ | ✓ | 必要时 | ✓ | ✓ |
| **KEEP BUT DARK** | ✓ | ✓ | ✓ | × | × | ×（直到 G0–G11 PASS） |
| **FREEZE** | ✓ | ✓ | ✓（标记历史） | × | × | × |
| **SEPARATE** | 不在 MOOD 工作集 | — | LEGACY | — | — | — |

## 7. 与 012–025 的衔接

- **012 Protocol Foundation Extraction** 应从 **KEEP + KEEP BUT DARK** 集合中提取 PROTOCOL 底座；不引入 FREEZE 资产。
- **013 MOOD Portal Shell** 应使用 **KEEP** 文档 / 品牌；不暴露 **KEEP BUT DARK** 资产。
- **014 MOOD Library** 应引用 **KEEP** docs；把 **KEEP BUT DARK / FREEZE** 标记为历史。
- **015–022** 应基于 **KEEP** 集合演进。
- **024 Genesis Readiness Review** 是 **KEEP BUT DARK + FREEZE** 集合的最终复审环节；之后才能进入 G11。
- **025 MOOD Token Activation** 是 G0–G11 全部 PASS 后的执行阶段，**不**在 011 提前实现。
