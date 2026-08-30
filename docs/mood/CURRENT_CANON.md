# CURRENT CANON — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md`（本文件）→ `docs/canon/*` → verified runtime evidence
**Supersedes:** any earlier document that frames MOOD as a single token-only product, or that treats `codex/mood-mainnet-integration-009` as canonical for the public MOOD surface.
**Related:** [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) · [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md) · [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md) · [SEPTEMBER_BUILD_ROADMAP.md](SEPTEMBER_BUILD_ROADMAP.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) · [DECISION_LOG.md](DECISION_LOG.md) · [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)

---

## 1. 单一宣言

```text
MOOD = WORLD + PROTOCOL + PORTAL
```

| 词 | 含义 | 性质 |
|---|---|---|
| **MOOD** | 开放的 Web3 数字世界 / 协议网络 | 总体身份 |
| **Moodify Protocol** | 声音、AI、贡献与协作协议 | 协议层 |
| **Moodify** | Genesis Application（首个面向用户的应用） | 应用层 |
| **MOOD Token** | 未来的 Settlement / Incentive / Governance Layer | 经济层（**未激活**） |
| **AI Agents** | 自动参与者、建设者与执行者 | 网络居民 |
| **Developers / Creators / Nodes** | 网络居民与建设者 | 网络居民 |

## 2. 三条不可交换原则

### 2.1 Token is not the product.
MOOD 不是「一个发了币的项目」。Token 是 WORLD 的未来经济层，不是产品本身。

### 2.2 Token is not the protocol.
Moodify Protocol 是 WORLD 的协议层。Protocol 的存在独立于 Token 的存在；没有 Token，Protocol 仍然成立。

### 2.3 Token is not the world.
MOOD 是 WORLD + PROTOCOL + PORTAL 三者的总和。Token 只是其中一个未来可选子集（见 [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)）。

## 3. 不变量（Canon 不变量）

1. **MOOD 不可被解释为单一 Token。**
2. **011 不授权任何未来新官方 CA。** 任何新增 CA 行为必须经过 [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md) 全部 PASS。
3. **旧 Token / 旧合约不能自动成为未来 MOOD Token 的 Canon。** 一切历史 Genesis / Distributor / Airdrop 资产进入 [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md) 的 `FREEZE` 集合，不得自动继承。
4. **`crestwavecoin.com` 是 MOOD 世界入口；Moodify 是 Genesis Application。** 两者关系见 [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md)。
5. **历史 / archive 文档允许保留，但必须明确历史属性。** 历史文档不能反向覆盖当前 Canon。
6. **Canon 变更必须可见。** 进入 [DECISION_LOG.md](DECISION_LOG.md) 与根 `docs/canon/CANON_CHANGELOG.md`。

## 3.1 MOOD Network Interface 公共语言与入口

`crestwavecoin.com` 必须呈现为一个统一结构、多个入口的 MOOD Network Interface：

```text
MOOD = WORLD + PROTOCOL + PORTAL
        + NETWORK / LIBRARY / MOODIFY GATE
```

当前公共主句：

> **MOOD is the world. Moodify is only the beginning.**

> **在这里，成为你自己。**

`Every voice deserves to be heard.` 不再用于 MOOD World 公共表面。Token 准备、发行状态与合约信息不得成为世界入口的主叙事；Token 继续作为未来经济层受 Launch Gate 约束。

## 4. 011 不做的事

011 是 **Canon Freeze & Branch Convergence**，不是产品扩张：

- � 不发新币
- ❌ 不部署合约
- ❌ 不写生产链
- ❌ 不触碰私钥 / 助记词
- ❌ 不移动真实资金
- ❌ 不创建 Flap 生产 Token
- ❌ 不添加真实 LP
- ❌ 不执行空投 / Claim / Genesis Distribution
- ❌ 不把 pending reward 自动转为 Token
- � 不 force push
- ❌ 不 reset --hard 覆盖并行工作
- ❌ 不删除未知分支
- ❌ 不整条 merge `codex/mood-mainnet-integration-009`
- ❌ 不进行与 011 无关的 Android / Electron / Player UI 开发
- ❌ 不偷跑实现 012–025 任一后续 package

011 的价值在于 **减少歧义**，不在于增加功能。

## 5. Canon Change Rule

任何改变以下内容的任务必须声明 `CANON_CHANGE = YES` 并说明 why / evidence / affected authority files / migration / rollback：

- 对外产品身份（MOOD / Moodify / Moodify Protocol 边界）
- 内部 / 外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority
- Token 是否进入激活路径

普通功能任务不得静默修改 Canon。

## 6. 与既有 Canon 的关系

- **`docs/canon/CURRENT_CANON.md`（v1.1 Public Form Package 01）**：处理 Moodify Music / Player 对外产品面与公共品牌。011 不覆盖该 Canon；MOOD 与 Moodify 是 **应用 � 总体世界** 关系。
- **`docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`**：公共品牌主题权威；MOOD 入口域名（如 `crestwavecoin.com`）的对外语言仍受其约束。
- **`docs/canon/AUTHORITY_ORDER.md`**：权威顺序继续生效；MOOD Canon 在第 3 级。
- **`docs/canon/CANON_CHANGELOG.md`**：011 的变更条目（MOOD 总体世界身份、Token Gate 冻结）必须进入此 changelog。

## 7. 与 012–025 的边界

| Package | 是否 011 提前实现 | 说明 |
|---|---|---|
| 012 Protocol Foundation Extraction | 否 | 012 决定如何从仓库提取 Wallet / Contribution / Transparency 底座 |
| 013 MOOD Portal Shell | 否 | 013 建立 PORTAL 信息架构 |
| 014 MOOD Library | 否 | 014 Whitepaper / Docs / Hash |
| 015 Wallet + MOOD Passport | 否 | 015 居民身份 |
| 016 Contribution Network v1 | 否 | 016 在 PROTOCOL 上跑 |
| 017 Network Observatory | 否 | 017 在 PROTOCOL 上跑 |
| 018 AI Agents Registry | 否 | 018 在 PROTOCOL 上跑 |
| 019 Nodes Registry | 否 | 019 在 PROTOCOL 上跑 |
| 020 MIP Governance | 否 | 020 在 PROTOCOL 上跑 |
| 021 Treasury & Transparency | 否 | 021 在 PROTOCOL 上跑 |
| 022 Security & Trust Layer | 否 | 022 跨层 |
| 023 Public Staging & E2E | 否 | 023 公网验证 |
| 024 Genesis Readiness Review | 否 | 024 Tokenomics / Flap / Legacy 复审 |
| 025 MOOD Token Activation | **必须被 011 GATE 拦截** | 025 必须等 G0–G11 全部 PASS |

011 不偷跑任何上述 package。

## 8. 入口

- [START_HERE_FOR_011.md](START_HERE_FOR_011.md)（本目录入口）
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)（边界）
- [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md)（MOOD ↔ Moodify ↔ crestwavecoin）
- [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md)（KEEP / KEEP BUT DARK / FREEZE / SEPARATE）
- [IN_FLIGHT_CHANGE_REGISTER.md](IN_FLIGHT_CHANGE_REGISTER.md)（并行分支）
- [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)（G0–G11）
- [SEPTEMBER_BUILD_ROADMAP.md](SEPTEMBER_BUILD_ROADMAP.md)（011–025）
- [DECISION_LOG.md](DECISION_LOG.md)（决策）
