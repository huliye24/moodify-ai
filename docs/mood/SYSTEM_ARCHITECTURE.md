# SYSTEM_ARCHITECTURE — MOOD

**Version:** 1.0（MOOD FOUNDATION 011, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [CURRENT_CANON.md](CURRENT_CANON.md) · [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md) · [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md)

---

## 1. 总图

```text
+-----------------------------------------------------------------+
|                          MOOD  (WORLD)                           |
|                                                                  |
|   +---------------------+       +--------------------------+     |
|   |   MOOD PORTAL       |       |   MOOD PROTOCOL          |     |
|   |   (PORTAL)          |<----->|   (PROTOCOL)             |     |
|   |                     |  API  |                          |     |
|   |  - World home       |       |  - Moodify Protocol      |     |
|   |  - Library          |       |  - MPF-001..005          |     |
|   |  - Passport         |       |  - Contributions         |     |
|   |  - Governance UX    |       |  - Reputation            |     |
|   |  - Treasury UX      |       |  - Node Registry         |     |
|   +---------------------+       |  - Mainnet Facts         |     |
|                                 +--------------------------+     |
|                                                                  |
|   +----------------------------------------------------------+  |
|   |   MOOD TOKEN  (future Settlement/Incentive/Governance)    | |
|   |   STATUS: NOT ACTIVATED                                    | |
|   +----------------------------------------------------------+  |
+-----------------------------------------------------------------+
              |
              | Genesis Application (Moodify Music / Player)
              v
+-----------------------------------------------------------------+
|                       Moodify Music / Player                     |
|                    (first concrete user app)                     |
+-----------------------------------------------------------------+
```

## 2. 三层边界

### 2.1 WORLD（MOOD 总体）

```text
WORLD = MOOD PORTAL + MOOD PROTOCOL + (future) MOOD TOKEN
       + AI Agents + Developers / Creators / Nodes
```

WORLD 是开放的去中心化数字世界。任何个人 / 团队都可以加入 WORLD 成为居民（resident），WORLD 不持有居民的资产或身份密钥。

WORLD 不对外提供「购买 MOOD」CTA。Token 仅在 G0–G11 全部 PASS 后才被激活（见 [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)）。

### 2.2 PROTOCOL（Moodify Protocol）

```text
PROTOCOL = MPF-001 Mainnet Facts
         + MPF-002 Contribution Core
         + MPF-003 Reputation
         + MPF-004 Node Registry
         + MPF-005 Protocol API
```

PROTOCOL 是 WORLD 的协议层，提供：

- 公开的事实记录（mainnet facts）
- 贡献记录（contribution core）
- 协议身份与声誉（reputation）
- 节点目录（node registry）
- 统一 API（protocol API）

PROTOCOL 的存在 **不依赖** Token。Token 仅作为未来 Settlement / Incentive / Governance Layer。

PROTOCOL 的边界在 [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md) 中与 Moodify Music / Player 明确区分。

### 2.3 PORTAL（MOOD Portal）

```text
PORTAL = WORLD Home
       + Library（Whitepaper / Docs / Hash / Research）
       + MOOD Passport（Resident Identity）
       + Governance UX
       + Treasury UX
       + Discovery / Observatory
       + Agent / Node registry UI
```

PORTAL 是 WORLD 的入口与信息架构。PORTAL 是 **用户接触 MOOD 的主要面**，但 PORTAL 不是产品本身。

PORTAL 入口：`crestwavecoin.com`（状态：`PLANNED`，见 [PRODUCT_RELATIONSHIP.md](PRODUCT_RELATIONSHIP.md)）。

### 2.4 MOOD TOKEN（future economic layer）

```text
MOOD TOKEN = future Settlement Layer
           + future Incentive Layer
           + future Governance Layer
           + future LP / DEX surface
```

**当前状态：`NOT ACTIVATED`。**

Token 激活条件：G0–G11 全部 PASS（见 [TOKEN_LAUNCH_GATE.md](TOKEN_LAUNCH_GATE.md)）。

任何 Token 相关资产（Genesis / Distributor / Airdrop / Claim / DEX / LP）当前 **全部属于 FREEZE 集合**，详见 [ASSET_CLASSIFICATION.md](ASSET_CLASSIFICATION.md)。

## 3. on-chain / off-chain 边界

| 类别 | on-chain | off-chain |
|---|---|---|
| **Mainnet Facts（MPF-001）** | ✓（锁定后） | 写入前 |
| **Contribution 记录（MPF-002）** | 否（仅指纹 + 元数据可上链） | ✓（主权威） |
| **Reputation 快照（MPF-003）** | 否（passport reputation 当前不被强迫上链） | ✓（主权威） |
| **Node Registry（MPF-004）** | 否（公开事实 off-chain） | ✓（主权威） |
| **Protocol API（MPF-005）** | 否 | ✓ |
| **Token Transfer / Claim / Airdrop** | FREEZE | FREEZE |
| **Passport 身份证明** | 否（当前阶段） | ✓ |

Passport / Reputation **当前不被强迫上链**。上链决定属于未来 MIP（MOOD Improvement Proposal）范畴，由 MIP Governance（020）显式授权。

## 4. Passport / Reputation 当前不被强迫上链

011 明确：

- **Passport（Resident Identity）** 由 015 引入；当前阶段是 off-chain 概念。
- **Reputation Snapshot** 由 MPF-003 提供；上链是 **MIP 议题**，不是默认行为。
- **不创建「Reputation = On-chain Reputation」的隐含假设。** 历史文档若把 Reputation 默认为 on-chain，必须在引用时明确历史属性。

## 5. Genesis Application（Moodify Music / Player）

Moodify Music / Player 是 **Genesis Application**：第一个面向最终用户的应用。它运行在 WORLD 之上，但它不是 WORLD。

```text
WORLD  (MOOD)
   |
   |--- PROTOCOL (MPF-001..005)
   |
   |--- PORTAL  (crestwavecoin.com)
   |
   +--- Genesis Application
        |
        +-- Moodify Music / Player
              (PLAY-first user app)
```

Moodify Music / Player 的对外产品身份仍由 `docs/canon/CURRENT_CANON.md`（v1.1 Public Form Package 01）+ `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` 规定。011 不覆盖该 Canon。

## 6. AI Agents 在架构中的位置

```text
WORLD
  ├── PROTOCOL
  ├── PORTAL
  ├── Token（future）
  ├── Residents
  │     ├── Developers
  │     ├── Creators
  │     └── Nodes
  └── AI Agents
        ├── Protocol-native agents（MPF-002 contribution authors）
        ├── Operator agents（run on operator-owned infra）
        └── Resident agents（owned by a resident, declare via 018）
```

AI Agents 是 WORLD 的第一类居民。Agent 行为规则在 PROTOCOL 中定义（contribution 记录、capability 声明、health 报告），不属于产品 UX。

## 7. 现实边界

- **`crestwavecoin.com`** 当前为 `PLANNED`，未上线。011 不授权上线。
- **MPF-001..005** 在仓库内已实现，但云端生产流量与上线属于 023 Public Staging。
- **Token 部署 / Claim / Airdrop** 全部属于 FREEZE。
- **历史文档**（如 `codex/moodify-classic-reconstruction-001`）的 Genesis v1.0 实现进入 `FREEZE` 集合，不得自动成为 MOOD Token 的 Canon。
- **完整云端生产链** 属于 `docs/canon/CURRENT_ARCHITECTURE.md` 的 Moodify Ear 内部系统，不属于 MOOD 公开面。

## 8. 与 PUBLIC BRAND 的边界

- `crestwavecoin.com`（WORLD Home）尚未上线；上线后的公共语言约束在 `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`。
- `rongjingmusic.com`（Moodify Product Home）继续由 `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` 规定，与 MOOD WORLD Home **不混用品牌语言**。
- WORLD Home 与 Product Home 站点间互链但保持品牌分层。
